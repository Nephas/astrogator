"""Author: Marco Fink"""

import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Particle import Particle
from Screen import Screen

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

    def drawTrail(self, screen, orbfrac):
        length = min(self.root.main.screen.refbody.torbit * orbfrac, self.torbit * orbfrac)
        times = np.linspace(self.root.time - length, self.root.time, 100 * orbfrac)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map[Screen.TRAIL], self.color, False, mappos)

    def getClosest(self, mappos):
        refbodies = [body.getClosest(mappos) for body in self.child] + self.child + [self]
        dists = [np.linalg.norm((mappos - body.mappos)) for body in refbodies]
        return refbodies[np.argmin(dists)]

    def Move(self, dt):
        self.cylpos = self.cylpos + dt * self.cylvel
        self.mappos = self.MapPos(self.root.time)

        for child in self.child:
            child.Move(dt)


class Star(Body):
    """A Star..."""

    def __init__(self, parent, root, mass, cylpos=np.array([0, 0]), name="unknown"):
        Body.__init__(self, parent, root, cylpos, name)

        self.child = []
        self.particle = []

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
        self.EmitParticle(10)

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

    def EmitParticle(self, n=10):
        for i in range(n):
            self.particle.append(Particle(self, self.root, [rd.random() * self.scorbit[MAX], 0]))

    def Collapse(self, full=True):
        hole = BlackHole(self.parent, self.root, self.mass, self.cylpos, self.name)
        hole.Create(full)
        for i, comp in enumerate(self.parent.comp):
            if comp is self:
                self.parent.comp[i] = hole

    def Draw(self, screen):
        # star hill sphere
        if screen.mapscale < Screen.PLANETTHRESHOLD:
            self.color.a = 15
            pg.draw.circle(screen.map[Screen.GRAV], self.color, screen.Map2Screen(
                self.mappos, self.root.time), (int(self.scorbit[MAX] * screen.mapscale)))
            self.color.a = 255
            self.drawTrail(screen, 0.3)

            for particle in self.particle:
                particle.Draw(screen)

        # star image
        if Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            image = pg.transform.rotozoom(self.image, 0, screen.starscale * self.radius)
            screen.map[Screen.BODY].blit(image, screen.Map2Screen(
                self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

        for planet in self.child:
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
            self.color.a = 15
            pg.draw.circle(screen.map[Screen.GRAV], self.color, screen.Map2Screen(
                self.mappos, self.root.time), (int(self.scorbit[MAX] * screen.mapscale)))
            self.color.a = 255
            self.drawTrail(screen, 0.3)

        # star image
        if Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            image = pg.transform.rotozoom(self.image, 0, screen.starscale * 0.5 * self.radius)
            screen.map[Screen.BODY].blit(image, screen.Map2Screen(
                self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

        for planet in self.child:
            planet.Draw(screen)


class Planet(Body):
    """Basic Planet class"""

    PLANETIMAGE = pg.image.load("graphics/planet.png")

    def __init__(self, parent, root, cylpos=[0, 0], name="unknown"):
        Body.__init__(self, parent, root, cylpos, name)

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

        self.image = Body.PLANETIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("brown"))

    def Draw(self, screen):
        if not Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            return

        # planet hill sphere
        self.color = pg.Color("brown")
        self.color.a = 15
        pg.draw.circle(screen.map[Screen.GRAV], self.color, screen.Map2Screen(
            self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
        self.color.a = 255
        self.drawTrail(screen, 0.25)

        if screen.mapscale > Screen.PLANETTHRESHOLD:
            for moon in self.child:
                moon.Draw(screen)

        image = pg.transform.rotozoom(
            self.image, -self.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map[Screen.BODY].blit(image, screen.Map2Screen(
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
        if not Screen.Contains(screen.Map2Screen(self.mappos, self.root.time)):
            return

        self.drawTrail(screen, 0.15)

        image = pg.transform.rotozoom(
            self.image, -self.parent.cylpos[PHI] / (2 * np.pi) * 360, screen.planetscale * self.radius)
        screen.map[Screen.BODY].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)
