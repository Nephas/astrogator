from globals import *
from Moon import Moon

R=0; PHI=1
X=0; Y=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

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
        self.torbit = 365*math.sqrt(self.cylpos[R]**3/self.parent.mass) # orbital period in days from parent mass
        self.cylvel = np.array([0,2*math.pi/self.torbit])

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

        linecolor = pg.Color("orange")
        linecolor.a = 75
        pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos,self.system.time), int(self.scorbit[MAX]*screen.mapscale))
        linecolor.a = 255

        # planet trail
        traillength = self.torbit
        time = self.system.time
        dt = self.torbit/200
        while time > self.system.time - self.torbit/4:
            pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.MapPos(time), time),0)
#            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.MapPos(time-dt), time-dt), screen.Map2Screen(self.MapPos(time), time))
            time -= dt

        # planet prediction
        linecolor = pg.Color("green")
        time = self.system.time
        while time < self.system.time + self.torbit/4:
            pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.MapPos(time), time),0)
#            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.MapPos(time+dt), time+dt), screen.Map2Screen(self.MapPos(time), time))
            time += dt

        image = pg.transform.rotozoom(self.image, -self.cylpos[PHI]/(2*math.pi)*360, screen.planetscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos,self.system.time) - np.array(image.get_size())*0.5)

    def MapPos(self, time = 0): # time in days
        cylnow = self.cylstart + time*self.cylvel
        return Screen.Pol2Cart(cylnow) + self.parent.MapPos(time)

    def Move(self, dt):
        self.cylpos = self.cylpos + dt*self.cylvel
        self.mappos = self.MapPos(self.system.time)

        for moon in self.moon: moon.Move(dt)
