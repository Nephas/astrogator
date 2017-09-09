"""Author: Marco Fink"""

import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Screen import Screen
from Structure import Ring

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Body:
    """Basic Planet class"""

    MOONIMAGE = pg.image.load("graphics/moon.png")
    STARIMAGE = pg.image.load("graphics/star.png")
    PLANETIMAGE = pg.image.load("graphics/planet.png")
    HOLEIMAGE = pg.image.load("graphics/blackhole.png")

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        self.parent = parent
        self.root = root
        self.name = name

        self.child = []
        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0, 0])      # now in rad/day
        self.mappos = np.array([0, 0])      # absolute cartesian position now in AU

        self.color = pg.Color("white")

    def MapPos(self, time=0):
        """Get positions for a list of times: [t2] -> [x2,y2]"""
        if type(time) == np.ndarray:
            t = np.ndarray((len(time), 2))
            cs = np.ndarray((len(time), 2))
            cv = np.ndarray((len(time), 2))

            t[:, R] = time
            t[:, PHI] = time
            cs[:, :] = self.cylstart[:]
            cv[:, :] = self.cylvel[:]

            return Screen.Pol2Cart(cs + cv * t) + self.parent.MapPos(time)
        else:
            return Screen.Pol2Cart(self.cylstart + time * self.cylvel) + self.parent.MapPos(time)

    def drawTrail(self, screen, orbfrac):
        self.color.a = 128
        length = min(self.root.main.screen.refbody.torbit * orbfrac, self.torbit * orbfrac)
        times = np.linspace(self.root.time - length, self.root.time, 100 * orbfrac)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map['TRAIL'], self.color, False, mappos)
        self.color.a = 255

    def getClosest(self, mappos):
        refbodies = [body.getClosest(mappos) for body in self.child] + self.child + [self]
        dists = [np.linalg.norm((mappos - body.mappos)) for body in refbodies]
        return refbodies[np.argmin(dists)]

    def getHierarchy(self):
        hierarchy = [self]
        body = self
        while body is not self.root:
            body = body.parent
            hierarchy.insert(0, body)
        return hierarchy

    def Move(self, dt):
        self.cylpos = self.cylpos + dt * self.cylvel
        self.mappos = self.MapPos(self.root.time)

        for child in self.child:
            child.Move(dt)


class Star(Body):
    """A Star..."""

    def __init__(self, parent, root, mass, cylpos=np.array([0, 0]), name="unknown"):
        Body.__init__(self, parent, root, cylpos, name)

        self.structure = None

        self.mass = mass
        self.scorbit = [0, 0]          # stable circular orbit ranges
        self.torbit = 1e+15
        self.luminosity = 0     # solar lum
        self.radius = 0         # solar radii
        self.temp = 0           # Kelvin

    def Create(self, full=True):
        if self.mass > 1.4 and rd.random() < 0.3:
            self.Collapse(full)
            return

        if self.cylpos[R] != 0:
            distance = self.parent.orbit[A] + self.parent.orbit[B]
            self.torbit = 365 * np.sqrt(distance**3 / self.parent.mass)  # orbital period in years from parent mass
            self.cylvel = np.array([0, 2 * np.pi / (self.torbit)])

        self.radius = Astro.MassRadius(self.mass)
        self.luminosity = Astro.MassLuminosity(self.mass)
        self.temp = Astro.StefanBoltzmann(self.luminosity, self.radius)
        (self.spectral, self.color) = Astro.SpectralClass(self.temp)

        if not full:
            return
        # load graphics
        self.image = Body.STARIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), self.color)

        self.CreatePlanets()

    def CreatePlanets(self, innerRadius=0.1):
        self.scorbit[MIN] = innerRadius
        if self.scorbit[MAX] == 0:
            if self.parent.binary:
                dist = sum(self.parent.orbit)
                self.scorbit[MAX] = Astro.HillSphere(dist, self.mass, self.parent.mass)
            else:
                self.scorbit[MAX] = Astro.HillSphere(0.003 * Astro.pc_AU, self.mass, 100.)

        i = 0
        n = 0
        while True:
            planetorbit = Astro.TitiusBode(i)
            if planetorbit > self.scorbit[MAX]:
                break
            if planetorbit > self.scorbit[MIN]:
                self.child.append(
                    Planet(self, self.root, [planetorbit, rd.random() * 2 * np.pi], self.name + chr(97 + n)))
                self.child[n].Create()
                n += 1
            i += 1

    def Collapse(self, full=True):
        hole = BlackHole(self.parent, self.root, self.mass, self.cylpos, self.name)
        hole.Create(full)
        for i, comp in enumerate(self.parent.comp):
            if comp is self:
                self.parent.comp[i] = hole

    def Draw(self, screen):
        # star hill sphere
        self.color.a = 8
        pg.draw.circle(screen.map['GRAV'], self.color, screen.Map2Screen(
            self.mappos, self.root.time), (int(self.scorbit[MAX] * screen.mapscale)))
        self.color.a = 255

        if screen.mapscale < Screen.PLANETTHRESHOLD:
            self.drawTrail(screen, 0.3)

        # star image
        if Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            image = pg.transform.rotozoom(self.image, 0, screen.starscale * self.radius)
            screen.map['BODY'].blit(image, screen.Map2Screen(
                self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

        for planet in self.child:
            if Screen.Contains(screen.Map2Screen(planet.mappos, self.root.time)):
                planet.Draw(screen)


class BlackHole(Star):
    """A Black Hole..."""

    def __init__(self, parent, root, mass, cylpos=[0, 0], name="unknown"):
        Star.__init__(self, parent, root, mass, cylpos, name)

    def Create(self, full=True):
        if self.cylpos[R] != 0:
            distance = self.parent.orbit[A] + self.parent.orbit[B]
            self.torbit = 365 * np.sqrt(distance**3 / self.parent.mass)  # orbital period in years from parent mass
            self.cylvel = np.array([0, 2 * np.pi / (self.torbit)])

        self.radius = self.mass
        self.color = pg.Color(50, 50, 50)

        if not full:
            return

        # load graphics
        self.image = Body.HOLEIMAGE.convert_alpha()

        self.CreatePlanets(10)

    def Draw(self, screen):
        # star hill sphere
        if screen.mapscale < Screen.PLANETTHRESHOLD:
            self.color.a = 32
            pg.draw.circle(screen.map['GRAV'], self.color, screen.Map2Screen(
                self.mappos, self.root.time), (int(self.scorbit[MAX] * screen.mapscale)))
            self.color.a = 255
            self.drawTrail(screen, 0.3)

        # star image
        if Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            image = pg.transform.rotozoom(self.image, 0, screen.starscale * 0.5 * self.radius)
            screen.map['BODY'].blit(image, screen.Map2Screen(
                self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

        for planet in self.child:
            planet.Draw(screen)


class Planet(Body):
    """Basic Planet class"""

    PLANETIMAGE = pg.image.load("graphics/planet.png")

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        Body.__init__(self, parent, root, cylpos, name)

        self.structure = None

        self.mass = 0         # in earth mass
        self.scorbit = [0, 0]  # Hills-Radius in AU
        self.radius = 0       # in earth radii
        self.torbit = 0
        self.structure = None
        self.image = None

    def Create(self):
        self.mass = min(300, 0.5 + np.random.exponential(self.cylpos[R]))
        self.radius = Astro.PlanetRadius(self.mass)

        # setup circular orbit
        self.torbit = 365 * np.sqrt(self.cylpos[R]**3 / self.parent.mass)
        self.cylvel = np.array([0, 2 * np.pi / self.torbit])

        self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R], self.mass * Astro.Me_Msol, self.parent.mass)
        self.scorbit[MIN] = 0

        self.color = pg.Color("brown")

        # create moons
        i = 0
        n = 0
        while True:
            moonorbit = Astro.TitiusBode(i, 0.1 * self.scorbit[MAX])
            if moonorbit > self.scorbit[MAX]:
                break
            if moonorbit > self.scorbit[MIN]:
                self.child.append(Moon(self, self.root, [moonorbit, rd.random() * 2 * np.pi]))
                self.child[n].Create()
                n += 1
            i += 1

        self.image = Body.PLANETIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("brown"))

    def Draw(self, screen):
        # planet hill sphere
        self.color.a = 15
        pg.draw.circle(screen.map['GRAV'], self.color, screen.Map2Screen(
            self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
        self.color.a = 255

        if screen.mapscale > Screen.PLANETTHRESHOLD:
            if self.structure is not None:
                self.structure.Draw(screen)

            for moon in self.child:
                if Screen.Contains(screen.Map2Screen(moon.mappos, self.root.time)):
                    moon.Draw(screen)

        self.drawTrail(screen, 0.25)

        image = pg.transform.rotozoom(
            self.image, -self.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map['BODY'].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)


class Moon(Body):
    """Basic Moon class"""

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        Body.__init__(self, parent, root, cylpos, name)

        self.mass = 0         # in earth mass
        self.radius = 0       # in earth radii
        self.torbit = 0
        self.image = None

    def Create(self):
        self.mass = np.random.uniform(0.01, 0.1) * self.parent.mass
        self.radius = Astro.PlanetRadius(self.mass)

        # setup circular orbit
        # orbital period in days from parent mass
        self.torbit = 365 * np.sqrt(self.cylpos[R]**3 / (Astro.Me_Msol * self.parent.mass))
        self.cylvel = np.array([0, 2 * np.pi / self.torbit])

        self.image = Body.MOONIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("darkgray"))

    def Draw(self, screen):

        self.drawTrail(screen, 0.1)

        image = pg.transform.rotozoom(
            self.image, -self.parent.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map['BODY'].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)
