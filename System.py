from globals import *
from Star import Star
from Planet import Planet
from Ship import Ship
import random as rd


class System:

    def __init__(self, parent, main = None, root = None, mass = 10, cylpos = [0,0], name = "Epsilon Eridani", binary = True, rank = 0):
        self.main = main
        self.parent = parent
        self.name = name
        self.time = 0
        self.rank = rank
        self.root = root
        self.binary = binary
        if self.root is None:
            self.root = self

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0,0])       # now in rad/day
        self.mappos = np.array([0,0])       # absolute cartesian position now in AU

        self.mass = mass             # total system mass
        self.body = []
        self.comp = []              # comp[A], comp[B]
        self.planet = []            # common planets
        self.ship = []
        # 0,0,0 in case of single, r1,r2,angle in case of double
        self.orbit = [0, 0]
        self.torbit = 1e+15
        self.scorbit = [0, 0]       # stable circular orbit ranges
        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color("green"), [50,50], 50)

    def Create(self):
        if self.binary:
            massA = rd.uniform(0.5,0.9) * self.mass
            massB = self.mass - massA

            if self.rank == 0:
                self.orbit[B] = rd.uniform(10,50)
            else:
                self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass,self.parent.mass)
                self.orbit[B] = rd.uniform(0.2,0.8)*self.scorbit[MAX]

            self.orbit[A] = self.orbit[B] * massB / massA


            if self.cylpos[R] != 0:
                distance = self.parent.orbit[A] + self.parent.orbit[B]
                self.torbit = 365*np.sqrt(distance**3/self.parent.mass) # orbital period in years from parent mass
                self.cylvel = np.array([0,2*np.pi/(self.torbit)])

            if rd.random() < 0.5 or self.rank >= 2:
                self.comp.append(Star(self, self.root, massA, [self.orbit[A], 0], self.name + " A"))
            else:
                self.comp.append(System(self, self.main, self.root, massA, [self.orbit[A], 0], self.name + " A", True, self.rank+1))
            if rd.random() < 0.5 or self.rank >= 1:
                self.comp.append(Star(self, self.root, massB, [self.orbit[B], np.pi], self.name + " B"))
            else:
                self.comp.append(System(self, self.main, self.root, massB, [self.orbit[B], np.pi], self.name + " B", True, self.rank+1))

            self.comp[A].Create()
            self.comp[B].Create()
        # or single star
        elif not self.binary:
            self.comp.append(Star(self, self, self.mass, [0, 0], self.name))
            self.comp[A].scorbit[MAX] = 100
            self.comp[A].Create()

#        create planets
        # i = 0
        # n = 0
        # while True:
        #     planetorbit = Astro.TitiusBode(i)
        #     if planetorbit > self.scorbit[MAX]:
        #         break
        #     if planetorbit > self.scorbit[MIN]:
        #         self.planet.append(Planet(self, self, [
        #                            planetorbit, rd.random() * 2 * np.pi], self.name + " " + chr(97 + n)))
        #         self.planet[n].Create()
        #         n += 1
        #     i += 1

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

    def Draw(self, screen, potential=False):
        linecolor = pg.Color("green")

        # stability zone
        if potential:
            linecolor.a = 10
            pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(
                self.mappos, self.time), int(self.scorbit[MAX] * screen.mapscale))
            linecolor.a = 0
            pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(
                self.mappos, self.time), int(self.scorbit[MIN] * screen.mapscale))
            linecolor.a = 255

        for planet in self.planet:
            planet.Draw(screen, potential=potential)
        for comp in self.comp:
            comp.Draw(screen, potential=potential)
        for ship in self.ship:
            ship.Draw(screen)

        image = pg.transform.rotozoom(self.image, 0, 0.05)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)


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
        if type(time) == list:
            return [self.mappos] * len(time)
        elif type(time) == np.ndarray:
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
        if self.rank == 0:
            return self.RootPos(time)

        if type(time) == list:
            return [Screen.Pol2Cart(self.cylstart + t*self.cylvel) + self.parent.MapPos(t) for t in time]
        elif type(time) == np.ndarray:
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

    def Move(self, dt):
        self.time += dt
        self.cylpos = self.cylpos + dt*self.cylvel
        self.mappos = self.MapPos(self.root.time)

        for comp in self.comp:
            comp.Move(dt)
        for planet in self.planet:
            planet.Move(dt)
        for ship in self.ship:
            ship.Move(dt)

    def printTerm(self, indent):
        print(indent + "Mass: " + str(self.mass))
        print(indent + "Name: " + " " + str(self.rank) +" "+ str(self.name))
        print(indent + str(self.root.name))
        print(indent + "Orbits: " + str(self.orbit))

        print(indent + "Comps:" )
        indent += "   "
        for comp in self.comp:
            comp.printTerm(indent)
