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
        self.pos.topleft = (randint(-100, 1000), randint(-100, 1000))
        self.atlas = ResourceManager.getAtlas("arbol")
        self.sprite = components.Graphic(self,self.atlas)
        self.sprite.addState("tree", [0])
        self.sprite.setState("tree")

class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0,0)):
        super().__init__(name, pos)
        self.spriteGroups = list()
        self.pos.size = (ResourceManager.getConfig().getint("video","xres"), ResourceManager.getConfig().getint("video","yres"))
        self.bounding =  self.pos.scale_by(0.2, 0.2)
        self.reference = None

    def addGroup(self, group:pygame.sprite.Group):
        self.spriteGroups.append(group)

    def moveCamera(self, target):
        #Calculamos la fueza con la que se tiene que mover la camara teninendo en cuenta la distancia maxima de la pantalla. (Utilizamos la distancia cuadrada pa ir mas rapido)
        max_distance = (self.pos.size[0] ** 2 +  self.pos.size[1]**2)  / 4 # <- Un objeto se puede alejar como mucho la mitad de la diagonal. Como empleamos el cuadrado pues entre 4
        vector = pygame.math.Vector2(target)
        strength = vector.distance_squared_to(self.pos.center) / max_distance
        strength = pygame.math.clamp((1 - strength * 0.2), 0.5, 1) # Hacemos un clamp para que no pete con un minimo para que no se aproxime infinitamente
        vector = vector.lerp(self.pos.center, strength) # 1 -> Se queda en el centro de la camara, 0 -> se queda en la posicion target
        self.pos.center = (vector.x, vector.y)
        self.bounding.center = self.pos.center
        print(f"Actuall: {self.pos.center} GOAL: {vector} TARGET: {target}")
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.pos.topleft)
                


    def setReference(self, ref:abstract.Object):
        self.reference = ref
        #initial center on the reference
        self.pos.center = (ref.pos[0], ref.pos[1])
        self.bounding.center = self.pos.center
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.pos.topleft)

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos.topleft):
                self.moveCamera(self.reference.pos.topleft)

class tileMap(abstract.Object):

    def __init__(self, tmx, name="tilemap", pos=(0,0)):
        super().__init__(name, pos)
        # load and cache the TMX data
        self.tmx = ResourceManager.getTileMap(tmx)
        self.reachable = [[]]
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

