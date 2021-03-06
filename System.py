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

    def __init__(self, pack, seed):
        self.seed = seed

        self.worldpos = pack.worldpos
        self.mapstart = pack.worldpos
        self.mapvel = 0. * np.array([np.random.normal(), np.random.normal()])

        self.main = pack.main
        self.name = pack.name
        self.mass = pack.mass
        self.binary = pack.binary
        self.color = pack.color
        self.image = pg.transform.scale(
            System.STARIMAGE.convert_alpha(), (32, 32))
        self.image = Screen.colorSurface(self.image, pack.color)
        self.luminosity = pack.luminosity
        self.mag = -2.5 * np.log10(max(0.01, pack.luminosity)) - 25

    def Unpack(self):
        """Unpack the system, returning a full scale System() object"""
        system = RootSystem(self.main, mass=self.mass, worldpos=self.worldpos)
        rd.seed(self.seed)
        np.random.seed(self.seed)

        system.Create(full=True)
        return system

        # string to seed: int(''.join([str(ord(l)) for l in s]))%(2**32-1)

    def MapPos(self, time=0):
        """Get positions for a list of times: [t1] -> [x1,y1]"""
        if type(time) == np.ndarray:
            t = np.ndarray((len(time), 2))
            ms = np.ndarray((len(time), 2))
            mv = np.ndarray((len(time), 2))

            t[:, X] = time
            t[:, Y] = time
            ms[:, :] = self.mapstart[:]
            mv[:, :] = self.mapvel[:]

            return ms + mv * t
        else:
            return self.mapstart + time * self.mapvel

    def drawTrail(self, screen):
        length = 36500
        self.color.a = 32
        times = np.linspace(self.main.world.time - length,
                            self.main.world.time, 5)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map['TRAIL'], self.color, False, mappos)
        self.color.a = 255

    def Draw(self, screen):
        if Screen.Contains(screen.Map2Screen(self.worldpos, self.main.world.time)):
            image = pg.transform.rotozoom(
                self.image, 0, - 10 * screen.starscale * self.mag)
            screen.map['BODY'].blit(image, screen.Map2Screen(
                self.worldpos, self.main.world.time) - np.array(image.get_size()) * 0.5)
            self.drawTrail(screen)

    def Move(self, dt=0):
        self.worldpos = self.MapPos(self.main.world.time)


class System:
    """A generic binary or singular system"""

    MAXSIZE = 100
    RECURSION_DEPTH = 2
    STARIMAGE = pg.image.load("graphics/airy.png")

    def __init__(self, mass=0, name="unknown", cylpos=[0, 0], rank=0, binary=False):
        self.name = name
        self.root = None
        self.rank = rank
        self.binary = binary

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0, 0])       # now in rad/day
        # absolute cartesian position now in AU
        self.mappos = np.array([0, 0])

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
            self.comp.append(Star(self, self.root, massA, [
                             self.orbit[A], phirand], self.name + " A"))
        else:
            self.comp.append(SubSystem(self, self.root, massA, self.name +
                                       " A", [self.orbit[A], phirand], self.rank + 1))
        if rd.random() < 0.5 or self.rank >= System.RECURSION_DEPTH - 1:
            self.comp.append(Star(self, self.root, massB, [
                             self.orbit[B], phirand + np.pi], self.name + " B"))
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

    def getHierarchy(self):
        hierarchy = [self]
        body = self
        while body is not self.root:
            body = body.parent
            hierarchy.insert(0, body)
        return hierarchy

    def getClosest(self, mappos):
        refbodies = [body.getClosest(
            mappos) for body in self.comp + self.child] + self.child + [self]
        dists = [np.linalg.norm((mappos - body.mappos)) for body in refbodies]
        return refbodies[np.argmin(dists)]

    def getMajorBodies(self):
        bodies = []
        for comp in self.comp:
            bodies += comp.getMajorBodies()
        return bodies + self.child

    def Draw(self, screen):
        # stability zone and CoM
        if self.binary and screen.mapscale < Screen.PLANETTHRESHOLD:
            self.color.a = 8
            pg.draw.circle(screen.map['GRAV'], self.color, screen.Map2Screen(
                self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
            self.color.a = 0
            pg.draw.circle(screen.map['GRAV'], self.color, screen.Map2Screen(
                self.mappos, self.root.time), int(self.scorbit[MIN] * screen.mapscale))
            self.color.a = 255

        for comp in self.comp:
            comp.Draw(screen)
        for planet in self.child:
            if Screen.Contains(screen.Map2Screen(planet.mappos, self.root.time)):
                planet.Draw(screen)

        image = pg.transform.rotozoom(self.cmsImage, 0, 0.2)
        screen.map['BODY'].blit(image, screen.Map2Screen(
            self.mappos, self.root.time) - np.array(image.get_size()) * 0.5)

    def Move(self, dt=0):
        oldpos = self.mappos
        self.mappos = self.MapPos(self.root.time)
        self.mapvel = (self.mappos - oldpos) / dt

        for comp in self.comp:
            comp.Move(dt)
        for child in self.child:
            child.Move(dt)


class RootSystem(System):
    """The root class for a hierarchical multiple system"""

    def __init__(self, main, mass=0, name="unknown", worldpos=[0, 0], binary=False):
        System.__init__(self, mass, name, cylpos=[0, 0], rank=0)
        self.main = main
        self.root = self
        self.time = main.world.time
        self.worldpos = np.array(worldpos)

        self.mappos = np.array([0., 0.])
        self.mapvel = np.array([0., 0.])

        self.major = []  # a list of major bodies and their solar masses
        self.minor = []  # a list of minor bodies in the n-body potential

    def Generate(self, seed=0, time=0):
        rd.seed(seed)
        np.random.seed(seed)

        self.Create(full=False)
        return PackedSystem(self, seed)

    def Create(self, full=True):
        self.name = "HIP " + str(rd.randint(10000, 99999))
        if rd.random() < 0.5:
            self.binary = True

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

        # create planets
        if self.binary:
            self.scorbit[MIN] = self.orbit[B] + self.comp[B].scorbit[MAX]
            self.CreatePlanets()

        self.major = map(lambda b: (b, b.mass), self.getMajorBodies())

    def getClosest(self, mappos):
        refbodies = [body.getClosest(
            mappos) for body in self.comp + self.child] + self.child + self.minor + [self]
        dists = [np.linalg.norm((mappos - body.mappos)) for body in refbodies]
        return refbodies[np.argmin(dists)]

    def MapPos(self, time=0):
        if type(time) == np.ndarray:
            pos = np.ndarray((len(time), 2))
            pos[:, :] = self.mappos[:]
            return pos
        else:
            return self.mappos

    def potential(self, mappos):
        mass = np.array(map(lambda mb: mb[1], self.major))

        pos = np.ndarray((len(self.major), 2))
        pos[:, :] = mappos[:]

        bodypos = np.ndarray((len(self.major), 2))
        bodypos[:, :] = map(lambda mb: mb[0].mappos, self.major)

        diff = pos - bodypos
        g = np.power(np.linalg.norm(diff, axis=1), -3) * mass
        acc = - Astro.G * np.sum((diff.transpose() * g), axis=1)
        return acc

    def Move(self, dt=0):
        self.time += dt

        for comp in self.comp:
            comp.Move(dt)
        for planet in self.child:
            planet.Move(dt)
        for body in self.minor:
            body.Move(dt)


class SubSystem(System):
    """All other binaries in a hierarchical multiple system"""

    def __init__(self, parent, root, mass=0, name="unknown", cylpos=[0, 0], rank=0):
        System.__init__(self, mass, name, cylpos, rank, binary=True)
        self.root = root
        self.parent = parent

    def Create(self, full=True):
        massA = rd.uniform(0.5, 0.9) * self.mass
        massB = self.mass - massA

        self.scorbit[MAX] = Astro.HillSphere(
            self.cylpos[R], self.mass, self.parent.mass)
        self.orbit[B] = rd.uniform(0.2, 0.8) * self.scorbit[MAX]
        self.orbit[A] = self.orbit[B] * massB / massA

        distance = sum(self.parent.orbit)
        # orbital period in years from parent mass
        self.torbit = 365 * np.sqrt(distance**3 / self.parent.mass)
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
