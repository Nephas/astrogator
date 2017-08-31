from globals import *
from Planet import Planet

R=0; PHI=1
X=0; Y=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

class Star:
    def __init__(self, parent, system, mass, cylpos = [0,0]):
        self.parent = parent
        self.system = system
        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = None                  # now in rad/day
        self.mappos = None                  # absolute cartesian position now in AU
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
            self.torbit = 365*math.sqrt(distance**3/self.parent.mass) # orbital period in years from parent mass
            self.cylvel = np.array([0,2*math.pi/(self.torbit)])

        self.radius = Astro.MassRadius(self.mass)
        self.luminosity = Astro.MassLuminosity(self.mass)
        self.temp = Astro.StefanBoltzmann(self.luminosity,self.radius)
        self.spectral = Astro.SpectralClass(self.temp)
        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, self.spectral[COLOR], [50,50], 50)

        self.scorbit[MIN] = 0.5
        if self.scorbit[MAX] == 0:
            self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass,self.parent.mass)

        i = 0; n = 0
        while True:
            planetorbit = Astro.TitiusBode(i)                  # Titius Bode's law
            if planetorbit > self.scorbit[MAX]: break
            if planetorbit > self.scorbit[MIN]:
                self.planet.append(Planet(self, self.system, [planetorbit, 0]))
                self.planet[n].Create()
                n += 1
            i += 1

    def Draw(self,screen):

        # star hill sphere
        linecolor = pg.Color("white")
        linecolor.a = 15
        pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos,self.system.time), int(self.scorbit[MAX]*screen.mapscale))
        linecolor.a = 0
        pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos,self.system.time), int(self.scorbit[MIN]*screen.mapscale))
        linecolor.a = 255

        for planet in self.planet: planet.Draw(screen)

        # star trail
        traillength = self.torbit
        time = self.system.time
        dt = self.torbit/200
        while time > self.system.time - self.torbit/4:
            pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.MapPos(time), time),0)
#            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.MapPos(time-dt), time-dt), screen.Map2Screen(self.MapPos(time), time))
            time -= dt

        # star prediction
        linecolor = pg.Color("blue")
        time = self.system.time
        while time < self.system.time + self.torbit/4:
            pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.MapPos(time), time),0)
#            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.MapPos(time+dt), time+dt), screen.Map2Screen(self.MapPos(time), time))
            time += dt

        # star image
        image = pg.transform.rotozoom(self.image, 0, screen.starscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.system.time) - np.array(image.get_size())*0.5)

#    def InitMove(self, dt):

    # get mapspace position of absolute time
    def MapPos(self, time = 0): # time in days
        cylnow = self.cylstart + time*self.cylvel
        return Screen.Pol2Cart(cylnow) + self.parent.MapPos(time)

    def Move(self, dt):
        self.cylpos = self.cylpos + dt*self.cylvel
        self.mappos = self.MapPos(self.system.time)

        for planet in self.planet: planet.Move(dt)
