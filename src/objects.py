import pygame
from pytmx import pytmx
import abstract
import components
from random import randint
from resourceManager import ResourceManager

#just a class for create a simple sprite in  a random places for testing purposes
class testTree(abstract.Object):
    def __init__(self):
        super().__init__()
        config = ResourceManager.getConfig()
        image = pygame.image.load(config.get("engine", "assets_path") + "arbol.png")
        self.pos = (randint(-100, 1000), randint(-100, 1000))
        self.atlas = ResourceManager.getAtlas("arbol")
        self.sprite = components.Graphic(self,self.atlas, False, False)
        self.sprite.addName("tree", 0,0)
        self.sprite.set("tree")

class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0,0)):
        super().__init__(name, pos)
        self.spriteGroups = list()
        size = (ResourceManager.getConfig().getint("video","xres"), ResourceManager.getConfig().getint("video","yres"))
        self.box = pygame.Rect(self.pos, size)
        print("Camera area:" + str(self.box))
        self.bounding =  self.box.scale_by(0.5, 0.5)
        print("Bound area:" + str(self.bounding))
        self.reference = None

    def addGroup(self, group:pygame.sprite.Group):
        self.spriteGroups.append(group)

    def move(self, vector):
        #move the camera
        self.pos = (self.pos[0]+ vector[0],self.pos[1]+vector[1])
        self.box.topleft = self.pos 
        self.bounding.center = self.box.center 
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.box.topleft)
                
        print("Camera moved. Amount: " + str(vector) + "Pos: " + str(self.pos) + " Box:" + str(self.box.topleft) + " bound: " + str(self.bounding.topleft))


    def setReference(self, ref:abstract.Object):
        self.reference = ref
        #initial center on the reference
        offset = (ref.pos[0] - self.box.center[0], ref.pos[1] - self.box.center[1])
        self.move(offset)

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos):
                offx = 0
                offy = 0
                if self.reference.pos[0] < self.bounding.left:
                    offx = self.reference.pos[0] - self.bounding.left
                elif self.reference.pos[0] > self.bounding.right:
                    offx = self.reference.pos[0] - self.bounding.right

                if self.reference.pos[1] < self.bounding.top:
                    offy = self.reference.pos[1] - self.bounding.top
                elif self.reference.pos[1] > self.bounding.bottom:
                    offy = self.reference.pos[1] - self.bounding.bottom
                self.move((round(offx * 0.2), round(offy * 0.2)))
            
    def draw(self, screen):
        for group in self.spriteGroups:
            group.draw(screen)

class tileMap(abstract.Object):

    def __init__(self, tmx, name="tilemap", pos=(0,0)):
        super().__init__(name, pos)
        # load and cache the TMX data
        self.tmx = ResourceManager.getTileMap(tmx)
        layers = self._render_map()
        self.sprite = components.Tile(self, layers)

    def update(self, dt):
        # forward to the sprite component so camera offsets are applied
        self.sprite.update(dt)

    # Predenderizamos el mapa completo y lo envolvemos en nuestra clase grafica
    def _render_map(self):
            # Creamos superficies del tamaño total del mapa (sin escala) para
            # optimizar; aplicaremos el escalado global de una sola vez al
            # final, igual que hacemos en Atlas.
            width = self.tmx.width * self.tmx.tilewidth
            height = self.tmx.height * self.tmx.tileheight
            layers = []

            for layer in self.tmx.visible_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                    for x, y, gid in layer:
                        tile = self.tmx.get_tile_image_by_gid(gid)
                        if tile:
                            temp_surf.blit(tile, (x * self.tmx.tilewidth,
                                                   y * self.tmx.tileheight))
                    layers.append(temp_surf)

            # ahora aplicamos la escala global a cada capa de una sola vez
            scale = ResourceManager.getConfig().getint("video", "scale")
            if scale != 1:
                scaled = []
                for layer in layers:
                    new_size = (layer.get_width() * scale,
                                layer.get_height() * scale)
                    scaled.append(pygame.transform.scale(layer, new_size))
                return scaled

            return layers

