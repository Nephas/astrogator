from globals import *

class Moon:
    def __init__(self, parent, cylpos=[0,0]):
        self.parent = parent
        self.cylpos = np.array(cylpos)    # parent related coordinates r in AU, phi in rad
        self.mappos = []  # cartesian position
        self.cylvel = np.array([0,0])  # radial velocity in AU/day angular velocity in rad/day
        self.mass = 0
        self.image = None
        self.radius = 1

    def Create(self):
        self.mass = rd.random()/10
        self.mappos.insert(0,Screen.Pol2Cart(self.cylpos) + self.parent.mappos[0])

        #setup circular orbit
        torbit = math.sqrt(self.cylpos[R]**3/(2.27e-07*self.parent.mass)) # orbital period in years from parent mass
        self.cylvel = np.array([0,2*math.pi/(torbit*365)])
        print(self.mass)

        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color("blue"), [50,50], 50)
        pg.draw.rect(self.image, TRANSPARENCY, pg.Rect(50,0,50,100))


    def Draw(self,screen):
        linecolor = pg.Color("darkblue")
#        for step in range(1,len(self.mappos)):
#            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.mappos[step-1],step-1),screen.Map2Screen(self.mappos[step],step))
#            linecolor.a -= screen.alphastep

        image = pg.transform.rotozoom(self.image, -self.parent.cylpos[PHI]/(2*math.pi)*360, screen.moonscale*self.radius)
        screen.map.blit(image, screen.Map2Screen(self.mappos[0]) - np.array(image.get_size())*0.5)

#        screen.display.blit(pg.transform.rotate(self.image, -self.parent.pos[PHI]/(2*math.pi)*360), vec.Sub(screen.Map2Screen(self.mappos),[self.image.get_width()/2,self.image.get_height()/2]))

    def Move(self, dt):
        self.cylpos[PHI] += dt*self.cylvel[PHI]
        self.mappos.insert(0,Screen.Pol2Cart(self.cylpos) + self.parent.mappos[0])
        if len(self.mappos) >= Screen.TRAILLENGTH:
            self.mappos.pop()
