from direct.showbase.ShowBase import ShowBase

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        self.player = self.loader.loadModel("alliedflanker.egg")
        self.player.setPos(20,20,65)
        self.player.setH(225)
        self.player.reparentTo(self.render)



app = MyApp()
app.run()
