from panda3d.core import Vec3
from direct.task import Task
from pandac.PandaModules import VBase3

class AlliedFlanker():
    def __init__(self,loader,scenegraph,taskMgr):
        self.loader = loader
        self.render = scenegraph
        self.taskMgr = taskMgr
        self.maxspeed = 200.0
        self.speed = 0
        self.startPos = Vec3(200,200,100)
        self.startHpr = Vec3(225,0,0)
        self.player = self.loader.loadModel("volume1/models/alliedflanker")
        self.player.setScale(.2,.2,.2)
        self.player.reparentTo(self.render)
        self.reset()
        self.calculate()

        # load the explosion ring
        self.explosionModel = self.loader.loadModel('volume1/models/explosion')
        self.explosionModel.reparentTo(self.render)
        self.explosionModel.setScale(0.0)
        self.explosionModel.setLightOff()
        # only one explosion at a time:
        self.exploding = False
        self.maxdistance = 400 # default in case below never called

    def setMaxHeight(self,distance):
        """ Maximum flying altitude """
        self.maxdistance = distance

    def reset(self):
        """ Back to start position, orientation, speed """
        self.player.show()
        self.player.setPos(self.startPos)
        self.player.setHpr(self.startHpr)
        self.speed = self.maxspeed/5

    def calculate(self):
        """ Should be called every frame.
        It calculates how the player should move (position and orientation) """
        self.factor = globalClock.getDt()
        self.scalefactor = self.factor *self.speed
        self.climbfactor = self.scalefactor * 0.3
        self.bankfactor  = self.scalefactor
        self.speedfactor = self.scalefactor * 2.9
        self.gravityfactor = ((self.maxspeed-self.speed)/100.0)*1.35

    # note the collision enhancements
    def climb(self):
        if (self.speed > 0):
            # faster you go, quicker you climb
            self.player.setFluidZ(self.player.getZ()+self.climbfactor)
            self.player.setR(self.player.getR()+(0.5*self.climbfactor))
            # quickest return: (avoids uncoil/unwind)
            if (self.player.getR() >= 180):
                self.player.setR(-180)

    def dive(self):
        if (self.speed > 0):
            self.player.setFluidZ(self.player.getZ()-self.climbfactor)
            self.player.setR(self.player.getR()-(0.5*self.climbfactor))
            # quickest return:
            if (self.player.getR() <= -180):
                self.player.setR(180)

    def unwindVertical(self):
        """ Used to return the aircraft to its default orientation, it would
        look odd after a climb/fall if the plane stayed pointed up/down! """
        if (self.player.getR() > 0):
                self.player.setR(self.player.getR()-(self.climbfactor+0.1))
                if (self.player.getR() < 0):
                    self.player.setR(0) # avoid jitter
        elif (self.player.getR() < 0):
                self.player.setR(self.player.getR()+(self.climbfactor+0.1))
                if (self.player.getR() > 0):
                    self.player.setR(0)

    def bankLeft(self):
        if (self.speed > 0):
            self.player.setH(self.player.getH()+self.bankfactor)
            self.player.setP(self.player.getP()+self.bankfactor)
            # quickest return:
            if (self.player.getP() >= 180):
                self.player.setP(-180)

    def bankRight(self):
        if (self.speed > 0):
            self.player.setH(self.player.getH()-self.bankfactor)
            self.player.setP(self.player.getP()-self.bankfactor)
            if (self.player.getP() <= -180):
                self.player.setP(180)

    def unwindHorizontal(self):
        """ Used to return the aircraft to its default orientation,
        it would look odd after banking if the plane stayed tilted! """
        if (self.player.getP() > 0):
                self.player.setP(self.player.getP()-(self.bankfactor+0.1))
                if (self.player.getP() < 0):
                    self.player.setP(0)
        elif (self.player.getP() < 0):
                self.player.setP(self.player.getP()+(self.bankfactor+0.1))
                if (self.player.getP() > 0):
                    self.player.setP(0)

    def move(self,boundingBox):
        # move forwards - our X/Y is inverted, see the issue
        valid = True
        if self.exploding == False:
            self.player.setFluidX(self.player,-self.speedfactor)
            valid = self.__inBounds(boundingBox)
            self.player.setFluidZ(self.player,-self.gravityfactor)
        return valid

    def __inBounds(self,boundingBox):
        if (self.player.getZ() > self.maxdistance):
            self.player.setZ(self.maxdistance)
        elif (self.player.getZ() < 0):
            self.player.setZ(0)

        # and now the X/Y world boundaries:
        valid = True
        if (self.player.getX() < 0):
            self.player.setX(0)
            valid = False
        elif (self.player.getX() > boundingBox):
            self.player.setX(boundingBox)
            valid = False
        if (self.player.getY() < 0):
            self.player.setY(0)
            valid = False
        elif (self.player.getY() > boundingBox):
            self.player.setY(boundingBox)
            valid = False
        return valid

    def accelerate(self):
        self.speed += 1
        if (self.speed > self.maxspeed):
            self.speed = self.maxspeed

    def brake(self):
        self.speed -= 1
        if (self.speed < 0.0):
            self.speed = 0.0

    def die(self):
        if (self.exploding == False):
            self.player.setZ(self.player.getZ()+10)
            self.exploding = True
            self.explosionModel.setPosHpr(Vec3(self.player.getX(),self.player.getY(), \
                                   self.player.getZ()),Vec3( self.player.getH(),0,0))
            self.player.hide()
            self.taskMgr.add(self.__expandExplosion,'expandExplosion')

    def __expandExplosion(self,Task):
        # expand the explosion ring each frame until a certain size
        if self.explosionModel.getScale( ) < VBase3( 60.0, 60.0, 60.0 ):
            scale = self.explosionModel.getScale()
            scale = scale + VBase3( self.factor*40, self.factor*40, self.factor*40 )
            self.explosionModel.setScale(scale)
            return Task.cont
        else:
            self.explosionModel.setScale(0)
            self.exploding = False
            self.reset()
            # and it stops the task

    def __speedAsPercentage(self):
        # needed for camera trick
        return (self.speed/self.maxspeed)

    def attach(self,node):
        return self.player.attachNewNode(node)

    # See Issue 5 video for what this does:
    def lookAtMe(self,camera):
        percent = (self.__speedAsPercentage())*2
        camera.setPos(self.player, 9+(20*percent), 0, 0)
        # compensate for model problem (see Issue 3)
        camera.setH(self.player.getH()+90)
        camera.setP(self.player.getR())
        camera.setR(self.player.getP())
        # final adjustments
        camera.setZ(self.player,3)
        camera.setY(self.player,1.5)
