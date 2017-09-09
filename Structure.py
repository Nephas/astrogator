"""Author: Marco Fink"""


import pygame as pg

from Screen import Screen

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Structure:
    """Base class for system spanning extended structures"""
    def __init__(self, parent, root, scorbit=[0, 0], color=pg.Color("white")):
        self.parent = parent
        self.root = root

        self.color = color
        self.mappos = self.parent.mappos
        self.scorbit = scorbit


# class Wind(Structure):


class Ring(Structure):
    """A planetary ring"""

    def __init__(self, parent, root, scorbit=[0, 0]):
        Structure.__init__(self, parent, root, scorbit=scorbit)

        self.orbits = []

    def Create(self):
        self.scorbit[MIN] = 0.5 * self.parent.scorbit[MAX]
        self.scorbit[MAX] = 0.75 * self.parent.scorbit[MAX]
        self.color = self.parent.color

        # create moons
        ringorbit = 0.1 * self.scorbit[MAX]
        while True:
            if ringorbit > 0.5 * self.scorbit[MAX]:
                break
            self.orbits.append([ringorbit, 0.1 * ringorbit])
            ringorbit *= 1.2

    def Draw(self, screen):
        for orbit in self.orbits:
            pg.draw.circle(screen.map['TRAIL'], self.color, screen.Map2Screen(
                self.parent.mappos, self.root.time), int(orbit[0] * screen.mapscale), int(orbit[1] * screen.mapscale))


# class Disk(Structure):
