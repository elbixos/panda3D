from direct.showbase.ShowBase import ShowBase
import sys

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        self.player = self.loader.loadModel("alliedflanker.egg")
        self.player.setPos(220,220,85)
        self.player.setH(90)
        self.player.reparentTo(self.render)

        self.stuff = self.loader.loadModel("camera.egg")
        self.stuff.setPos(self.player,-100,0,0)
        self.stuff.setHpr(90,-90,0)
        self.stuff.reparentTo(self.render)


        # performance (to be masked later by fog) and view:
        self.maxdistance = 400
        self.camLens.setFar(self.maxdistance)
        self.camLens.setFov(60)

        self.taskMgr.add(self.updateTask, "update")
        self.keyboardSetup()

        self.speed = 10.0
        self.maxspeed = 100.0


    def updateTask(self, task):
        self.updatePlayer()
        self.updateCamera()

        return task.cont

    def keyboardSetup(self):
        self.keyMap = {"left":0, "right":0, "climb":0, "fall":0, \
            "accelerate":0, "decelerate":0, "fire":0}

        self.accept("escape", sys.exit)

        ## Gestion Vitesse
        self.accept("a", self.setKey, ["accelerate",1])
        self.accept("a-up", self.setKey, ["accelerate",0])

        self.accept("q", self.setKey, ["decelerate",1])
        self.accept("q-up", self.setKey, ["decelerate",0])

        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])

        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_right-up", self.setKey, ["right",0])

        # self.accept(“arrow_left”, self.setKey, [“left”,1])
        # self.accept(“arrow_left-up”, self.setKey, [“left”,0])
        # self.accept(“arrow_right”, self.setKey, [“right”,1])
        # self.accept(“arrow_right-up”, self.setKey, [“right”,0])
        # self.accept(“arrow_down”, self.setKey, [“climb”,1])
        # self.accept(“arrow_down-up”, self.setKey, [“climb”,0])
        # self.accept(“arrow_up”, self.setKey, [“fall”,1])
        # self.accept(“arrow_up-up”, self.setKey, [“fall”,0])
        # self.accept(“space”, self.setKey, [“fire”,1])
        # self.accept(“space-up”, self.setKey, [“fire”,0])
        base.disableMouse() # or updateCamera will fail!



    def setKey(self, key, value):
        self.keyMap[key] = value


    def updateCamera(self):
        # see issue content for how we calculated these:
        self.camera.setPos(self.player, 25.6225, 3.8807, 10.2779)
        self.camera.lookAt(self.player)

    def updatePlayer(self):
        # Global Clock
        # by default, panda runs as fast as it can frame to frame
        scalefactor = (globalClock.getDt()*self.speed)
        climbfactor = scalefactor * 0.5
        bankfactor = scalefactor
        speedfactor = scalefactor * 2.9

        # move forwards - our X/Y is inverted, see the issue
        self.player.setX(self.player,-speedfactor)

        # throttle control
        if (self.keyMap["accelerate"]!=0):
            self.speed += 1
            if (self.speed > self.maxspeed):
                self.speed = self.maxspeed
        elif (self.keyMap["decelerate"]!=0):
            self.speed -= 1
            if (self.speed < 0.0):
                self.speed = 0.0

        # Left and Right
        if (self.keyMap["left"]!=0 and self.speed > 0.0):
            self.player.setH(self.player.getH()+bankfactor)
            self.player.setP(self.player.getP()+bankfactor)

        elif (self.keyMap["right"]!=0 and self.speed > 0.0):
            self.player.setH(self.player.getH()-bankfactor)
            self.player.setP(self.player.getP()-bankfactor)


            # quickest return:
            # if (self.player.getP() >= 180):
            #     self.player.setP(-180)
            # elif (self.keyMap[“right”]!=0 and self.speed > 0.0):
            #     self.player.setH(self.player.getH()-bankfactor)
            #     self.player.setP(self.player.getP()-bankfactor)
            #
            # if (self.player.getP() <= -180): self.player.setP(180) # autoreturn elif (self.player.getP() > 0):
            #     self.player.setP(self.player.getP()-(bankfactor+0.1))
            #
            # if (self.player.getP() < 0):
            #     self.player.setP(0)
            # elif (self.player.getP() < 0):
            #     self.player.setP(self.player.getP()+(bankfactor+0.1))
            #
            #     if (self.player.getP() > 0):
            #         self.player.setP(0)

app = MyApp()
app.run()
