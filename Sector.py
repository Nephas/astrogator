"""Author: Marco Fink"""

import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Screen import Screen
from System import System

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

    def __init__(self, main, size=[20, 20], density=0.5):
        self.main = main
        self.time = 0
        self.system = []
        self.activesystem = None
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
            system = System(self.main, mappos=pos)
            pack = system.Generate(rd.randint(0, 2**16), 0)
            self.system.append(pack)

            if i % 100 == 0:
                print("  " + str(i) + "/" + str(numStars))

        self.activesystem = rd.choice(self.system).Unpack()
        self.main.screen.refbody = self.activesystem

    def Draw(self, screen):
        if screen.mapscale < Screen.SYSTEMTHRESHOLD:
            for system in self.system:
                if Screen.Contains(screen.Map2Screen(system.mappos, self.time)):
                    image = pg.transform.rotozoom(
                        system.image, 0, - 5 * screen.starscale * (system.mag))
                    screen.map[Screen.BODY].blit(image, screen.Map2Screen(
                        system.mappos, self.time) - np.array(image.get_size()) * 0.5)
        else:
            self.activesystem.Draw(screen)

    def Move(self, dt):
        self.time += dt
        self.activesystem.Move(dt)

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
        if self.main.screen.mapscale < Screen.SYSTEMTHRESHOLD:
            dists = [np.linalg.norm((mappos - system.mappos))
                     for system in self.system]
            i = np.argmin(dists)
            return self.system[i]
        else:
            return self.activesystem.getClosest(mappos)

    def changeFocus(self, body):
        """To another system, unpacking it on the way, or to a body inside the activesystem"""
        if hasattr(body, 'root') and body.root is self.activesystem:
            self.main.screen.refbody = body
        elif body is not self.activesystem:
            self.activesystem = body.Unpack()
            self.main.screen.refbody = self.activesystem
