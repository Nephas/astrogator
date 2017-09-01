from globals import *
from Moon import Moon

class Planet:
    def __init__(self, parent, system, cylpos=[0,0]):
        self.parent = parent
        self.system = system
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

        # for i in range(rd.randint(0,3)):
        #     self.moon.append(Moon(self, [(i+1)*0.005,rd.random()*2*math.pi]))
        #     self.moon[i].Create()

        self.scorbit[MAX] = Astro.HillSphere(self.cylpos[R],self.mass*Astro.Me_Msol,self.parent.mass)
        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color("red"), [50,50], 50)
        pg.draw.rect(self.image, TRANSPARENCY, pg.Rect(50,0,50,100))


    def Draw(self,screen):
        # if screen.moonscale > 2:
        for moon in self.moon: moon.Draw(screen)

        if not Screen.Contains(screen.Map2Screen(self.mappos,self.system.time)):
            return

        # planet trail
        linecolor = pg.Color("orange")
        length = min(self.system.body[self.system.parent.focus].torbit/4, self.torbit/4)
        times = np.linspace(self.system.time - length, self.system.time, 20)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map, linecolor, False, mappos)

        linecolor = pg.Color("darkgreen")
        times = np.linspace(self.system.time + length, self.system.time, 20)
        mappos = screen.Map2Screen(self.MapPos(times), times)
        pg.draw.lines(screen.map, linecolor, False, mappos)

        image = pg.transform.rotozoom(self.image, -self.cylpos[PHI]/(2*np.pi)*360, screen.planetscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.system.time) - np.array(image.get_size())*0.5)

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
        self.mappos = self.MapPos(self.system.time)

        for moon in self.moon: moon.Move(dt)
