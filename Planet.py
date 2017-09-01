from globals import *
from Moon import Moon

class Planet:
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
        self.mass = rd.uniform(0.5, 100)
        self.radius = Astro.PlanetRadius(self.mass)
#        self.mappos.insert(0,Screen.Pol2Cart(self.cylpos) + self.parent.mappos[0])

        #setup circular orbit
        self.torbit = 365*np.sqrt(self.cylpos[R]**3/self.parent.mass) # orbital period in days from parent mass
        self.cylvel = np.array([0,2*np.pi/self.torbit])

        self.scorbit[MAX] = 0.1*Astro.HillSphere(self.cylpos[R],self.mass*Astro.Me_Msol,self.parent.mass)
        self.scorbit[MIN] = 0.05*self.scorbit[MAX]

        # # create moons
        # i = 0; n = 0
        # while True:
        #     moonorbit = Astro.TitiusBode(i,self.scorbit[MIN])           # Titius Bode's law
        #     print(moonorbit)
        #     if moonorbit > self.scorbit[MAX]: break
        #     if moonorbit > self.scorbit[MIN]:
        #         self.moon.append(Moon(self, self.root, [moonorbit, rd.random()*2*np.pi]))
        #         self.moon[n].Create()
        #         n += 1
        #     i += 1

        self.image = pg.image.load("graphics/star.png",)
        self.image.convert_alpha()
        self.image = Screen.colorSurface(self.image.copy(), pg.Color("brown"))
        self.image.convert_alpha()
        pg.draw.rect(self.image, TRANSPARENCY, pg.Rect(50,0,50,100))


    def Draw(self, screen, body=True, potential=False):
        # if screen.moonscale > 2:

        if not Screen.Contains(screen.Map2Screen(self.mappos,self.root.time)):
            return

        # # planet hill sphere
        if potential:
        #     linecolor = pg.Color("orange")
        #     linecolor.a = 15
        #     pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(self.mappos,self.root.time), int(self.scorbit[MAX]*screen.mapscale))
        #     linecolor.a = 0
        #     pg.draw.circle(screen.potential, linecolor, screen.Map2Screen(self.mappos,self.root.time), int(self.scorbit[MIN]*screen.mapscale))
        #     linecolor.a = 255

        # planet trail
            linecolor = pg.Color("brown")
            length = min(self.root.body[self.root.main.focus].torbit/4, self.torbit/4)
            times = np.linspace(self.root.time - length, self.root.time, 20)
            mappos = screen.Map2Screen(self.MapPos(times), times)
            pg.draw.lines(screen.potential, linecolor, False, mappos)

            linecolor = pg.Color("darkgreen")
            times = np.linspace(self.root.time + length, self.root.time, 20)
            mappos = screen.Map2Screen(self.MapPos(times), times)
            pg.draw.lines(screen.potential, linecolor, False, mappos)

        image = pg.transform.rotozoom(self.image, -self.cylpos[PHI]/(2*np.pi)*360, screen.planetscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.root.time) - np.array(image.get_size())*0.5)

#        if screen.moonscale < 0.02:
        for moon in self.moon: moon.Draw(screen, potential=potential)


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
