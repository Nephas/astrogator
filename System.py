from globals import *
from Star import Star
from Planet import Planet
from Ship import Ship
import random as rd

R=0; PHI=1
X=0; Y=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

class System:
    def __init__(self, parent):
        self.parent = parent
        self.time = 0
        self.mappos = np.array([0,0]) # [np.array([0,0]) for x in range(2*Screen.TRAILLENGTH)]           # absolute cartesian position over time
        self.mass = 10             # total system mass
        self.body = []
        self.comp = []              # comp[A], comp[B]
        self.planet = []            # common planets
        self.ship = []
        self.orbit = [0, 0]         # 0,0,0 in case of single, r1,r2,angle in case of double
        self.scorbit = [0, 0]       # stable circular orbit ranges
        self.image = pg.Surface((10,10))
        self.time = 0
        pg.draw.circle(self.image, pg.Color("white"), (5,5), 5)

    def Create(self):
        # create binary star

        if rd.random() < 0.99:
            massA = rd.random()*self.mass/2. +self.mass/2.
            massB = rd.random()*10
            self.mass = massA + massB
            self.orbit[A] = rd.random()*10
            self.orbit[B] = self.orbit[A]*massA/massB

            self.scorbit = [self.orbit[A] + self.orbit[B]*2, 100]

            phistart = 0
            self.comp.append(Star(self, self, massA, [self.orbit[A], 0]))
            self.comp.append(Star(self, self, massB, [self.orbit[B], math.pi]))
            self.comp[A].Create()
            self.comp[B].Create()
        # or single star
        else:
            massA = rd.random()*10
            self.mass = massA
            self.comp.append(Star(self, self, massA, [0,0]))
            self.comp[A].scorbit[MAX] = 100
            self.comp[A].Create()

#        create planets
        i = 0; n = 0
        while True:
            planetorbit = Astro.TitiusBode(i)
            if planetorbit > self.scorbit[MAX]: break
            if planetorbit > self.scorbit[MIN]:
                self.planet.append(Planet(self, self, [planetorbit,0]))
                self.planet[n].Create()
                n += 1
            i += 1

        # create ship
        self.ship.append(Ship(self, self))
        self.ship[0].Create()

        # Fill the system list with all bodies
        self.body.append(self)
        for comp in self.comp:
            self.body.append(comp)
            for planet in comp.planet: self.body.append(planet)
        for planet in self.planet: self.body.append(planet)
        for ship in self.ship: self.body.append(ship)

    def Draw(self,screen):
        # center of mass trail
        linecolor = pg.Color("white")
        # for step in range(1,len(self.mappos)):
        #     pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.mappos[step-1],step-1),screen.Map2Screen(self.mappos[step],step))
        #     linecolor.a -= screen.alphastep

        # stability zone
        linecolor.a = 15
        pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos), int(self.scorbit[MAX]*screen.mapscale))
        linecolor.a = 0
        pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos), int(self.scorbit[MIN]*screen.mapscale))
        linecolor.a = 255

        for planet in self.planet: planet.Draw(screen)
        for comp in self.comp: comp.Draw(screen)
        for ship in self.ship: ship.Draw(screen)

    def CalcAcc(self, mappos):
        acc = np.array([0,0])
        for comp in self.comp:
            direction = mappos - comp.mappos
            dist = np.linalg.norm(direction)
            acc = acc - Astro.G*comp.mass*direction/dist**3
            for planet in comp.planet:
                if Screen.GridDist(mappos,planet.mappos) < 2*planet.scorbit[MAX]:
                    direction = mappos - planet.mappos
                    dist = np.linalg.norm(direction)
                    acc = acc - Astro.G*comp.mass/Astro.Msol_Me*direction/dist**3

        for planet in self.planet:
            if Screen.GridDist(mappos,planet.mappos) < 2*planet.scorbit[MAX]:
                direction = mappos - planet.mappos
                dist = np.linalg.norm(direction)
                acc = acc - Astro.G*comp.mass/Astro.Msol_Me*direction/dist**3

        if (np.linalg.norm(acc) > 0.001):
            self.parent.stepsize[1] = 0.005/np.linalg.norm(acc)
        else:
            self.parent.stepsize[1] = 10
        return acc

    def MapPos(self, time = 0):
        return self.mappos

    def Move(self, dt):
        self.time += dt

        for comp in self.comp: comp.Move(dt)
        for planet in self.planet: planet.Move(dt)
        for ship in self.ship: ship.Move(dt)
