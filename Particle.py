from globals import *
from Moon import Moon
from Screen import Screen
from Astro import Astro

class Particle:
    def __init__(self, parent, root, cylpos=[0,0]):
        self.parent = parent
        self.root = root

        self.tbirth = self.root.time
        self.cylpos = np.array(cylpos)      # running polar position
        self.cylstart = np.array(cylpos)
        self.cylvel = np.array([0.1,0])       # now in rad/day
        self.mappos = np.array([0,0])                  # absolute cartesian position now in AU

        self.image = pg.Surface([1,1], flags = pg.SRCALPHA)
        self.image.fill(self.parent.color)

    def Draw(self,screen):
        r = int(self.cylpos[R]*self.root.main.screen.mapscale+1)
        color = Screen.ColorBrightness(self.parent.color,0.1 + 0.5*(1 - self.cylpos[R]/self.parent.scorbit[MAX]))
        pg.draw.circle(screen.map[TRAIL], color, screen.Map2Screen(self.parent.mappos,self.root.time).astype(int), int(r), 1)
#        points:
#        screen.potential.blit(self.image, screen.Map2Screen(self.MapPos(self.root.time),self.root.time) - np.array(self.image.get_size())*0.5)

    def MapPos(self, time = 0): # time in days
        return Screen.Pol2Cart(self.cylpos) + self.parent.mappos

    def Move(self, dt):
        self.cylvel[R] = min(0.1,1./self.cylpos[R])
        self.cylpos = self.cylpos + dt*self.cylvel
        self.mappos = self.MapPos(self.root.time)

        if self.cylpos[R] > self.parent.scorbit[MAX]:
            self.parent.wind.remove(self)
