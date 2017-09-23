"""Author: Marco Fink"""
import pygame as pg
import numpy as np
import time as t


from Astro import Astro
from Screen import Screen


class MinorBody:
    """Basic Planet class"""

    STARIMAGE = pg.image.load("graphics/star.png")
    SPARKIMAGE = pg.image.load("graphics/spark.png")

    def __init__(self, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        self.root = root
        self.name = name

        self.child = []
        self.mapvel = np.array(mapvel)
        self.mappos = np.array(mappos)      # absolute cartesian position now in AU
        self.mapacc = np.array([0.,0.])

        self.torbit = 1e+15
        self.mass = 0

        self.color = pg.Color("white")
        self.image = MinorBody.STARIMAGE

    def Draw(self, screen):
        image = pg.transform.rotozoom(self.image, 0, 0.1)
        screen.map['BODY'].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

    def getHierarchy(self):
        hierarchy = [self, self.root]
        return hierarchy

    def MapPos(self, time=0):
        if type(time) == np.ndarray:
            pos = np.ndarray((len(time), 2))
            pos[:, :] = self.mappos[:]
            return pos
        else:
            return self.mappos

    def Move(self, dt=0):
        # Leapfrog integration
        self.mapacc = self.root.nbodyAcc(self.mappos)
        velInter = self.mapvel + dt/2.*self.mapacc
        velComp = self.mapvel + dt*self.mapacc

        self.mappos += dt*velInter
        self.mapvel = velInter + dt/2.*self.root.potential(self.mappos)

        error = np.sum(np.abs(velComp-self.mapvel))/np.sum(np.abs(velComp))
        tol = 0.05

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(stepsize,0.9*stepsize*max(tol/error,0.3))


class Ship(MinorBody):
    def __init__(self, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        MinorBody.__init__(self, root, mappos, mapvel, name)

        self.pointing = np.array([1.,0.])
        self.acc = np.array([0.,0.])
        self.thrust = 0.0

        self.trail = np.array([(0.,0.,0.) for i in range(1024)])
        self.trailpointer = 0

    def Draw(self, screen, sector=False):
        image = pg.transform.rotozoom(self.image, 0, 0.1)

        if not sector:
            self.drawTrail(screen, pg.Color('darkblue'))
            pos = screen.Map2Screen(self.mappos, self.root.time)
        elif sector and not self.root is self.root.main.world:
            pos = screen.Map2Screen(self.mappos + screen.refsystem.mappos, self.root.time)
        else:
            pos = screen.Map2Screen(self.mappos, self.root.time)

        screen.map['BODY'].blit(image, pos - np.array(image.get_size()) * 0.5)

        arrow = (self.mapvel-screen.refbody.mapvel)*Astro.AU_kms
        pg.draw.lines(screen.map['TRAIL'], pg.Color("green"), False, [pos, pos+arrow])

        arrow = Screen.Pol2Cart(self.pointing)*20
        pg.draw.lines(screen.map['TRAIL'], pg.Color("blue"), False, [pos, pos+arrow])

        sign = np.sign(self.mapacc)
        arrow = sign * np.log(np.abs(self.mapacc)*1000 + np.array([1,1])) * 100
        pg.draw.lines(screen.map['TRAIL'], pg.Color("red"), False, [pos, pos+arrow])

    def drawTrail(self, screen, color=None):
        if color is None:
            color = self.color
        color.a = 128

        if self.trailpointer > 1:
            mappos = screen.Map2Screen(self.trail[0:self.trailpointer,1:3], self.trail[0:self.trailpointer,0])
            pg.draw.lines(screen.map['TRAIL'], color, False, mappos)

    def circularize(self,refbody):
        dist = np.linalg.norm(self.mappos - refbody.mappos)
        vorbit = Astro.vOrbit(dist, refbody.mass)

        self.mapvel = refbody.mapvel + vorbit*Screen.Pol2Cart(self.pointing)

    def changeSystem(self, root):
        self.root = root

    def Move(self, dt=0):
        self.trail[self.trailpointer] = [self.root.time] + list(self.mappos)
        self.trailpointer = (self.trailpointer + 1) % len(self.trail)

        self.acc = self.thrust*Screen.Pol2Cart(self.pointing)

        # Leapfrog integration
        self.mapacc = self.root.potential(self.mappos)
        velInter = self.mapvel + dt/2.*(self.mapacc + self.acc)
        velComp = self.mapvel + dt*(self.mapacc + self.acc)

        self.mappos += dt*velInter
        self.mapvel = velInter + dt/2.*(self.root.potential(self.mappos) + self.acc)

        error = np.sum(np.abs(velComp-self.mapvel))/np.sum(np.abs(velComp))
        tol = 0.01

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(stepsize,0.9*stepsize*max(tol/error,0.3))

        if self.root is not self.root.main.world and np.linalg.norm(self.mappos) > 100:
            self.mappos = self.root.pack.mappos + self.mappos
            self.root = self.root.main.world
