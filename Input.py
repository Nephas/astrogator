"""Author: Marco Fink"""

import random as rd

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


class Input:
    """General Mouse and Keyboard input handler"""

    def __init__(self, main):
        """Init"""
        self.main = main
        pg.key.set_repeat(200, 50)

    def HandleKey(self, keyname):
        """Key Handling by key string name"""
        if keyname == "escape":
            pg.event.post(pg.event.Event(pg.QUIT))
        elif keyname == "p":
            pg.event.post(pg.event.Event(pg.DEBUG))
        elif keyname == "space":
            pg.event.post(pg.event.Event(pg.PAUSE))
        elif keyname == "r":
            self.main.Generate(rd.randint(0, 2**16))

        elif keyname == "2":
            self.main.stepsize *= 2
        elif keyname == "1":
            self.main.stepsize *= 0.5
        elif keyname == "+":
            self.main.screen.Zoom()
        elif keyname == "-":
            self.main.screen.Zoom(False)
        elif keyname == "tab":
            i = self.main.world.system.index(self.main.screen.refsystem)
            self.main.world.changeFocus(
                self.main.world.system[(i + 1) % len(self.main.world.system)])
        elif keyname == "left shift":
            i = self.main.world.system.index(self.main.screen.refsystem)
            self.main.world.changeFocus(self.main.world.system[i - 1])

        elif keyname == "right":
            self.main.screen.playership.pointing[PHI] += 0.1
        elif keyname == "left":
            self.main.screen.playership.pointing[PHI] -= 0.1
        elif keyname == "down":
            self.main.screen.playership.thrust -= 0.001
        elif keyname == "up":
            self.main.screen.playership.thrust += 0.001
        elif keyname == "#":
            self.main.screen.playership.thrust = 0.0
        elif keyname == "c":
            self.main.screen.playership.circularize(self.main.screen.refbody)

    def HandleMouse(self, button, pos):
        """Mouse Handling"""
        if button == 4:
            self.main.screen.Zoom(False)
        elif button == 5:
            self.main.screen.Zoom()
        elif button == 1:
            mappos = self.main.screen.Screen2Map(
                np.array(pos), self.main.world.time)
            self.main.world.changeFocus(self.main.world.getClosest(mappos))
