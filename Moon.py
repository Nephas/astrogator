"""Author: Marco Fink"""

import numpy as np
import pygame as pg

from Astro import Astro
from Screen import Screen

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Moon:
    """Basic Moon class"""
    MOONIMAGE = pg.image.load("graphics/moon.png")

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        self.parent = parent
        self.root = root
        self.name = name

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = None                  # now in rad/day
        self.mappos = None                  # absolute cartesian position now in AU

        self.mass = 0         # in earth mass
        self.radius = 0       # in earth radii
        self.torbit = 0

        self.image = None

    def Create(self):
        self.mass = np.random.uniform() / 10

        # setup circular orbit
        # orbital period in days from parent mass
        self.torbit = 365 * np.sqrt(self.cylpos[R]**3 / (Astro.Me_Msol * self.parent.mass))
        self.cylvel = np.array([0, 2 * np.pi / self.torbit])

        self.image = Moon.MOONIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("darkgray"))

    def Draw(self, screen):
        if not Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            return

        linecolor = pg.Color("darkgray")
        length = min(self.root.main.screen.refbody.torbit / 6, self.torbit / 6)
        times = np.linspace(self.root.time - length, self.root.time, 10)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map[Screen.TRAIL], linecolor, False, mappos)

        image = pg.transform.rotozoom(
            self.image, -self.parent.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map[Screen.BODY].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

    def MapPos(self, time=0):  # time in days
        # Get positions for a list of times:
        # [t1]    [x1,y1]
        # [t2] -> [x2,y2]
        # [...]   [...]
        if type(time) == list:
            return [Screen.Pol2Cart(self.cylstart + t * self.cylvel) + self.parent.MapPos(t) for t in time]
        elif type(time) == np.ndarray:
            t = np.ndarray((len(time), 2))
            t[:, R] = time
            t[:, PHI] = time

            cs = np.ndarray((len(time), 2))
            cs[:, :] = self.cylstart[:]

            cv = np.ndarray((len(time), 2))
            cv[:, :] = self.cylvel[:]

            return Screen.Pol2Cart(cs + cv * t) + self.parent.MapPos(time)
        else:
            return Screen.Pol2Cart(self.cylstart + time * self.cylvel) + self.parent.MapPos(time)

    def Move(self, dt):
        self.cylpos = self.cylpos + dt * self.cylvel
        self.mappos = self.MapPos(self.root.time)
