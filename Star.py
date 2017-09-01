from globals import *
from Planet import Planet

class Star:
    def __init__(self, parent, root, mass, cylpos = [0,0], name = "unknown"):
        self.parent = parent
        self.root = root
        self.name = name

        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = np.array([0,0])       # now in rad/day
        self.mappos = np.array([0,0])       # absolute cartesian position now in AU

        self.planet = []
        self.mass = mass
        self.scorbit = [0,0]          # stable circular orbit ranges
        self.torbit = 0
        self.luminosity = 0     # solar lum
        self.radius = 0         # solar radii
        self.temp = 0           # Kelvin
        self.spectral = []
        self.image = None

    def Create(self):

        if self.cylpos[R] != 0:
            distance = self.parent.orbit[A] + self.parent.orbit[B]
            self.torbit = 365*np.sqrt(distance**3/self.parent.mass) # orbital period in years from parent mass
            self.cylvel = np.array([0,2*np.pi/(self.torbit)])

        self.radius = Astro.MassRadius(self.mass)
        self.luminosity = Astro.MassLuminosity(self.mass)
        self.temp = Astro.StefanBoltzmann(self.luminosity,self.radius)
        self.spectral = Astro.SpectralClass(self.temp)
        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, self.spectral[COLOR], [50,50], 50)

        self.scorbit[MIN] = 0.25
        if self.scorbit[MAX] == 0:
            self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass,self.parent.mass)

        i = 0; n = 0
        while True:
            planetorbit = Astro.TitiusBode(i)                  # Titius Bode's law
            if planetorbit > self.scorbit[MAX]: break
            if planetorbit > self.scorbit[MIN]:
                self.planet.append(Planet(self, self.root, [planetorbit, rd.random()*2*np.pi], self.name + chr(97+n)))
                self.planet[n].Create()
                n += 1
            i += 1

    def Draw(self,screen, body=True, potential=False):

        # star hill sphere
        if potential:
            linecolor = pg.Color("white")
            linecolor.a = 15
            pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(self.mappos,self.root.time), int(self.scorbit[MAX]*screen.mapscale))
            linecolor.a = 0
#            pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(self.mappos,self.root.time), int(self.scorbit[MIN]*screen.mapscale))
            linecolor.a = 255

        for planet in self.planet: planet.Draw(screen,potential=potential)

        if not Screen.Contains(screen.Map2Screen(self.mappos,self.root.time)):
            return

        # star trail
        if potential:
            linecolor = pg.Color("blue")
            length = min(self.root.body[self.root.main.focus].torbit/3, self.torbit/3)
            times = np.linspace(self.root.time - length, self.root.time, 20)
            mappos = screen.Map2Screen(self.MapPos(times), times)
            pg.draw.lines(screen.potential, linecolor, False, mappos)

        # star image
        image = pg.transform.rotozoom(self.image, 0, screen.starscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)

    def MapPos(self, time = 0): # time in days
        # Get positions for a list of times:
        # [t1]    [x1,y1]
        # [t2] -> [x2,y2]
        # [...]   [...]
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
        self.cylpos = self.cylpos + dt*self.cylvel
        self.mappos = self.MapPos(self.root.time)

        for planet in self.planet: planet.Move(dt)

    def printTerm(self, indent):
        print(indent + "Mass: " + str(self.mass))
        print(indent + "Name: Star " + str(self.name))
#        print(indent + "Comps:" )
#        indent += "   "
#        for comp in self.comp:
#            comp.printTerm(indent)
