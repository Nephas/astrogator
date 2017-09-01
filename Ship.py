from globals import *
from Planet import Planet

R=0; PHI=1
X=0; Y=1
POS=0; T=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

class Ship:
    def __init__(self, parent, root, startpos = [1,1], mapvel = [0,0.01]):
        self.parent = parent
        self.root = root
        self.orientation = rd.random()*2*np.pi      # parent related coordinates r, phi
        self.pointing = np.array([np.cos(self.orientation),np.sin(self.orientation)])
        self.mappos = [[np.array(startpos),0] for x in range(50)]  # cartesian position in absolute space with according time
        self.mapvel = np.array(mapvel)    # map velocity in AU/day

#        self.mapacc = np.array([0,0])

        self.image = None
        self.mass = 0

    def Create(self):
#        self.mappos.insert(0,self.mappos[0] + self.mapvel)

        self.image = pg.Surface([100,100], flags = pg.SRCALPHA)
        pg.draw.polygon(self.image, pg.Color("blue"), [(100,0),(100,100),(0,50)])

    def Draw(self,screen):

        linecolor = pg.Color("blue")
        # linecolor.a = 255
        for step in range(1,len(self.mappos)):
#            pg.draw.circle(screen.map, linecolor, screen.Map2Screen(self.mappos[step][POS],self.mappos[step][T]),0)
            pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.mappos[step][POS],self.mappos[step][T]),screen.Map2Screen(self.mappos[step-1][POS],self.mappos[step-1][T]))
        #     linecolor.a -= screen.alphastep
        #
        #
        # linecolor = pg.Color("red")
        # linecolor.a = 255
        # for step in range(1,Screen.TRAILLENGTH):
        #     pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.mappos[step-1],step-1),screen.Map2Screen(self.mappos[step],step))
        #     linecolor.a -= screen.alphastep

        image = pg.transform.rotozoom(self.image, -self.orientation/(2*np.pi)*360, screen.planetscale*10    )
        screen.map.blit(image, screen.Map2Screen(self.mappos[0][POS],self.root.time) - np.array(image.get_size())*0.5)

        # linecolor = pg.Color("green")
        # for step in range(1,len(self.mappred)):
        #     pg.draw.line(screen.map, linecolor, screen.Map2Screen(self.mappred[step-1],0),screen.Map2Screen(self.mappred[step],0))
#            linecolor.a -= screen.alphastep

    def MapPos(self, time = 0): # time in days
        cylnow = self.cylstart + time*self.cylvel
        return self.mappos[time] + self.parent.MapPos(time)

    def Move(self, dt):
        self.pointing = np.array([np.cos(self.orientation),np.sin(self.orientation)])
        self.mapvel = self.mapvel + dt*self.root.CalcAcc(self.mappos[0][POS])
        self.mappos.insert(0,[self.mappos[0][POS] + dt*self.mapvel, self.root.time])
        self.mappos.pop()

#        dt = 1
#        self.mappos[0] = self.mappos[Screen.NOW]
#        mapvel = self.mapvel
#        for i in range(0, Screen.NOW-2):
#            mapvel = mapvel # + dt*self.parent.CalcAcc(self.mappos[i])
#            self.mappos[i+1] = self.mappos[i] + dt*mapvel

        # self.mappred = [self.mappos[0]]
        # for i in range(Screen.TRAILLENGTH):
        #     self.mappred.append(self.mappred[0] + i*dt*self.mapvel)
