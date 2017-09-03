from globals import *
from Star import Star
from Planet import Planet
from Ship import Ship
from Screen import Screen
from Astro import Astro

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
    MAXSIZE = 100
    RECURSION_DEPTH = 2
    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, main, parent = None, mass = 0, cylpos = [0,0], name = "", binary = True, rank = 0, mappos = [0,0]):
        self.main = main
        self.parent = parent
        self.name = name
        self.rank = rank
        self.binary = binary
        if self.parent is None:
            self.root = self
        else:
            self.root = self.parent.root

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0,0])       # now in rad/day
        self.mappos = np.array(mappos)      # absolute cartesian position now in AU

        self.mass = mass             # total system mass
        self.luminosity = 0
        self.body = []
        self.comp = []              # comp[A], comp[B]
        self.planet = []            # common planets
        self.ship = []
        # 0,0,0 in case of single, r1,r2,angle in case of double
        self.orbit = [0, 0]
        self.torbit = 1e+15
        self.scorbit = [0, 0]       # stable circular orbit ranges
        self.cmsImage = pg.Surface([10,10], flags = pg.SRCALPHA)
        self.starImage = System.STARIMAGE.convert_alpha()
        self.color = pg.Color("white")

    def UnpackSystem(self, seed = 0, time = 0):
        rd.seed(seed)
        np.random.seed(seed)
        self.time = time
        self.seed = seed

        self.mass = min(100,0.5 + np.random.exponential(2))
        self.name = "HIP " + str(rd.randint(10000,99999))
        self.binary = rd.choice([True,False])
        self.Create()
        self.Move()

        return PackedSystem(self)

    def Create(self):
        # Binary System
        if self.binary:
            massA = rd.uniform(0.5,0.9) * self.mass
            massB = self.mass - massA

            if self.rank == 0:
                self.orbit[B] = rd.uniform(0.2,0.8)*self.MAXSIZE
            else:
                self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass,self.parent.mass)
                self.orbit[B] = rd.uniform(0.2,0.8)*self.scorbit[MAX]
            self.orbit[A] = self.orbit[B] * massB / massA

            if self.cylpos[R] != 0:
                distance = self.parent.orbit[A] + self.parent.orbit[B]
                self.torbit = 365*np.sqrt(distance**3/self.parent.mass) # orbital period in years from parent mass
                self.cylvel = np.array([0,2*np.pi/(self.torbit)])

            if rd.random() < 0.5 or self.rank >= System.RECURSION_DEPTH - 1:
                self.comp.append(Star(self, self.root, massA, [self.orbit[A], 0], self.name + " A"))
            else:
                self.comp.append(System(self.main, self, massA, [self.orbit[A], 0], self.name + " A", True, self.rank+1))
            if rd.random() < 0.5 or self.rank >= System.RECURSION_DEPTH - 1:
                self.comp.append(Star(self, self.root, massB, [self.orbit[B], np.pi], self.name + " B"))
            else:
                self.comp.append(System(self.main, self, massB, [self.orbit[B], np.pi], self.name + " B", True, self.rank+1))

            self.comp[A].Create()
            self.comp[B].Create()

            self.color = self.comp[A].color + self.comp[B].color

        # or single star
        elif not self.binary:
            self.comp.append(Star(self, self, self.mass, [0, 0], self.name))
            self.comp[A].scorbit[MAX] = System.MAXSIZE
            self.comp[A].Create()
            self.color = self.comp[A].color

        # setup zones of planetary stability
        if self.parent is not None and self.parent.binary:
            dist = sum(self.parent.orbit)
            self.scorbit[MAX] = Astro.HillSphere(dist, self.mass, self.parent.mass)

        # Maximum System size criterion: should be stable against close flybys
        if self.parent is None:
            self.scorbit[MAX] =  Astro.HillSphere(0.003*Astro.pc_AU,self.mass,100.)# System.MAXSIZE

        if self.binary:
            self.scorbit[MIN] = self.orbit[B] + self.comp[B].scorbit[MAX]

            # create planets
            i = 0; n = 0
            while True:
                planetorbit = Astro.TitiusBode(i)                  # Titius Bode's law
                if planetorbit > self.scorbit[MAX]: break
                if planetorbit > self.scorbit[MIN]:
                    self.planet.append(Planet(self, self.root, [planetorbit, rd.random()*2*np.pi], self.name + chr(97+n)))
                    self.planet[n].Create()
                    n += 1
                i += 1

        # create ship
        # self.ship.append(Ship(self, self))
        # self.ship[0].Create()

        # Fill the system list with all bodies
        self.root.body.append(self)
        for comp in self.comp:
            self.root.body.append(comp)
            for planet in comp.planet:
                self.root.body.append(planet)
        for planet in self.planet:
            self.root.body.append(planet)

        pg.draw.circle(self.cmsImage, self.color, [5,5], 5)
        self.luminosity = sum([c.luminosity for c in self.comp])
        self.starImage = Screen.colorSurface(self.starImage, self.color)

    def Draw(self, screen, potential=False):
        linecolor = self.color

        # Sector Scale: draw every system, brightness by magnitude formula
        if screen.mapscale < Screen.SYSTEMTHRESHOLD:
#            image = pg.transform.rotozoom(self.starImage, 0, 0.2*np.log10(1.5+screen.starscale*self.luminosity))
            image = pg.transform.rotozoom(self.starImage, 0, -screen.starscale*(-2.5*np.log10(self.luminosity) - 25))
            screen.map[BODY].blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)
            return

        else:
        # System Scale: check if this is the camera system
            if not self.main.screen.refbody.root is self.root: return

            # stability zone and CoM
            if self.binary and screen.mapscale < Screen.PLANETTHRESHOLD:
                linecolor.a = 8
                pg.draw.circle(screen.map[GRAV], linecolor, screen.Map2Screen(
                    self.mappos, self.root.time), int(self.scorbit[MAX] * screen.mapscale))
                linecolor.a = 0
                pg.draw.circle(screen.map[GRAV], linecolor, screen.Map2Screen(
                    self.mappos, self.root.time), int(self.scorbit[MIN] * screen.mapscale))
                linecolor.a = 255

                image = pg.transform.rotozoom(self.cmsImage, 0, 0.3)
                screen.map[TRAIL].blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)

            for comp in self.comp:
                comp.Draw(screen, potential=potential)
            for planet in self.planet:
                planet.Draw(screen, potential=potential)
            for ship in self.ship:
                ship.Draw(screen)


    def CalcAcc(self, mappos):
        acc = np.array([0, 0])
        for comp in self.comp:
            direction = mappos - comp.mappos
            dist = np.linalg.norm(direction)
            acc = acc - Astro.G * comp.mass * direction / dist**3
            for planet in comp.planet:
                if Screen.GridDist(mappos, planet.mappos) < 2 * planet.scorbit[MAX]:
                    direction = mappos - planet.mappos
                    dist = np.linalg.norm(direction)
                    acc = acc - Astro.G * comp.mass / Astro.Msol_Me * direction / dist**3

        for planet in self.planet:
            if Screen.GridDist(mappos, planet.mappos) < 2 * planet.scorbit[MAX]:
                direction = mappos - planet.mappos
                dist = np.linalg.norm(direction)
                acc = acc - Astro.G * comp.mass / Astro.Msol_Me * direction / dist**3

        if (np.linalg.norm(acc) > 0.001):
            self.main.stepsize[1] = 0.005 / np.linalg.norm(acc)
        else:
            self.main.stepsize[1] = 10
        return acc

    def RootPos(self, time=0):
        if type(time) == np.ndarray:
            pos = np.ndarray((len(time), 2))
            pos[:, :] = self.mappos[:]
            return pos
        else:
            return self.mappos

    def MapPos(self, time = 0): # time in days
        # Get positions for a list of times:
        # [t1]    [x1,y1]
        # [t2] -> [x2,y2]
        # [...]   [...]
        if self.root is self:
            return self.RootPos(time)

        if type(time) == np.ndarray:
            t = np.ndarray((len(time),2))
            t[:,R] = time
            t[:,PHI] = time

            cs = np.ndarray((len(time),2))
            cs[:,:] = self.cylstart[:]
            cv = np.ndarray((len(time),2))
            cv[:,:] = self.cylvel[:]

            return Screen.Pol2Cart(cs+cv*t) + self.parent.MapPos(time)
        else:
            return Screen.Pol2Cart(self.cylstart + time*self.cylvel) + self.parent.MapPos(time)

    def getClosest(self, mappos):
        dists = [np.linalg.norm((mappos - body.MapPos(self.time))) for body in self.body]
        i = np.argmin(dists)
        return (i,self.body[i])

    def Move(self, dt=0):
        if self.root is self:
            self.time += dt
        else:
            self.cylpos = self.cylpos + dt*self.cylvel
            self.mappos = self.MapPos(self.root.time)

        for comp in self.comp:
            comp.Move(dt)
        for planet in self.planet:
            planet.Move(dt)
        for ship in self.ship:
            ship.Move(dt)

    def printTerm(self, indent = ""):
        print(indent + "Mass: " + str(self.mass))
        print(indent + "Name: " + " " + str(self.rank) +" "+ str(self.name))
        print(indent + str(self.root.name))
        print(indent + "Orbits: " + str(self.orbit))

        print(indent + "Comps:" )
        indent += "   "
        for comp in self.comp:
            comp.printTerm(indent)
