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
        self.sprite = components.Graphic(self,self.atlas, False)
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
    """An object representing a tiled map loaded from a TMX file.

    The constructor pre-renders each visible tile layer into a surface and
    then constructs a :class:`components.TileMap` sprite component that is used
    for drawing.  The object itself holds the raw ``tmx`` data and a list of
    layer surfaces in ``layers`` in case gameplay logic needs to inspect
    individual layers later (for example, to build collision geometry).

    The important behavioural change compared to the earlier implementation is
    that ``tileMap.sprite`` now behaves just like the ``graphic`` or ``sprite``
    components attached to other objects; it can be added to a
    ``pygame.sprite.Group`` and will automatically receive ``update`` and
    ``cameraUpdate`` calls as the camera moves.  A convenience helper
    ``addToGroup()`` is provided for symmetry with ``components.Graphic``.
    """

    def __init__(self, tmx, name="tilemap", pos=(0,0)):
        super().__init__(name, pos)
        # load and cache the TMX data
        self.tmx = ResourceManager.getTileMap(tmx)
        # render each layer into a surface and remember the list
        self.layers = self._render_map()
        # wrap the surfaces with a sprite component so the map can be
        # added to sprite groups just like any other object graphic
        self.sprite = components.TileMap(self, self.layers)
        # provide the same convenience API as other objects: update the
        # internal sprite when the map is updated and a helper to insert the
        # map into groups.

    def update(self, dt):
        # forward to the sprite component so camera offsets are applied
        self.sprite.update(dt)

    def addToGroup(self, group: pygame.sprite.Group):
        """Shortcut for ``group.add(self.sprite)``; mirrors the behaviour
        of :class:`components.Graphic.add` when you call
        ``some_object.graphic.add(group)``.
        """
        group.add(self.sprite)

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

