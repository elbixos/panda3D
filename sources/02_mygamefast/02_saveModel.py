from direct.showbase.ShowBase import ShowBase   # import the bits of panda
from panda3d.core import GeoMipTerrain          # that we need

class MyApp(ShowBase):                          # our 'class'
    def __init__(self):
        ShowBase.__init__(self)                        # initialise
        terrain = GeoMipTerrain("worldTerrain")        # create a terrain
        terrain.setHeightfield("gwadaHeight.png")        # set the height map
        terrain.setColorMap("gwadaTexture.jpg")           # set the colour map
        #terrain.setBruteforce(True)                    # level of detail
        root = terrain.getRoot()                       # capture root
        root.reparentTo(render)                        # render from root
        root.setSz(60)                                 # maximum height
        terrain.generate()                             # generate
        root.writeBamFile('world.bam')                 # create 3D model

app = MyApp()                                   # our 'object'
app.run()                                       # away we go!
