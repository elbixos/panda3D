from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import CollisionTraverser, CollisionNode
from pandac.PandaModules import CollisionSphere, CollisionHandlerQueue
from panda3d.core import BitMask32, TextNode
from panda3d.core import NodePath, PandaNode
from direct.gui.OnscreenText import OnscreenText
import sys
from environment import GameWorld
from player import AlliedFlanker

class ArcadeFlightGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.debug = False
        self.maxdistance = 400
        self.statusLabel = self.makeStatusLabel(0)
        self.collisionLabel = self.makeStatusLabel(1)

        self.player = AlliedFlanker(self.loader,self.render,self.taskMgr)
        self.world = GameWorld(1024,self.loader,self.render,self.camera)

        self.taskMgr.add(self.updateTask, "update")
        self.keyboardSetup()

        # performance and map to player so can't fly beyond visible terrain
        self.player.setMaxHeight(self.maxdistance)

        if self.debug == False:
            self.camLens.setFar(self.maxdistance)
        else:
            base.oobe()

        self.camLens.setFov(60)
        self.setupCollisions()
        self.textCounter = 0

    def makeStatusLabel(self, i):
        """ Create a status label at the top-left of the screen,
        Parameter 'i' is the row number """
        return OnscreenText(style=2, fg=(.5,1,.5,1), pos=(-1.3,0.92-(.08 * i)), \
                               align=TextNode.ALeft, scale = .08, mayChange = 1)

    def keyboardSetup(self):
        self.keyMap = {"left":0, "right":0, "climb":0, "fall":0, \
                        "accelerate":0, "decelerate":0, "fire":0}
        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["accelerate",1])
        self.accept("a-up", self.setKey, ["accelerate",0])
        self.accept("z", self.setKey, ["decelerate",1])
        self.accept("z-up", self.setKey, ["decelerate",0])
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_down", self.setKey, ["climb",1])
        self.accept("arrow_down-up", self.setKey, ["climb",0])
        self.accept("arrow_up", self.setKey, ["fall",1])
        self.accept("arrow_up-up", self.setKey, ["fall",0])
        self.accept("space", self.setKey, ["fire",1])
        self.accept("space-up", self.setKey, ["fire",0])
        base.disableMouse() # or updateCamera will fail!

    def setKey(self, key, value):
        """ Used by keyboard setup """
        self.keyMap[key] = value

    def setupCollisions(self):
        self.collTrav = CollisionTraverser()

        # rapid collisions detected using below plus FLUID pos
        self.collTrav.setRespectPrevTransform(True)

        self.playerGroundSphere = CollisionSphere(0,1.5,-1.5,1.5)
        self.playerGroundCol = CollisionNode('playerSphere')
        self.playerGroundCol.addSolid(self.playerGroundSphere)

        # bitmasks
        self.playerGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.playerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.world.setGroundMask(BitMask32.bit(0))
        self.world.setWaterMask(BitMask32.bit(0))

        # and done
        self.playerGroundColNp = self.player.attach(self.playerGroundCol)
        self.playerGroundHandler = CollisionHandlerQueue()
        self.collTrav.addCollider(self.playerGroundColNp, self.playerGroundHandler)

        # DEBUG as per video:
        if (self.debug == True):
            self.playerGroundColNp.show()
            self.collTrav.showCollisions(self.render)

    def updateTask(self, task):
        """ Gets added to the task manager, updates the player, deals with inputs,
        collisions, game logic etc. """
        self.player.calculate()
        self.actionInput()
        validMove = self.player.move(self.world.getSize())

        # lets not be doing this every frame...
        if validMove == False and self.textCounter > 30:
            self.statusLabel.setText("STATUS: MAP END; TURN AROUND")
        elif self.textCounter > 30:
            self.statusLabel.setText("STATUS: OK")
        if self.textCounter > 30:
            self.textCounter = 0
        else:
            self.textCounter = self.textCounter + 1
        self.updateCamera()

        self.collTrav.traverse(self.render)
        for i in range(self.playerGroundHandler.getNumEntries()):
            entry = self.playerGroundHandler.getEntry(i)
            if (self.debug == True):
                self.collisionLabel.setText("DEAD:"+str(globalClock.getFrameTime()))
            self.player.die()
        return Task.cont

    def actionInput(self):
        """ Used by updateTask to process keyboard input """
        if (self.keyMap["climb"]!=0):
            self.player.climb()
        elif (self.keyMap["fall"]!=0):
            self.player.dive()
        else:
            self.player.unwindVertical()

        if (self.keyMap["left"]!=0):
            self.player.bankLeft()
        elif (self.keyMap["right"]!=0):
            self.player.bankRight()
        else:
            self.player.unwindHorizontal()

        if (self.keyMap["accelerate"]!=0):
            self.player.accelerate()
        elif (self.keyMap["decelerate"]!=0):
            self.player.brake()

    def updateCamera(self):
        self.player.lookAtMe(self.camera)
