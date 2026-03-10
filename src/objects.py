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
        self.pos.topleft = (randint(-100, 1000), randint(-100, 1000))
        self.atlas = ResourceManager.getAtlas("arbol")
        self.sprite = components.Graphic(self,self.atlas)
        self.sprite.addState("tree", [0])
        self.sprite.setState("tree")

class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0,0)):
        super().__init__(name, pos)
        self.spriteGroups = list()
        size = (ResourceManager.getConfig().getint("video","xres"), ResourceManager.getConfig().getint("video","yres"))
        self.box = pygame.Rect(self.pos.topleft, size) # AL emplear un rect en la posicion esto es redundandte NEEDFIX
        print("Camera area:" + str(self.box))
        self.bounding =  self.box.scale_by(0.2, 0.2)
        print("Bound area:" + str(self.bounding))
        self.reference = None

    def addGroup(self, group:pygame.sprite.Group):
        self.spriteGroups.append(group)

    def moveCamera(self, target, strength=1):
        #move the camera    
        DEFAUTL_STRENGTH = 0.9
        vector = pygame.math.Vector2(target)
        vector = vector.smoothstep(self.box.center, pygame.math.clamp(DEFAUTL_STRENGTH*strength, 0, 1))
        self.box.center = (vector.x, vector.y)
        self.bounding.center = self.box.center
        self.pos = self.box.topleft

        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.box.topleft)
                
        #print("Camera moved. Target: " + str(target) + "Pos: " + str(self.pos) + " Box:" + str(self.box.topleft) + " bound: " + str(self.bounding.topleft))


    def setReference(self, ref:abstract.Object):
        self.reference = ref
        #initial center on the reference
        self.box.center = (ref.pos[0], ref.pos[1])
        self.bounding.center = self.box.center
        self.pos = self.box.topleft
        #print("Camera reference set to: " + str(ref.name) + " at pos: " + str(ref.pos))
        #print("Camera pos: " + str(self.pos) + " Box:" + str(self.box.topleft) + " bound: " + str(self.bounding.topleft) + "center: " + str(self.box.center))
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.box.topleft)

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos.topleft):
                #Recalcular la fuerza del movimiento en funcion de la tasa de fotogramas
                strength = (dt/1000) * ResourceManager.getConfig().getint("video", "maxfps")
                self.moveCamera(self.reference.pos.topleft, round(strength))
            
    def draw(self, screen):
        for group in self.spriteGroups:
            group.draw(screen)

class tileMap(abstract.Object):

    def __init__(self, tmx, name="tilemap", pos=(0,0)):
        super().__init__(name, pos)
        # load and cache the TMX data
        self.tmx = ResourceManager.getTileMap(tmx)
        self.reachable = [[]]
        layers = self._render_map()
        self.sprite = components.Tile(self, layers)
        print(self.reachable)

    def update(self, dt):
        # forward to the sprite component so camera offsets are applied
        self.sprite.update(dt)

    # Predenderizamos el mapa completo y lo envolvemos en nuestra clase grafica
    def _render_map(self):
            # Creamos superficies del tamaño total del mapa (sin escala) para
            # optimizar; aplicaremos el escalado global de una sola vez al
            # final, igual que hacemos en Atlas.
            tile_size = ResourceManager.getConfig().getint("engine", "tile_size")
            width = self.tmx.width * tile_size
            height = self.tmx.height * tile_size
            layers = []
            self.reachable = [[0 for x in range(self.tmx.width)] for y in range(self.tmx.height)]

            for layer in self.tmx.layers:
                if (isinstance(layer, pytmx.TiledTileLayer) and layer.visible):
                    temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                    for x, y, gid in layer:
                        props = self.tmx.get_tile_properties_by_gid(gid)
                        if props and props.get("reachable"):
                            self.reachable[y][x] = 1
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

