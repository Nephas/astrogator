from globals import *
from Sector import Sector

class Sector:
    def __init__(self, main, sizex=10, sizey=10, density=0.5):
        self.main = main
        self.system = []
        self.density = density      # in stars / pc^2
        self.size = [sizex,sizey]   # in pc

    def Create(self):
        rd.seed()
        numStars = int(self.size[X]*self.size[Y]*self.density)
        for i in range(0,numStars):
            self.system.append((rd.randint(0,2**16),0))


    def Draw(self,screen):
        for system in self.system:
            system.Draw(screen)
