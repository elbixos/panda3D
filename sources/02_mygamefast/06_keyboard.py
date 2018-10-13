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

        # performance (to be masked later by fog) and view:
        self.maxdistance = 400
        self.camLens.setFar(self.maxdistance)
        self.camLens.setFov(60)

        self.taskMgr.add(self.updateTask, "update")
        self.keyboardSetup()
        self.speed = 10.0


    def updateTask(self, task):
        self.updatePlayer()
        self.updateCamera()

        return task.cont

    def keyboardSetup(self):


        self.accept("escape", sys.exit)

        base.disableMouse() # or updateCamera will fail!



    def setKey(self, key, value):
        self.keyMap[key] = value


    def updateCamera(self):
        # see issue content for how we calculated these:
        self.camera.setPos(self.player, 25.6225, 3.8807, 10.2779)
        self.camera.setHpr(self.player,94.8996,-16.6549,1.55508)

    def updatePlayer(self):
        # Global Clock
        # by default, panda runs as fast as it can frame to frame
        scalefactor = (globalClock.getDt()*self.speed)
        climbfactor = scalefactor * 0.5
        bankfactor = scalefactor
        speedfactor = scalefactor * 2.9

        self.player.setX(self.player,-speedfactor)

app = MyApp()
app.run()
