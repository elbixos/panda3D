from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos


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
        self.stuff.setPos(self.player,0,0,10)
        self.stuff.setHpr(90,-90,0)
        self.stuff.reparentTo(self.render)



        # performance (to be masked later by fog) and view:
        self.maxdistance = 400
        self.camLens.setFar(self.maxdistance)
        self.camLens.setFov(60)

        base.disableMouse() # or updateCamera will fail!
        self.updateCamera()

    def updateCamera(self):
        # see issue content for how we calculated these:
        self.camera.setPos(self.player, 25.6225, 3.8807, 10.2779)
        self.camera.setHpr(self.player,94.8996,-16.6549,1.55508)

app = MyApp()
app.run()
