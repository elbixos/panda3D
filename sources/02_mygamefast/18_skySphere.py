from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.LerpInterval import LerpTexOffsetInterval, LerpPosInterval
from pandac.PandaModules import CompassEffect, CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionSphere, CollisionHandlerQueue, Material
from pandac.PandaModules import VBase4, VBase3, TransparencyAttrib
from panda3d.core import AmbientLight, DirectionalLight, Vec4, Vec3, Fog, Point3
from panda3d.core import BitMask32, Texture, TextNode, TextureStage
from panda3d.core import NodePath, PandaNode
from direct.gui.OnscreenText import OnscreenText
import sys


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.debug = True
        self.statusLabel = self.makeStatusLabel(0)
        self.collisionLabel = self.makeStatusLabel(1)


        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)




        self.maxspeed = 100.0
        # Avion à la pointe des chateaux, direction Ouest !
        self.startPos = Vec3(1200,320,85)
        #print (self.startPos)
        self.startHpr = Vec3(0,0,0)
        #self.player.setPos(1200,320,85)
        #self.player.setH(0)
        self.player = self.loader.loadModel("alliedflanker.egg")
        #self.player.setPos(640,640,85)
        self.player.setScale(0.2,0.2,0.2)
        self.player.reparentTo(self.render)
        self.resetPlayer()

        # load the explosion ring
        self.explosionModel = loader.loadModel('explosion')
        self.explosionModel.reparentTo(self.render)
        self.explosionModel.setScale(0.0)
        self.explosionModel.setLightOff()
        # only one explosion at a time:
        self.exploding = False


        # performance (to be masked later by fog) and view:
        self.maxdistance = 1200
        self.camLens.setFar(self.maxdistance)
        self.camLens.setFov(60)

        self.taskMgr.add(self.updateTask, "update")
        self.keyboardSetup()




        # relevant for world boundaries
        self.worldsize = 1024

        self.createEnvironment()

        self.setupCollisions()
        self.textCounter = 0

        base.oobe()

    def resetPlayer(self):
        self.player.show()
        #self.player.setPos(self.world,self.startPos)
        #self.player.setHpr(self.world,self.startHpr)
        self.player.setPos(self.startPos)
        self.player.setHpr(self.startHpr)
        self.speed = 10.0
        #self.speed = self.maxspeed/2

        #print (self.player.getPos())


    def makeStatusLabel(self, i):
        return OnscreenText(style=2, fg=(.5,1,.5,1), pos=(-1.3,0.92-(.08 * i)), \
		align=TextNode.ALeft, scale = .08, mayChange = 1)


    def updateTask(self, task):
        self.updatePlayer()
        self.updateCamera()

        self.collTrav.traverse(self.render)
        for i in range(self.playerGroundHandler.getNumEntries()):
            entry = self.playerGroundHandler.getEntry(i)
            if (self.debug == True):
                self.collisionLabel.setText("DEAD:"+str(globalClock.getFrameTime()))
            if (self.exploding == False):
                self.player.setZ(entry.getSurfacePoint(self.render).getZ()+10)
                self.explosionSequence()
            # we will later deal with 'what to do' when the player dies

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

        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])


        self.accept("arrow_down", self.setKey, ["climb",1])
        self.accept("arrow_down-up", self.setKey, ["climb",0])

        self.accept("arrow_up", self.setKey, ["fall",1])
        self.accept("arrow_up-up", self.setKey, ["fall",0])

        # self.accept(“space”, self.setKey, [“fire”,1])
        # self.accept(“space-up”, self.setKey, [“fire”,0])
        base.disableMouse() # or updateCamera will fail!



    def setKey(self, key, value):
        self.keyMap[key] = value


    def updateCamera(self):
        # see issue content for how we calculated these:
        percent = (self.speed/self.maxspeed)
        self.camera.setPos(self.player, 19.6225+(10*percent), 3.8807, 10.2779)
        self.camera.setHpr(self.player,94.8996,-12.6549, 1.55508)
        # see issue content for how we calculated these:
        #self.camera.setPos(self.player, 25.6225, 3.8807, 10.2779)
        #self.camera.setPos(0, 0, 90)
        #self.camera.setHpr(self.player,94.8996,-16.6549,1.55508)

    def updatePlayer(self):
        # Global Clock
        # by default, panda runs as fast as it can frame to frame
        scalefactor = (globalClock.getDt()*self.speed)
        #climbfactor = scalefactor * 0.5
        #bankfactor = scalefactor
        #speedfactor = scalefactor * 2.9
        climbfactor = scalefactor * 0.5 *2
        bankfactor = scalefactor *2.0
        speedfactor = scalefactor * 2.9

        gravityfactor = ((self.maxspeed-self.speed)/100.0)*2.0


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
            if (self.player.getP() >= 180):
                self.player.setP(-180)

        elif (self.keyMap["right"]!=0 and self.speed > 0.0):
            self.player.setH(self.player.getH()-bankfactor)
            self.player.setP(self.player.getP()-bankfactor)
            if (self.player.getP() <= -180):
                self.player.setP(180)

        elif (self.player.getP() > 0): # autoreturn from right
            self.player.setP(self.player.getP()-(bankfactor+0.1))
            if (self.player.getP() < 0): self.player.setP(0)

        elif (self.player.getP() < 0): # autoreturn from left
            self.player.setP(self.player.getP()+(bankfactor+0.1))
            if (self.player.getP() > 0):
                self.player.setP(0)

        # Climb and Fall
        if (self.keyMap["climb"]!=0 and self.speed > 0.00):
            # faster you go, quicker you climb
            self.player.setZ(self.player.getZ()+climbfactor)
            self.player.setR(self.player.getR()+climbfactor)
            if (self.player.getR() >= 180):
                self.player.setR(-180)

        elif (self.keyMap["fall"]!=0 and self.speed > 0.00):
            self.player.setZ(self.player.getZ()-climbfactor)
            self.player.setR(self.player.getR()-climbfactor)
            if (self.player.getR() <= -180):
                self.player.setR(180)


        elif (self.player.getR() > 0): # autoreturn from up
            self.player.setR(self.player.getR()-(climbfactor+0.1))
            if (self.player.getR() < 0):
                self.player.setR(0)
        # avoid jitter
        elif (self.player.getR() < 0): # autoreturn from down
            self.player.setR(self.player.getR()+(climbfactor+0.1))
            if (self.player.getR() > 0):
                self.player.setR(0)

        # move forwards - our X/Y is inverted, see the issue
        if self.exploding == False:
            self.player.setX(self.player,-speedfactor)
            self.applyBoundaries()
            self.player.setZ(self.player,-gravityfactor)


    def createEnvironment(self):
        # Fog to hide a performance tweak:
        colour = (0.5,0.5,0.5)
        expfog = Fog("scene-wide-fog")
        expfog.setColor(*colour)
        expfog.setExpDensity(0.002) # original : 0.004
        render.setFog(expfog)
        base.setBackgroundColor(*colour)

        # Our sky
        skysphere = self.loader.loadModel('blue-sky-sphere')
        skysphere.setEffect(CompassEffect.make(self.render))
        skysphere.setScale(0.08)

        # NOT render or you'll fly through the sky!:
        skysphere.reparentTo(self.camera)

        # Our lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.6, .6, .6, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))

        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setColor(VBase4(0.8, 0.8, 0.5, 1))
        dlnp = self.render.attachNewNode(directionalLight)
        dlnp.setPos(0,0,260)
        dlnp.lookAt(self.player)
        self.render.setLight(dlnp)

        # water
        self.water = self.loader.loadModel('square.egg')
        self.water.setSx(self.worldsize*2)
        self.water.setSy(self.worldsize*2)
        self.water.setPos(self.worldsize/2,self.worldsize/2,25) # sea level
        self.water.setTransparency(TransparencyAttrib.MAlpha)
        newTS = TextureStage('1')
        self.water.setTexture(newTS,self.loader.loadTexture('water.png'))
        self.water.setTexScale(newTS,4)
        self.water.reparentTo(self.render)
        LerpTexOffsetInterval(self.water,200,(1,0),(0,0), textureStage=newTS).loop()

    def setupCollisions(self):
        self.collTrav = CollisionTraverser()

        self.playerGroundSphere = CollisionSphere(0,1.5,-1.5,1.5)
        self.playerGroundCol = CollisionNode('playerSphere')
        self.playerGroundCol.addSolid(self.playerGroundSphere)

        # bitmasks
        self.playerGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.playerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.world.setCollideMask(BitMask32.bit(0))

        # and done
        self.playerGroundColNp = self.player.attachNewNode(self.playerGroundCol)
        self.playerGroundHandler = CollisionHandlerQueue()
        self.collTrav.addCollider(self.playerGroundColNp, self.playerGroundHandler)

        # DEBUG
        if (self.debug == True):
            #self.playerGroundColNp.show()
            self.collTrav.showCollisions(self.render)

    def applyBoundaries(self):
        if (self.player.getZ() > self.maxdistance):
            self.player.setZ(self.maxdistance)
        # should never happen once we add collision, but in case:
        elif (self.player.getZ() < 0):
            self.player.setZ(0)

        # and now the X/Y world boundaries:
        boundary = False
        if (self.player.getX() < 0):
            self.player.setX(0)
            boundary = True
        elif (self.player.getX() > self.worldsize):
            self.player.setX(self.worldsize)
            boundary = True
        if (self.player.getY() < 0):
            self.player.setY(0)
            boundary = True
        elif (self.player.getY() > self.worldsize):
            self.player.setY(self.worldsize)
            boundary = True

        # lets not be doing this every frame...
        if boundary == True and self.textCounter > 30:
            self.statusLabel.setText("STATUS: MAP END; TURN AROUND")
        elif self.textCounter > 30:
            self.statusLabel.setText("STATUS: OK")

        if self.textCounter > 30:
            self.textCounter = 0
        else:
            self.textCounter = self.textCounter + 1

    def explosionSequence(self):
        self.exploding = True
        self.explosionModel.setPosHpr( Vec3(self.player.getX(),self.player.getY(), \
                               self.player.getZ()), Vec3( self.player.getH(),0,0))
        self.player.hide()
        taskMgr.add( self.expandExplosion, 'expandExplosion' )

    def expandExplosion( self, Task ):
        # expand the explosion rign each frame until a certain size
        if self.explosionModel.getScale( ) < VBase3( 60.0, 60.0, 60.0 ):
            factor = globalClock.getDt()
            scale = self.explosionModel.getScale()
            scale = scale + VBase3( factor*40, factor*40, factor*40 )
            self.explosionModel.setScale(scale)
            return Task.cont
        else:
            self.explosionModel.setScale(0)
            self.exploding = False
            self.resetPlayer()
            # and it stops the task

app = MyApp()
app.run()
