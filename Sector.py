"""Author: Marco Fink"""

import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Screen import Screen
from System import RootSystem
from Minor import Ship

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Sector:
    """Some hundred systems with a list of packaged system and one loaded player system"""

    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, main, size=[10, 10], density=0.5):
        self.main = main
        self.time = 0
        self.system = []
        self.activesystem = None
        self.viewsystem = None
        self.refsystem = None
        self.playership = None
        self.density = density      # in stars / pc^2
        self.size = size            # in pc

    def Generate(self):
        rd.seed()
        numStars = min(1000, int(self.size[X] * self.size[Y] * self.density))

        print("Generating Systems:")

        for i in range(numStars):
            pos = Astro.pc_AU * 0.5 * \
                np.array([np.random.normal() * self.size[X],
                          np.random.normal() * self.size[Y]])
            mass = min(100, 0.5 + np.random.exponential(2))
            system = RootSystem(self.main, mass=mass, worldpos=pos)
            pack = system.Generate(rd.randint(0, 2**16), 0)
            self.system.append(pack)

            if i % 100 == 0:
                print("  " + str(i) + "/" + str(numStars))

        self.system = sorted(list(set(self.system)), key=lambda sys: -sys.mag)

        self.refsystem = rd.choice(self.system)
        self.activesystem = self.refsystem.Unpack()
        self.viewsystem = self.activesystem

        ship = Ship(self, self.activesystem, [
                    0, 2.0], [-Astro.vOrbit(2.0, 1), 0])
        self.activesystem.minor.append(ship)

        self.main.screen.refbody = self.activesystem
        self.main.screen.refsystem = self.refsystem
        self.main.screen.playership = ship
        self.playership = ship

    def Draw(self, screen):
        if screen.mapscale < Screen.SYSTEMTHRESHOLD:
            for system in self.system:
                system.Draw(screen)
            self.playership.Draw(screen)
        else:
            #            for body in self.main.screen.refbody.getHierarchy():
            #                body.Draw(screen)
            self.viewsystem.Draw(screen)
            for body in self.viewsystem.minor:
                body.Draw(screen)
#        if self.viewsystem is self.activesystem:
#            self.playership.Draw(screen)
#            for body in self.viewsystem.minor:
#                body.Draw(screen)

    def potential(self, mappos):
        return np.array([0.0, 0.0])

    def Move(self, dt):
        self.time += dt
        if self.activesystem is not None:
            self.activesystem.Move(dt)
        if self.viewsystem is not None and self.viewsystem.name is not self.activesystem.name:
            self.viewsystem.Move(dt)
        for system in self.system:
            system.Move()

    def printTerm(self, indent=""):
        """Dummy"""
        print(indent + "Sector:")
        indent += "   "
        for system in self.system:
            print(indent + "Name: " + str(system.name))
            print(indent + "Mass: " + str(system.mass))
            print(indent + "Pos: " + str(system.mappos))

    def getClosest(self, mappos):
        """Return the closest system if in sector view, or the closest body when in system view"""
        if self.main.screen.mapscale < Screen.SYSTEMTHRESHOLD or self.viewsystem is None:
            dists = [np.linalg.norm((mappos - system.worldpos))
                     for system in self.system]
            i = np.argmin(dists)
            return self.system[i]
        else:
            return self.viewsystem.getClosest(mappos)

    def changeFocus(self, body):
        """To another system, unpacking it on the way, or to a body inside the activesystem"""
        if hasattr(body, 'root') and body.root is self.viewsystem:
            self.main.screen.refbody = body
        elif body.name != self.activesystem.name:
            self.refsystem = body
            self.viewsystem = body.Unpack()
            self.main.screen.refbody = self.viewsystem
        elif body.name == self.activesystem.name:
            self.refsystem = body
            self.viewsystem = self.activesystem
            self.main.screen.refbody = self.viewsystem

        self.main.screen.refsystem = self.refsystem
