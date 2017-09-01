from globals import *

class Moon:
    def __init__(self, parent, root, cylpos=[0,0]):
        self.parent = parent
        self.root = root
        self.cylstart = np.array(cylpos)    # parent related coordinates r, phi
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylvel = None                  # now in rad/day
        self.mappos = None                  # absolute cartesian position now in AU
        self.mass = 0
        self.image = None
        self.radius = 1

    def Create(self):
        self.mass = rd.random()/10

        #setup circular orbit
        self.torbit = 365*np.sqrt(self.cylpos[R]**3/self.parent.mass) # orbital period in days from parent mass
        self.cylvel = np.array([0,2*np.pi/self.torbit])

        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color("blue"), [50,50], 50)
        pg.draw.rect(self.image, TRANSPARENCY, pg.Rect(50,0,50,100))


    def Draw(self,screen,potential=False):
        if not Screen.Contains(screen.Map2Screen(self.mappos,self.root.time)):
            return

        potential=True
        # planet trail
        if potential:
            linecolor = pg.Color("darkgray")
            length = min(self.root.body[self.root.main.focus].torbit/6, self.torbit/6)
            times = np.linspace(self.root.time - length, self.root.time, 10)
            mappos = screen.Map2Screen(self.MapPos(times), times)
            pg.draw.lines(screen.potential, linecolor, False, mappos)

        if screen.moonscale > 0.02:
            image = pg.transform.rotozoom(self.image, -self.parent.cylpos[PHI]/(2*np.pi)*360, screen.moonscale*self.radius)
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
