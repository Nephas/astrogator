from globals import *
from Moon import Moon
from Screen import Screen
from Astro import Astro

class Planet:
    PLANETIMAGE = pg.image.load("graphics/planet.png")

    def __init__(self, parent, root, cylpos=[0,0], name = "unknown"):
        self.parent = parent
        self.root = root
        self.name = name

        self.moon = []
        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = None                  # now in rad/day
        self.mappos = None                  # absolute cartesian position now in AU

        self.mass = 0       # in earth mass
        self.scorbit = [0,0]  # Hills-Radius in AU
        self.radius = 0     # in earth radii
        self.torbit = 0

        self.image = None

    def Create(self):
#        self.mass = rd.uniform(0.5, 100)
        self.mass = min(300,0.5 + np.random.exponential(self.cylpos[R]))
        self.radius = Astro.PlanetRadius(self.mass)

        #setup circular orbit
        self.torbit = 365*np.sqrt(self.cylpos[R]**3/self.parent.mass) # orbital period in days from parent mass
        self.cylvel = np.array([0,2*np.pi/self.torbit])

        self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass*Astro.Me_Msol,self.parent.mass)
        self.scorbit[MIN] = 0#.1*self.scorbit[MAX]

        # # create moons
        i = 0; n = 0
        while True:
            moonorbit = Astro.TitiusBode(i,0.01)           # Titius Bode's law
            if moonorbit > self.scorbit[MAX]: break
            if moonorbit > self.scorbit[MIN]:
                self.moon.append(Moon(self, self.root, [moonorbit, rd.random()*2*np.pi]))
                self.moon[n].Create()
                n += 1
            i += 1

        self.image = Planet.PLANETIMAGE.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("brown"))


    def Draw(self, screen, body=True, potential=False):
        if not Screen.Contains(screen.Map2Screen(self.mappos,self.root.time)):
            return

        # # planet hill sphere
        linecolor = pg.Color("brown")
        linecolor.a = 15
        pg.draw.circle(screen.map[GRAV], linecolor, screen.Map2Screen(self.mappos,self.root.time), int(self.scorbit[MAX]*screen.mapscale))
        linecolor.a = 255

        # planet trail
        linecolor = Screen.ColorBrightness(pg.Color("brown"),0.8)
        length = min(self.root.main.screen.refbody.torbit/4, self.torbit/4)
        times = np.linspace(self.root.time - length, self.root.time, 20)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map[TRAIL], linecolor, False, mappos)

            # linecolor = pg.Color("darkgreen")
            # times = np.linspace(self.root.time + length, self.root.time, 20)
            # mappos = screen.Map2Screen(self.MapPos(times), times)
            # pg.draw.lines(screen.potential, linecolor, False, mappos)

        if screen.mapscale > Screen.PLANETTHRESHOLD:
            for moon in self.moon: moon.Draw(screen, potential=potential)

        image = pg.transform.rotozoom(self.image, -self.cylpos[PHI]/(2*np.pi)*360, screen.planetscale*self.radius)
        screen.map[BODY].blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)


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

        for moon in self.moon: moon.Move(dt)
