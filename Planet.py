
import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Moon import Moon
from Screen import Screen

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Planet:
    """Basic Planet class"""

    PLANETIMAGE = pg.image.load("graphics/planet.png")

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        self.parent = parent
        self.root = root
        self.name = name

        self.child = []
        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = None                  # now in rad/day
        self.mappos = None                  # absolute cartesian position now in AU

        self.mass = 0         # in earth mass
        self.scorbit = [0, 0]  # Hills-Radius in AU
        self.radius = 0       # in earth radii
        self.torbit = 0

        self.image = None

    def Create(self):
        self.mass = min(300, 0.5 + np.random.exponential(self.cylpos[R]))
        self.radius = Astro.PlanetRadius(self.mass)

        # setup circular orbit
        self.torbit = 365 * np.sqrt(self.cylpos[R]**3 / self.parent.mass)
        self.cylvel = np.array([0, 2 * np.pi / self.torbit])

        self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R], self.mass * Astro.Me_Msol, self.parent.mass)
        self.scorbit[MIN] = 0

        # create moons
        i = 0
        n = 0
        while True:
            moonorbit = Astro.TitiusBode(i, 0.01)
            if moonorbit > self.scorbit[MAX]:
                break
            if moonorbit > self.scorbit[MIN]:
                self.child.append(Moon(self, self.root, [moonorbit, rd.random() * 2 * np.pi]))
                self.child[n].Create()
                n += 1
            i += 1

        self.image = Planet.PLANETIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("brown"))

    def Draw(self, screen):
        if not Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            return

        # planet hill sphere
        linecolor = pg.Color("brown")
        linecolor.a = 15
        pg.draw.circle(screen.map[Screen.GRAV], linecolor, screen.Map2Screen(
            self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
        linecolor.a = 255

        # planet trail
        linecolor = Screen.ColorBrightness(pg.Color("brown"), 0.8)
        length = min(self.root.main.screen.refbody.torbit / 4, self.torbit / 4)
        times = np.linspace(self.root.time - length, self.root.time, 20)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map[Screen.TRAIL], linecolor, False, mappos)

        # linecolor = pg.Color("darkgreen")
        # times = np.linspace(self.root.time + length, self.root.time, 20)
        # mappos = screen.Map2Screen(self.MapPos(times), times)
        # pg.draw.lines(screen.potential, linecolor, False, mappos)

        if screen.mapscale > Screen.PLANETTHRESHOLD:
            for moon in self.child:
                moon.Draw(screen)

        image = pg.transform.rotozoom(
            self.image, -self.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map[Screen.BODY].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

    def MapPos(self, time=0):
        """Get positions for a list of times: [t2] -> [x2,y2]"""
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

        for child in self.child:
            child.Move(dt)
