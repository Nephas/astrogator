from globals import *

R=0; PHI=1
X=0; Y=1
A=0; B=1

class Screen:
    TRAILLENGTH = 100
    SIZE = np.array([1280,768])

    def __init__(self, parent):
        self.parent = parent
        self.mapscale = 50 # px/AU
        self.display = pg.display.set_mode(Screen.SIZE)
        self.map = pg.Surface(Screen.SIZE, flags = pg.SRCALPHA)
        self.gui = pg.Surface(Screen.SIZE, flags = pg.SRCALPHA)
        self.alphastep = int(255/(Screen.TRAILLENGTH))
        self.offset = 0.5*Screen.SIZE
        self.starscale = 0.05
        self.planetscale = 0.01
        self.moonscale = 0.005

    def RenderAll(self):
        self.RenderMap()
        self.RenderGui()
        self.display.fill(pg.Color("black"))
        self.display.blit(self.map, (0,0))
        self.display.blit(self.gui, (0,0))
        pg.display.flip()

    def RenderMap(self):
        self.map.fill(pg.Color(0,0,0,0))
        self.parent.world.Draw(self)

    def RenderGui(self):
        self.gui.fill(pg.Color(0,0,0,0))
        linecolor = pg.Color("white")
        linecolor.a = 50
        pg.draw.line(self.gui, linecolor, (Screen.SIZE[X]/2,0), (Screen.SIZE[X]/2,Screen.SIZE[Y]))
        pg.draw.line(self.gui, linecolor, (0,Screen.SIZE[Y]/2), (Screen.SIZE[X],Screen.SIZE[Y]/2))
        for i in range(-5,7):
            pg.draw.circle(self.gui, linecolor, (Screen.SIZE[X]/2,Screen.SIZE[Y]/2), int(math.floor(self.mapscale*2**i))+1, 1)

#        pg.draw.line(self.gui, linecolor,(Screen.SIZE[X],Screen.SIZE[X]),(-Screen.SIZE[X],-Screen.SIZE[X]))
#        pg.draw.line(self.gui, linecolor,(-Screen.SIZE[X],Screen.SIZE[X]),(Screen.SIZE[X],-Screen.SIZE[X]))


#    def Map2Screen(self,pos):    # Coordinate transformation from mapspace to screenspace
#        return pos*self.mapscale + self.offset

    def Map2Screen(self, mappos, time = 0):    # Coordinate transformation from mapspace to screenspace
        refbody = self.parent.world.body[self.parent.focus]
        screenpos = Screen.SIZE/2 + self.mapscale*(mappos - refbody.MapPos(time))
        return screenpos.astype(int)

    @staticmethod
    def Pol2Cart(cylpos):
        return np.array([math.cos(cylpos[PHI])*cylpos[R], math.sin(cylpos[PHI])*cylpos[R]])

    @staticmethod
    def GridDist(mapposA,mapposB):
        return (mapposA[0] - mapposB[0]) + (mapposA[1] - mapposB[1])
