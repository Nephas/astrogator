#! /usr/bin/env python

from globals import *

from System import System
from Sector import Sector
from Screen import Screen
from Input import Input

class Main:
    def __init__(self):
        pass

    def Init(self, seed=1):
        pg.init()

        self.stepsize = [0.1, 10]        # stepsize in days/timestep, max

        self.screen = Screen(self)      # Main display Surface
        self.input = Input(self)

#        self.world = System(self)
#        self.world.CreateRoot(seed)

        self.world = Sector(self)
        self.world.Create()

        self.world.printTerm()

#        self.screen.RenderBack()
        self.screen.RenderMap()
        self.screen.RenderAll()

    def Run(self):
        pg.event.clear()
        self.debug = False
        self.running = True

        pg.time.set_timer(pg.GAMETIC, 1000/TPS)
        pg.time.set_timer(pg.RENDER, 1000/FPS)
        pg.time.set_timer(pg.GUIRENDER, 500)

        while True:
            if self.debug: break
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
                    pg.time.set_timer(pg.GAMETIC, 1000/TPS * int(self.running))

                elif event.type == pg.GAMETIC:
                    self.world.Move(self.stepsize[0])
                elif event.type == pg.RENDER:
                    self.screen.RenderMap()
                    self.screen.RenderAll()

#                    self.screen.RenderBack()
#                    self.screen.RenderAll()
                elif event.type == pg.GUIRENDER:
                    self.screen.RenderGui()

                elif event.type == pg.KEYDOWN:
                    self.input.HandleKey(pg.key.name(event.key))
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.input.HandleMouse(event.button, event.pos)


main = Main()
main.Init()
main.Run()
