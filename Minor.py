"""Author: Marco Fink"""
import pygame as pg
import numpy as np
import time as t

class MinorBody:
    """Basic Planet class"""

    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, root, mappos=[0, 0], mapvel=[0, 0], name="unknown"):
        self.root = root
        self.name = name

        self.child = []
        self.mapvel = np.array(mapvel)
        self.mappos = np.array(mappos)      # absolute cartesian position now in AU
        self.torbit = 1e+15

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
        accInter = self.root.Acc(self.mappos)
        velInter = self.mapvel + dt/2*accInter
        velComp = self.mapvel + dt*accInter

        self.mappos += dt*velInter
        self.mapvel = velInter + dt/2*self.root.Acc(self.mappos)

        error = np.sum(np.abs(velComp-self.mapvel))/np.sum(np.abs(velComp))
        tol = 0.05

        stepsize = self.root.main.stepsize
        self.root.main.stepsize = min(stepsize,0.9*stepsize*max(tol/error,0.3))
