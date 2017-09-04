from globals import *
from Astro import Astro
from System import System
from Screen import Screen

class Sector:
    STARIMAGE = pg.image.load("graphics/star.png")

    def __init__(self, main, size = [22,22], density=1):
        self.main = main
        self.time = 0
        self.system = []
        self.activesystem = None
        self.density = density      # in stars / pc^2
        self.size = size   # in pc

    def Generate(self):
        rd.seed()
        numStars = min(1000,int(self.size[X]*self.size[Y]*self.density))

        print("Generating Systems:")

        for i in range(numStars):
            pos = Astro.pc_AU*0.5*np.array([np.random.normal()*self.size[X],np.random.normal()*self.size[Y]])
            sys = System(self.main, mappos = pos)
            pack = sys.Generate(rd.randint(0,2**16), 0)
            self.system.append(pack)

            if i % 100 == 0: print("  "+str(i)+"/"+str(numStars))

        self.activesystem = rd.choice(self.system).Unpack()
        self.main.screen.refbody = self.activesystem


    def Draw(self,screen):
        if screen.mapscale < Screen.SYSTEMTHRESHOLD:
            for system in self.system:
                if Screen.Contains(screen.Map2Screen(system.mappos,self.time)):
                    image = pg.transform.rotozoom(system.image, 0, - 5*screen.starscale*(system.mag))
                    screen.map[BODY].blit(image, screen.Map2Screen(system.mappos,self.time) - np.array(image.get_size())*0.5)
        else:
            self.activesystem.Draw(screen)



    def Move(self, dt):
        self.time += dt
        self.activesystem.Move(dt)

    def printTerm(self, indent = ""):
        print(indent + "Sector:" )
        indent += "   "
        for system in self.system:
            print(indent + "Name: " + str(system.name))
            print(indent + "Mass: " + str(system.mass))
            print(indent + "Pos: " + str(system.mappos))

    def getClosest(self, mappos):
        if self.main.screen.mapscale < Screen.SYSTEMTHRESHOLD:
            dists = [np.linalg.norm((mappos - system.mappos)) for system in self.system]
            i = np.argmin(dists)
            self.activesystem = self.system[i].Unpack()
            return self.activesystem
        else:
            return self.activesystem.getClosest(mappos)
