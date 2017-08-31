from globals import *

class Sector:
    def __init__(self, owner, sizex=10, sizey=10, density=0.5):
        self.owner = owner
        self.system = []
        self.density = density      # in stars / pc^2
        self.size = [sizex,sizey]   # in pc

    def Create(self):
        rd.seed()
        numStars = int(self.size[X]*self.size[Y]*self.density)
        for i in range(0,numStars):
            new = System(rd.random()*self.size[X], rd.random()*self.size[Y])
            new.Create()
            self.system.append(new)

    def Draw(self,screen):
        for system in self.system:
            system.Draw(screen)
