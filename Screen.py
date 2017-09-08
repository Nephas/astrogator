"""Author: Marco Fink"""

import numpy as np
import pygame as pg

R = 0
PHI = 1
X = 0
Y = 1
A = 0
B = 1
MIN = 0
MAX = 1


class Screen:
    """The pygame Screen handler with main rendering and screen coordinate transformations"""

    SIZE = np.array([1024, 768])
    SYSTEMTHRESHOLD = 0.1
    PLANETTHRESHOLD = 500

    GRAV = 2
    TRAIL = 1
    BODY = 0

    def __init__(self, main):
        self.main = main
        self.display = pg.display.set_mode(Screen.SIZE)

        self.back = pg.Surface(Screen.SIZE)
        self.back.fill(pg.Color("black"))

        self.map = [pg.Surface(Screen.SIZE, flags=pg.SRCALPHA)] * 3
        self.gui = pg.Surface(Screen.SIZE, flags=pg.SRCALPHA)
        self.font = pg.font.SysFont("Arial", 12)

        self.offset = 0.5 * Screen.SIZE
        self.mapscale = 50  # px/AU
        self.starscale = 0.1
        self.planetscale = 0.01

        self.refbody = None

    def RenderAll(self, gui=False):
        self.display.blit(self.back, (0, 0))
        for layer in self.map:
            self.display.blit(layer, (0, 0))
        self.display.blit(self.gui, (0, 0))

        pg.display.flip()

    def RenderMap(self):
        for layer in self.map:
            layer.fill(pg.Color(0, 0, 0, 0))
        self.main.world.Draw(self)

    def RenderGui(self):
        self.gui.fill(pg.Color(0, 0, 0, 0))
        linecolor = pg.Color("white")
        linecolor.a = 50

        pg.draw.line(self.gui, linecolor, (Screen.SIZE[X] / 2, 0), (Screen.SIZE[X] / 2, Screen.SIZE[Y]))
        pg.draw.line(self.gui, linecolor, (0, Screen.SIZE[Y] / 2), (Screen.SIZE[X], Screen.SIZE[Y] / 2))

        info = ["Time-step: " + str(self.main.stepsize) + " days/tick",
                "Time: " + str(self.main.world.time) + " days",
                "Mapscale: " + str(self.mapscale),
                "Planetscale: " + str(self.planetscale),
                self.refbody.name,
                str(self.refbody.mass)]

        for i, line in enumerate(info):
            self.gui.blit(self.font.render(line, 1, pg.Color("white")), (10, i * 20 + 10))

    # Coordinate transformation from mapspace to screenspace
    def Map2Screen(self, mappos, time=0):
        screenpos = Screen.SIZE / 2. + self.mapscale * (mappos - self.refbody.MapPos(time))
        return screenpos.astype(int)

    # Coordinate transformation from mapspace to screenspace
    def Screen2Map(self, screenpos, time=0):
        mappos = (screenpos - Screen.SIZE / 2.) / self.mapscale + self.refbody.MapPos(time)
        return mappos

    def Zoom(self, closer=True):
        if closer and self.mapscale >= 1000000:
            return
        if not closer and self.mapscale <= 1e-05:
            return

        mapFactor = 2.
        objectFactor = 5. / 4.
        if not closer:
            mapFactor = 1. / mapFactor
            objectFactor = 1. / objectFactor

        self.mapscale *= mapFactor
        self.starscale *= objectFactor
        self.planetscale *= objectFactor

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
            return [np.array([np.cos(pos[PHI]), np.sin(pos[PHI])]) * pos[R] for pos in cylpos]
        elif type(cylpos) == np.ndarray:
            if cylpos.ndim == 1:
                return np.array([np.cos(cylpos[PHI]), np.sin(cylpos[PHI])]) * cylpos[R]

            r = np.ndarray(cylpos.shape)
            r[:, X] = cylpos[:, R]
            r[:, Y] = cylpos[:, R]

            retarray = np.ndarray(cylpos.shape)
            retarray[:, X] = np.cos(cylpos[:, PHI])
            retarray[:, Y] = np.sin(cylpos[:, PHI])
            return retarray * r

    @staticmethod
    def GridDist(mapposA, mapposB):
        return (mapposA[0] - mapposB[0]) + (mapposA[1] - mapposB[1])

    @staticmethod
    def colorSurface(image, color):
        arr = pg.surfarray.pixels3d(image.copy()).astype(float)

        arr[:, :, 0] *= color.r / 255.
        arr[:, :, 1] *= color.g / 255.
        arr[:, :, 2] *= color.b / 255.

        surf = pg.surfarray.make_surface(arr).convert_alpha()
        alpha = pg.surfarray.pixels_alpha(surf)
        alpha[:, :] = pg.surfarray.array_alpha(image)
        return surf

    @staticmethod
    def ColorBrightness(color, factor=1):
        arr = np.array(color.normalize())
        arr[0:3] *= factor
        arr *= 255
        arr = map(lambda x: min(x, 255), arr.astype(int))
        return pg.Color(*arr)
