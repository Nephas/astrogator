
import numpy as np
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


class Wave:
    """Individual wave in a stellar wind"""

    def __init__(self, parent, root, cylpos=[0, 0]):
        self.parent = parent
        self.root = root

        self.tbirth = self.root.time
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylstart = np.array(cylpos)
        self.cylvel = np.array([0.1, 0])       # now in rad/day
        self.mappos = np.array([0, 0])                  # absolute cartesian position now in AU

        self.image = pg.Surface([1, 1], flags=pg.SRCALPHA)
        self.image.fill(self.parent.color)

    def Draw(self, screen):
        r = int(self.cylpos[R] * self.root.main.screen.mapscale + 1)
        color = Screen.ColorBrightness(self.parent.color, 0.1 + 0.5 * (1 - self.cylpos[R] / self.parent.scorbit[MAX]))
        pg.draw.circle(screen.map[Screen.TRAIL], color, screen.Map2Screen(
            self.parent.mappos, self.root.time).astype(int), int(r), 1)

    def MapPos(self, time=0):
        return Screen.Pol2Cart(self.cylpos) + self.parent.mappos

    def Move(self, dt):
        self.cylvel[R] = min(0.1, 1. / self.cylpos[R])
        self.cylpos = self.cylpos + dt * self.cylvel
        self.mappos = self.MapPos(self.root.time)

        if self.cylpos[R] > self.parent.scorbit[MAX]:
            self.parent.wind.remove(self)
