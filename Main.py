import os, sys, time
import pygame as pg
import numpy as np
import random as rd
import math
from pygame.locals import *
from globals import *

from System import System


class Main:
    def __init__(self):
        self.tstart = time.time()
        pg.init()
        pg.key.set_repeat(200,50)
        self.focus = 0
        self.time = 0           # time in seconds
        self.stepsize = [0.1, 10]       # stepsize in days/timestep, max
        self.ticsize = 0.05      # length of game tic in seconds

        self.screen = Screen(self)    # Main display Surface
        self.world = System(self)
        self.world.Create()

    def Loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    print(pg.key.name(event.key))
                    self.HandleKey(pg.key.name(event.key))
                elif event.type == pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
            if self.TimeStep():
                if self.stepsize[0] > self.stepsize[MAX]:
                    self.stepsize[0] = self.stepsize[MAX]
                self.world.Move(self.stepsize[0])
                print("%.1f"%self.world.time +" days - stepsize: "+str(self.stepsize[0]/self.ticsize)+" days/sec")
            self.screen.RenderAll()


    def HandleKey(self, keyname):
        if keyname == "escape":
            pg.event.post(pg.event.Event(QUIT))
        elif keyname == "2":
            self.stepsize[0] *= 2
            print(str(self.stepsize[0]/self.ticsize)+" days/sec")
        elif keyname == "1":
            self.stepsize[0] *= 0.5
            print(str(self.stepsize[0]/self.ticsize)+" days/sec")
        elif keyname == "+":
            self.screen.mapscale *= 2.
            self.screen.starscale *= 5./4
            self.screen.planetscale *= 5./4
            self.screen.moonscale *= 5./4
        elif keyname == "-":
            self.screen.mapscale *= 0.5
            self.screen.starscale *= 4./5
            self.screen.planetscale *= 4./5
            self.screen.moonscale *= 4./5

        elif keyname == "right":
            self.world.ship[0].orientation += 0.2
        elif keyname == "left":
            self.world.ship[0].orientation -= 0.2
        elif keyname == "down":
            self.world.ship[0].mapvel += 0.001*self.world.ship[0].pointing
        elif keyname == "up":
            self.world.ship[0].mapvel -= 0.001*self.world.ship[0].pointing
        elif keyname == "tab":
            self.focus += 1
            if self.focus >= len(self.world.body):
                self.focus = 0
        elif keyname == "left shift":
            self.focus -= 1
            if self.focus < 0:
                self.focus = len(self.world.body)-1

        elif keyname == "r":
            self.world = System(self)
            self.world.Create()

    def TimeStep(self):
        newTime = time.time() - self.tstart
        if newTime < self.time + self.ticsize:
            return False
        else:
            self.time = newTime
            return True


main = Main()
main.Loop()
