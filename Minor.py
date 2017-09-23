"""Author: Marco Fink"""
import pygame as pg
import numpy as np


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
        # absolute cartesian position now in AU
        self.mappos = np.array(mappos)
        self.mapacc = np.array([0., 0.])

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
        velInter = self.mapvel + dt / 2. * self.mapacc
        velComp = self.mapvel + dt * self.mapacc

        self.mappos += dt * velInter
        self.mapvel = velInter + dt / 2. * self.root.potential(self.mappos)

        error = np.sum(np.abs(velComp - self.mapvel)) / np.sum(np.abs(velComp))
        tol = 0.05

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(
            stepsize, 0.9 * stepsize * max(tol / error, 0.3))


class Ship(MinorBody):
    def __init__(self, world, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        MinorBody.__init__(self, root, mappos, mapvel, name)

        self.pointing = np.array([1., 0.])
        self.acc = np.array([0., 0.])
        self.thrust = 0.0

        self.world = world
        self.worldpos = np.array([0., 0.])

        self.trail = np.array([(0., 0., 0.) for i in range(1024)])
        self.trailpointer = 0

    def Draw(self, screen, sector=False):
        image = pg.transform.rotozoom(self.image, 0, 0.1)

        if screen.mapscale < Screen.SYSTEMTHRESHOLD:
            pos = screen.Map2Screen(self.worldpos, self.root.time)
        else:
            self.drawTrail(screen, pg.Color('darkblue'))
            pos = screen.Map2Screen(self.mappos, self.root.time)

        screen.map['BODY'].blit(image, pos - np.array(image.get_size()) * 0.5)

        arrow = (self.mapvel - screen.refbody.mapvel) * Astro.AU_kms
        pg.draw.lines(screen.map['TRAIL'], pg.Color(
            "green"), False, [pos, pos + arrow])

        arrow = Screen.Pol2Cart(self.pointing) * 20
        pg.draw.lines(screen.map['TRAIL'], pg.Color(
            "blue"), False, [pos, pos + arrow])

        sign = np.sign(self.mapacc)
        arrow = sign * np.log(np.abs(self.mapacc) *
                              1000 + np.array([1, 1])) * 100
        pg.draw.lines(screen.map['TRAIL'], pg.Color(
            "red"), False, [pos, pos + arrow])

    def drawTrail(self, screen, color=None):
        if color is None:
            color = self.color
        color.a = 128

        if self.trailpointer > 1:
            mappos = screen.Map2Screen(
                self.trail[0:self.trailpointer, 1:3], self.trail[0:self.trailpointer, 0])
            pg.draw.lines(screen.map['TRAIL'], color, False, mappos)

    def circularize(self, refbody):
        dist = np.linalg.norm(self.mappos - refbody.mappos)
        vorbit = Astro.vOrbit(dist, refbody.mass)

        self.mapvel = refbody.mapvel + vorbit * Screen.Pol2Cart(self.pointing)

    def changeSystem(self, newRoot):
        self.root.minor.remove(self)
        self.root = newRoot
        self.root.minor.append(self)
        self.world.activesystem = self.root
        if self.world.refsystem is newRoot:
            self.world.changeFocus(self.world.activesystem)

        self.mappos = self.worldpos - self.root.worldpos

        self.trail = np.array([(0., 0., 0.) for i in range(1024)])
        self.trailpointer = 0

    def checkSystem(self):
        dists = [np.linalg.norm((system.worldpos - self.worldpos))
                 for system in self.world.system]
        closest = self.world.system[np.argmin(dists)]
        if closest.name != self.root.name:
            self.changeSystem(closest.Unpack())

    def Move(self, dt=0):
        self.trail[self.trailpointer] = [self.root.time] + list(self.mappos)
        self.trailpointer = (self.trailpointer + 1) % len(self.trail)

        self.acc = self.thrust * Screen.Pol2Cart(self.pointing)

        # Leapfrog integration
        self.mapacc = self.root.potential(self.mappos)
        velInter = self.mapvel + dt / 2. * (self.mapacc + self.acc)
        velComp = self.mapvel + dt * (self.mapacc + self.acc)

        self.mappos += dt * velInter
        self.mapvel = velInter + dt / 2. * \
            (self.root.potential(self.mappos) + self.acc)

        self.worldpos = self.mappos + self.root.worldpos

        error = np.sum(np.abs(velComp - self.mapvel)) / np.sum(np.abs(velComp))
        tol = 0.01

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(
            stepsize, 0.9 * stepsize * max(tol / error, 0.3))

        self.checkSystem()
