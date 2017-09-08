#! /usr/bin/env python
"""Author: Marco Fink"""

import sys

import pygame as pg

from Input import Input
from Screen import Screen
from Sector import Sector


class Main:
    """Main game class"""

    TPS = 30
    FPS = 15

    def __init__(self):
        """Main game class"""
        pg.GAMETIC = 25
        pg.RENDER = 26
        pg.GUIRENDER = 27
        pg.DEBUG = 28
        pg.PAUSE = 29

        pg.init()
        self.stepsize = 0.1             # stepsize in days/timestep, max
        self.screen = Screen(self)      # Main display Surface
        self.input = Input(self)

    def Generate(self, seed=1):
        """Generate the game world"""
        self.world = Sector(self)
        self.world.Generate()

        self.screen.RenderMap()
        self.screen.RenderAll()

    def Run(self):
        """Start the main game loop"""
        pg.event.clear()
        self.debug = False
        self.running = True

        pg.time.set_timer(pg.GAMETIC, 1000 / Main.TPS)
        pg.time.set_timer(pg.RENDER, 1000 / Main.FPS)
        pg.time.set_timer(pg.GUIRENDER, 500)

        while True:
            if self.debug:
                break
            pg.time.wait(2)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.DEBUG:
                    pg.time.set_timer(pg.GAMETIC, 0)
                    pg.time.set_timer(pg.RENDER, 0)
                    pg.time.set_timer(pg.GUIRENDER, 0)
                    self.debug = True
                elif event.type == pg.PAUSE:
                    self.running = not self.running
                    pg.time.set_timer(pg.GAMETIC, 1000 / Main.TPS * int(self.running))

                elif event.type == pg.GAMETIC:
                    self.world.Move(self.stepsize)
                elif event.type == pg.RENDER:
                    self.screen.RenderMap()
                    self.screen.RenderAll()
                elif event.type == pg.GUIRENDER:
                    self.screen.RenderGui()

                elif event.type == pg.KEYDOWN:
                    self.input.HandleKey(pg.key.name(event.key))
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.input.HandleMouse(event.button, event.pos)


main = Main()
main.Generate()
main.Run()
