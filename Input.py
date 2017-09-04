
from globals import *



class Input:
    def __init__(self, main):
        self.main = main
        pg.key.set_repeat(200,50)

    def HandleKey(self, keyname):
        if keyname == "escape":
            pg.event.post(pg.event.Event(pg.QUIT))
        elif keyname == "p":
            pg.event.post(pg.event.Event(pg.DEBUG))
        elif keyname == "space":
            pg.event.post(pg.event.Event(pg.PAUSE))
        elif keyname == "r":
            self.main.Init(rd.randint(0,2**16))

        elif keyname == "2":
            self.main.stepsize[0] *= 2
        elif keyname == "1":
            self.main.stepsize[0] *= 0.5
        elif keyname == "+":
            self.main.screen.Zoom()
        elif keyname == "-":
            self.main.screen.Zoom(False)
        elif keyname == "tab":
            self.main.screen.refbody = rd.choice(self.main.world.body)
        elif keyname == "left shift":
            self.main.screen.refbody = rd.choice(self.main.world.body)


        # elif keyname == "right":
        #     self.main.world.ship[0].orientation += 0.2
        # elif keyname == "left":
        #     self.main.world.ship[0].orientation -= 0.2
        # elif keyname == "down":
        #     self.main.world.ship[0].mapvel += 0.001*self.main.world.ship[0].pointing
        # elif keyname == "up":
        #     self.main.world.ship[0].mapvel -= 0.001*self.main.world.ship[0].pointing


    def HandleMouse(self, button, pos):

        if button == 4:
            self.main.screen.Zoom(False)
        elif button == 5:
            self.main.screen.Zoom()
        elif button == 1:
            mappos = self.main.screen.Screen2Map(np.array(pos),self.main.world.time)
            self.main.screen.refbody = self.main.world.getClosest(mappos)
