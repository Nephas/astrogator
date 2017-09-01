from globals import *

R=0; PHI=1
X=0; Y=1
A=0; B=1

class Screen:
    TRAILLENGTH = 100
    SIZE = np.array([1024,768])

    def __init__(self, parent):
        self.parent = parent
        self.mapscale = 50 # px/AU
        self.display = pg.display.set_mode(Screen.SIZE)

        self.back = pg.Surface(Screen.SIZE)
        self.back.fill(pg.Color("black"))
        self.map = pg.Surface(Screen.SIZE, flags = pg.SRCALPHA)
        self.gui = pg.Surface(Screen.SIZE, flags = pg.SRCALPHA)
        self.font = pg.font.SysFont("Arial", 12)

        self.alphastep = int(255/(Screen.TRAILLENGTH))
        self.offset = 0.5*Screen.SIZE
        self.starscale = 0.05
        self.planetscale = 0.01
        self.moonscale = 0.005

    def Render(self, gui=False):
        self.RenderMap()
        self.display.blit(self.back, (0,0))
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
            pg.draw.circle(self.gui, linecolor, (Screen.SIZE[X]/2,Screen.SIZE[Y]/2), int(np.floor(self.mapscale*2**i))+1, 1)

        tstep = self.font.render("Time-step: " + str(self.parent.stepsize[0]*self.parent.TPS) + " days/s", 1, pg.Color("white"))
        t = self.font.render("Time: " + str(self.parent.world.time) + " days", 1, pg.Color("white"))
        # put the label object on the screen at point x=100, y=100
        self.gui.blit(tstep, (10, 10))
        self.gui.blit(t, (10, 30))

    def Map2Screen(self, mappos, time = 0):    # Coordinate transformation from mapspace to screenspace
        refbody = self.parent.world.body[self.parent.focus]
        screenpos = Screen.SIZE/2. + self.mapscale*(mappos - refbody.MapPos(time))

        return screenpos.astype(int)

    @staticmethod
    def Contains(pos):
        if pos[X] < 0 or pos[Y] < 0:
            return False
        elif pos[X] > Screen.SIZE[X] or pos[Y] > Screen.SIZE[Y]:
            return False
        else:
            return True

    @staticmethod
    def Pol2Cart(cylpos):
        # transform an array or list of shape:
        # [r1, phi1]    [x1,y1]
        # [r2, phi2] -> [x2,y2]
        # [r3, phi3]    [x3,y3]
        if type(cylpos) == list:
            return [np.array([np.cos(pos[PHI]), np.sin(pos[PHI])])*pos[R] for pos in cylpos]
        elif type(cylpos) == np.ndarray:
            if cylpos.ndim == 1:
                return np.array([np.cos(cylpos[PHI]), np.sin(cylpos[PHI])])*cylpos[R]

            r = np.ndarray(cylpos.shape)
            r[:,X] = cylpos[:,R]
            r[:,Y] = cylpos[:,R]

            retarray = np.ndarray(cylpos.shape)
            retarray[:,X] = np.cos(cylpos[:,PHI])
            retarray[:,Y] = np.sin(cylpos[:,PHI])
            return retarray*r

    @staticmethod
    def GridDist(mapposA,mapposB):
        return (mapposA[0] - mapposB[0]) + (mapposA[1] - mapposB[1])
