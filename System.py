"""Author: Marco Fink"""

import random as rd

import numpy as np
import pygame as pg

from Astro import Astro
from Body import Planet, Star
from Screen import Screen

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class PackedSystem:
    """A compact system representation containing the star graphics and system seed"""

    def __init__(self, pack):
        self.main = pack.main
        self.seed = pack.seed
        self.name = pack.name
        self.mass = pack.mass
        self.mappos = pack.mappos
        self.binary = pack.binary
        self.color = pack.color
        self.image = pg.transform.scale(System.STARIMAGE.convert_alpha(), (24, 24))
        self.image = Screen.colorSurface(self.image, pack.color)
        self.luminosity = pack.luminosity
        self.mag = -2.5 * np.log10(pack.luminosity) - 25

    def Unpack(self):
        """Unpack the system, returning a full scale System() object"""
        rd.seed(self.seed)
        np.random.seed(self.seed)

        system = RootSystem(self.main, mappos=self.mappos)
        system.seed = self.seed
        system.mass = self.mass
        system.name = self.name
        system.binary = self.binary
        system.Create(full=True)
        return system

        # string to seed: int(''.join([str(ord(l)) for l in s]))%(2**32-1)


class PackedSystem:
    def __init__(self, pack):
        self.main = pack.main
        self.seed = pack.seed
        self.name = pack.name
        self.mass = pack.mass
        self.mappos = pack.mappos
        self.color = pack.color
        self.luminosity = pack.luminosity

    def getClosest(self, mappos):
#        dists = [np.linalg.norm((mappos - body.MapPos(self.time))) for body in self.body]
#       i = np.argmin(dists)
        return (0,self)

    def Unpack(self):
        sys = System(self.main, mappos = self.mappos)
        sys.UnpackSystem(self.seed, 0)
        return sys


class System:
    """A generic binary or singular system"""

    MAXSIZE = 100
    RECURSION_DEPTH = 2
    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, mass=0, name="unknown", cylpos=[0, 0], rank=0, binary=False):
        self.name = name
        self.root = None
        self.rank = rank
        self.binary = binary

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0, 0])       # now in rad/day
        self.mappos = np.array([0, 0])      # absolute cartesian position now in AU

        self.mass = mass             # total system mass
        self.luminosity = 0
        self.orbit = [0, 0]
        self.torbit = 1e+15
        self.scorbit = [0, 0]       # stable circular orbit ranges

        self.comp = []              # comp[A], comp[B]
        self.child = []            # common planets

        self.cmsImage = pg.Surface([10, 10], flags=pg.SRCALPHA)

    def CreateComps(self, massA, massB):
        phirand = rd.random() * 2 * np.pi
        if rd.random() < 0.5 or self.rank >= System.RECURSION_DEPTH - 1:
            self.comp.append(Star(self, self.root, massA, [self.orbit[A], phirand], self.name + " A"))
        else:
            self.comp.append(SubSystem(self, self.root, massA, self.name +
                                       " A", [self.orbit[A], phirand], self.rank + 1))
        if rd.random() < 0.5 or self.rank >= System.RECURSION_DEPTH - 1:
            self.comp.append(Star(self, self.root, massB, [self.orbit[B], phirand + np.pi], self.name + " B"))
        else:
            self.comp.append(SubSystem(self, self.root, massB, self.name + " B",
                                       [self.orbit[B], phirand + np.pi], self.rank + 1))

    def CreatePlanets(self):
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

    def getClosest(self, mappos):
        refbodies = [body.getClosest(mappos) for body in self.comp + self.child] + self.child + [self]
        dists = [np.linalg.norm((mappos - body.mappos)) for body in refbodies]
        return refbodies[np.argmin(dists)]

    def Draw(self, screen):
        # stability zone and CoM
        if self.binary and screen.mapscale < Screen.PLANETTHRESHOLD:
            self.color.a = 8
            pg.draw.circle(screen.map[Screen.GRAV], self.color, screen.Map2Screen(
                self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
            self.color.a = 0
            pg.draw.circle(screen.map[Screen.GRAV], self.color, screen.Map2Screen(
                self.mappos, self.root.time), int(self.scorbit[MIN] * screen.mapscale))
            self.color.a = 255

        for comp in self.comp:
            comp.Draw(screen)
        for planet in self.child:
            planet.Draw(screen)

        image = pg.transform.rotozoom(self.cmsImage, 0, 0.2)
        screen.map[Screen.BODY].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

    def Move(self, dt=0):
        self.cylpos = self.cylpos + dt * self.cylvel
        self.mappos = self.MapPos(self.root.time)

        for comp in self.comp:
            comp.Move(dt)
        for child in self.child:
            child.Move(dt)


class RootSystem(System):
    """The root class for a hierarchical multiple system"""

    def __init__(self, main, mass=0, name="unknown", mappos=[0, 0], binary=False):
        System.__init__(self, mass, name, cylpos=[0, 0], rank=0)
        self.main = main
        self.root = self
        self.time = main.world.time
        self.mappos = mappos

    def Generate(self, seed=0, time=0):
        rd.seed(seed)
        np.random.seed(seed)
        self.seed = seed

        self.mass = min(100, 0.5 + np.random.exponential(2))
        self.name = "HIP " + str(rd.randint(10000, 99999))
        if rd.random() < 0.5:
            self.binary = True
        self.Create(full=False)
        return PackedSystem(self)

    def Create(self, full=True):
        # Binary System
        if self.binary:
            massA = rd.uniform(0.5, 0.9) * self.mass
            massB = self.mass - massA

            self.orbit[B] = rd.uniform(0.2, 0.8) * self.MAXSIZE
            self.orbit[A] = self.orbit[B] * massB / massA

            self.CreateComps(massA, massB)

        # or single star
        elif not self.binary:
            self.comp.append(Star(self, self, self.mass, [0, 0], self.name))
            self.comp[A].scorbit[MAX] = System.MAXSIZE

        self.color = pg.Color("black")
        for comp in self.comp:
            comp.Create(full=full)
        for comp in self.comp:
            self.color = self.color + comp.color

        self.luminosity = sum([c.luminosity for c in self.comp])

        if not full:

            return
        # create graphis
        pg.draw.circle(self.cmsImage, self.color, [5, 5], 5)

        # Maximum System size criterion: should be stable against close flybys
        self.scorbit[MAX] = Astro.HillSphere(0.003 * Astro.pc_AU, self.mass, 100.)  # System.MAXSIZE

        # create planets
        if self.binary:
            self.scorbit[MIN] = self.orbit[B] + self.comp[B].scorbit[MAX]
            self.CreatePlanets()

    def MapPos(self, time=0):
        if type(time) == np.ndarray:
            pos = np.ndarray((len(time), 2))
            pos[:, :] = self.mappos[:]
            return pos
        else:
            return self.mappos

    def Move(self, dt=0):
        self.time += dt

        for comp in self.comp:
            comp.Move(dt)
        for planet in self.child:
            planet.Move(dt)


class SubSystem(System):
    """All other binaries in a hierarchical multiple system"""

    def __init__(self, parent, root, mass=0, name="unknown", cylpos=[0, 0], rank=0):
        System.__init__(self, mass, name, cylpos, rank, binary=True)
        self.root = root
        self.parent = parent

    def Create(self, full=True):
        massA = rd.uniform(0.5, 0.9) * self.mass
        massB = self.mass - massA

        self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R], self.mass, self.parent.mass)
        self.orbit[B] = rd.uniform(0.2, 0.8) * self.scorbit[MAX]
        self.orbit[A] = self.orbit[B] * massB / massA

        distance = sum(self.parent.orbit)
        self.torbit = 365 * np.sqrt(distance**3 / self.parent.mass)  # orbital period in years from parent mass
        self.cylvel = np.array([0, 2 * np.pi / (self.torbit)])

        self.CreateComps(massA, massB)

        self.color = pg.Color("black")
        for comp in self.comp:
            comp.Create(full=full)
        for comp in self.comp:
            self.color = self.color + comp.color

        self.luminosity = sum([c.luminosity for c in self.comp])

        if not full:
            return
        # create graphis
        pg.draw.circle(self.cmsImage, self.color, [5, 5], 5)

        # setup zones of planetary stability
        dist = sum(self.parent.orbit)
        self.scorbit[MAX] = Astro.HillSphere(dist, self.mass, self.parent.mass)

        # create planets
        if self.binary:
            self.scorbit[MIN] = self.orbit[B] + self.comp[B].scorbit[MAX]
            self.CreatePlanets()

    def MapPos(self, time=0):
        """Get positions for a list of times: [t1] -> [x1,y1]"""
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
