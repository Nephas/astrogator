#! /usr/bin/env python

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

        pg.GAMETIC = 25
        pg.BACKRENDER = 26
        pg.GUIRENDER = 27

        self.TPS = 30
        self.FPS = 15

        pg.time.set_timer(pg.GAMETIC, 1000/self.TPS)
        pg.time.set_timer(pg.BACKRENDER, 1000/self.FPS)
        pg.time.set_timer(pg.GUIRENDER, 500)

        self.focus = 0
        self.stepsize = [0.1, 10]        # stepsize in days/timestep, max

        self.screen = Screen(self)      # Main display Surface
        self.world = System(self,self)
        self.world.Create()
        self.world.Move(self.stepsize[0])
        self.world.printTerm(" ")

    def Loop(self):
        while True:
            pg.time.wait(2)
#            t=tic()
            for i, event in enumerate(pg.event.get()):
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.GAMETIC:
                    self.world.Move(self.stepsize[0])
                    self.screen.RenderMap()
                    self.screen.RenderAll()
                elif event.type == pg.BACKRENDER:
                    self.screen.RenderBack()
                    self.screen.RenderAll()
                elif event.type == pg.GUIRENDER:
                    self.screen.RenderGui()

                elif event.type == pg.KEYDOWN:
                    print(pg.key.name(event.key))
                    self.HandleKey(pg.key.name(event.key))
                elif event.type == pg.MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
#            toc(t)


    def HandleKey(self, keyname):
        if keyname == "escape":
            pg.event.post(pg.event.Event(QUIT))
        elif keyname == "2":
            self.stepsize[0] *= 2
        elif keyname == "1":
            self.stepsize[0] *= 0.5
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
        elif keyname == "p":
            self.togglePotential()
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


main = Main()
main.Loop()
