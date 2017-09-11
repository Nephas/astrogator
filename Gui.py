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

    def __init__(self, parent, screenpos=(0,0), size=(0,0), title = "unknown", wincol=pg.Color(32,32,32,192), headcol=pg.Color(128,128,128,192), textcol=pg.Color("white")):
        self.paren = parent
        self.screenpos = screenpos
        self.size = size
        self.color = {'window' : wincol,
                      'header' : headcol,
                      'text': textcol}

        self.surf = pg.Surface(size, flags=pg.SRCALPHA)
        self.font = pg.font.SysFont("arial", 12)
        self.linesize = self.font.get_linesize()

        self.title = title
        self.head = pg.Surface((size[X],2*self.linesize), flags=pg.SRCALPHA)
        self.head.fill(self.color['header'])
        self.head.blit(self.font.render(self.title, 1, self.color['text']), (self.linesize/2, self.linesize/2))

        self.content = []

    def FormatContent(self,text):
        pass

    def Render(self, screen):
        self.surf.fill(self.color['window'])
        self.surf.blit(self.head, (0,0))
        for i, line in enumerate(self.content):
            self.surf.blit(self.font.render(line, 1, self.color['text']), (self.linesize/2, i * self.linesize + self.linesize*3))

        screen.blit(self.surf, self.screenpos)
