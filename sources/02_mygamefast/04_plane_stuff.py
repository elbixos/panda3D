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

app = MyApp()
app.run()
