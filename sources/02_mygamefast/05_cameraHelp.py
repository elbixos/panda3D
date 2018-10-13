from direct.showbase.ShowBase import ShowBase
from direct.task import Task

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        self.player = self.loader.loadModel("alliedflanker")
        self.player.setPos(self.world,220,220,85)
        self.player.setH(self.world,90)
        self.player.reparentTo(self.render)

        self.camera.setPos(self.player, 25.6225, 3.8807, 10.2779)
        self.camera.lookAt(self.player)
        self.taskMgr.add(self.updateTask, "update")

    def updateTask(self,task):
        # 'str' simple converts the Vec3 to string we can print
        print ("POS Joueur: "+str(self.player.getPos(self.world)))
        print ("POS CAM: "+str(self.camera.getPos(self.world)))
        #print ("POS: "+str(self.camera.getPos(self.player)))
        #print ("HPR: "+str(self.camera.getHpr(self.player)))
        return Task.cont

app = MyApp()
app.run()
