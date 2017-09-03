from globals import *
from Astro import Astro
from System import System

class Sector:
    def __init__(self, main, size = [5,5], density=0.5):
        self.main = main
        self.time = 0
        self.system = []
        self.density = density      # in stars / pc^2
        self.size = size   # in pc
        self.body = self.system

    def Create(self):
        rd.seed()
        numStars = min(1000,int(self.size[X]*self.size[Y]*self.density))
        for i in range(0,numStars):
            pos = Astro.pc_AU*0.5*np.array([np.random.normal()*self.size[X],np.random.normal()*self.size[Y]])
            sys = System(self.main, mappos = pos)
            sys.CreateRoot(rd.randint(0,2**16), 0)
            self.system.append(sys)

        self.main.screen.refbody = rd.choice(self.body)

    def Draw(self,screen,potential):
#        self.main.screen.refbody.root.Draw(screen,potential)
        for system in self.system:
            system.Draw(screen, potential)

    def Move(self, dt):
        self.time += dt
#        for system in self.system:
#            system.Move(dt)
        self.main.screen.refbody.root.Move(dt)

    def printTerm(self, indent = ""):
        print(indent + "Sector:" )
        indent += "   "
        for system in self.system:
            print(indent + "Name: " + str(system.name))
            print(indent + "Mass: " + str(system.mass))
            print(indent + "Pos: " + str(system.mappos))

    def getClosest(self, mappos):
        dists = [np.linalg.norm((mappos - body.mappos)) for body in self.body]
        i = np.argmin(dists)
        if self.main.screen.mapscale < 1:
            return (i,self.body[i])
        else:
            return self.body[i].getClosest(mappos)
