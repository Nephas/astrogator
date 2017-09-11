"""Author: Marco Fink"""
import pygame as pg
import numpy as np
import time as t


from Astro import Astro

class MinorBody:
    """Basic Planet class"""

    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        self.root = root
        self.name = name

        self.child = []
        self.mapvel = np.array(mapvel)
        self.mappos = np.array(mappos)      # absolute cartesian position now in AU
        self.mapacc = np.array([0,0])
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
        velInter = self.mapvel + dt/2*self.mapacc
        velComp = self.mapvel + dt*self.mapacc

        self.mappos += dt*velInter
        self.mapvel = velInter + dt/2*self.root.nbodyAcc(self.mappos)

        error = np.sum(np.abs(velComp-self.mapvel))/np.sum(np.abs(velComp))
        tol = 0.05

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(stepsize,0.9*stepsize*max(tol/error,0.3))


class Ship(MinorBody):
    def __init__(self, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        MinorBody.__init__(self, root, mappos, mapvel, name)

    def Draw(self, screen):
        image = pg.transform.rotozoom(self.image, 0, 0.1)
        screen.map['BODY'].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

        pos = screen.Map2Screen(self.mappos, self.root.time)
        arrow = self.mapvel*Astro.AU_kms
        pg.draw.lines(screen.map['TRAIL'], pg.Color("green"), False, [pos, pos+arrow])

        sign = np.sign(self.mapacc)
        arrow = sign * np.log(np.abs(self.mapacc)*1000 + np.array([1,1])) * 100
        pg.draw.lines(screen.map['TRAIL'], pg.Color("red"), False, [pos, pos+arrow])

#        acc = self.main.world.activesystem.Acc(self.Screen2Map(pos))
#        acc = 1000000 * np.log(acc + np.array([1, 1]))
#        endpos = self.mappos + self.mapacc
        #if self.Contains(endpos) and self.Contains(pos):
