import pygame
from pytmx import pytmx
import abstract
import components
from random import randint
from resourceManager import ResourceManager


class testTree(abstract.Object):
    def __init__(self):
        super().__init__()
        self.pos.topleft = (randint(-100, 1000), randint(-100, 1000))
        self.atlas = ResourceManager.getAtlas("arbol")
        self.sprite = components.Graphic(self, self.atlas)
        self.sprite.addState("tree", [0])
        self.sprite.setState("tree")


class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0, 0)):
        super().__init__(name, pos)
        cfg = ResourceManager.getConfig()
        self.spriteGroups = []
        self.pos.size = (cfg.getint("video", "xres"), cfg.getint("video", "yres"))
        self.bounding  = self.pos.scale_by(0.2, 0.2)
        self.reference = None

    def addGroup(self, group):
        self.spriteGroups.append(group)

    def setReference(self, ref):
        self.reference = ref
        self.pos.center = (ref.pos[0], ref.pos[1])
        self.bounding.center = self.pos.center
        self._notify()

    def update(self, dt):
        if self.reference and not self.bounding.collidepoint(self.reference.pos.topleft):
            self._move(self.reference.pos.topleft)

    def _move(self, target):
        max_dist = (self.pos.w ** 2 + self.pos.h ** 2) / 4
        v = pygame.math.Vector2(target)
        strength = pygame.math.clamp(1 - v.distance_squared_to(self.pos.center) / max_dist * 0.2, 0.5, 1)
        v = v.lerp(self.pos.center, strength)
        self.pos.center = (v.x, v.y)
        self.bounding.center = self.pos.center
        self._notify()

    def _notify(self):
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.pos.topleft)


class tileMap(abstract.Object):
    def __init__(self, tmx, name="tilemap", pos=(0, 0), groups=[]):
        super().__init__(name, pos)
        self.tmx       = ResourceManager.getTileMap(tmx)
        self.reachable = [[]]
        self.sprite    = components.Graphic(self, None)
        self.sprite.image = self._render_map()
        self.sprite.rect  = self.sprite.image.get_rect()

    def update(self, dt):
        self.sprite.update(dt)

    def _render_map(self):
        cfg       = ResourceManager.getConfig()
        tile_size = cfg.getint("engine", "tile_size")
        scale     = cfg.getint("video", "scale")
        w = self.tmx.width  * tile_size
        h = self.tmx.height * tile_size
        self.reachable = [[0] * self.tmx.width for _ in range(self.tmx.height)]
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for layer in self.tmx.layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.visible:
                for x, y, gid in layer:
                    props = self.tmx.get_tile_properties_by_gid(gid)
                    if props and props.get("reachable"):
                        self.reachable[y][x] = 1
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:
                        surf.blit(tile, (x * self.tmx.tilewidth, y * self.tmx.tileheight))
        if scale != 1:
            surf = pygame.transform.scale(surf, (w * scale, h * scale))
        return surf


class TextButton(abstract.Object):
    """
    Boton de texto para menus.
    - x, y, font_size en unidades BASE. Scale se aplica internamente.
    - Para animar: asigna un atlas y usa addState/setState en self.graphic.
    """
    def __init__(self, label: str, x: int, y: int,
                 font_size: int = 8,
                 font_name: str = "CaskaydiaCoveNerdFont-Regular.ttf"):
        super().__init__("text_button", (x, y))
        s    = ResourceManager.getConfig().getint("video", "scale")
        font = ResourceManager.getFont(font_name, font_size * s)
        surf = font.render(label, False, (80, 80, 80))
        surf.set_colorkey(surf.get_at((0, 0)))
        self.graphic       = components.Graphic(self, None)
        self.graphic.image = surf
        self.graphic.rect  = surf.get_rect(topleft=self.pos.topleft)
        self._clicked      = False

    def update(self, dt) -> bool:
        self.graphic.update(dt)
        pressed = pygame.mouse.get_pressed()[0]
        if self.graphic.rect.collidepoint(pygame.mouse.get_pos()):
            if pressed and not self._clicked:
                self._clicked = True
                return True
        if not pressed:
            self._clicked = False
        return False

    def events(self, events):   pass
    def draw(self):             pass
    def serialize(self):        return {}
    def unserialize(self, d):   pass


class TextInput(abstract.Object):
    """
    Campo de texto editable.
    - Llama handle_event(event) desde Scene.events().
    - x, y, font_size en unidades BASE.
    """
    BLINK_MS = 500

    def __init__(self, initial: str, x: int, y: int,
                 font_size: int = 8, max_chars: int = 10,
                 font_name: str = "CaskaydiaCoveNerdFont-Regular.ttf"):
        super().__init__("text_input", (x, y))
        s            = ResourceManager.getConfig().getint("video", "scale")
        self._font   = ResourceManager.getFont(font_name, font_size * s)
        self._max    = max_chars
        self._active = False
        self._blink  = 0
        self._show   = True
        self.value   = initial
        self.graphic = components.Graphic(self, None)
        self._render()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._active = self.graphic.rect.collidepoint(event.pos)
        if not self._active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self._active = False
            elif len(self.value) < self._max and event.unicode.isprintable():
                self.value += event.unicode
            self._render()

    def update(self, dt):
        self.graphic.update(dt)
        self._blink += dt
        if self._blink >= self.BLINK_MS:
            self._blink = 0
            self._show  = not self._show
            self._render()

    def _render(self):
        display = (self.value + "|") if self._active and self._show else self.value
        if not display:
            display = " "
        color = (40, 40, 40) if self._active else (120, 120, 120)
        surf  = self._font.render(display, False, color)
        surf.set_colorkey(surf.get_at((0, 0)))
        self.graphic.image = surf
        self.graphic.rect  = surf.get_rect(topleft=self.pos.topleft)

    def events(self, events):   pass
    def draw(self):             pass
    def serialize(self):        return {"value": self.value}
    def unserialize(self, d):   self.value = d["value"]; self._render()