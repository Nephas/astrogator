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

class Window:
    """Basic Planet class"""

    def __init__(self, parent, screenpos=np.array([0,0]), size=np.array([0,0]), title = "unknown", color=pg.Color("white"), textcol=pg.Color("black")):
        self.paren = parent
        self.screenpos = screenpos
        self.size = size
        self.color = color
        self.textcol = textcol

        self.surf = pg.Surface(size, flags=pg.SRCALPHA)
        self.font = pg.font.SysFont("Arial", 12)

        self.title = title
        self.content = []

        self.Render()

    def FormatContent(self,text):
        pass

    def Render(self):
        self.surf.blit(self.font.render(self.title, 1, self.textcol), (10, 10))
        self.surf.fill(self.color)

    def Draw(self, screen):
        screen.blit(self.surf, self.screenpos)
