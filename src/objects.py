import pygame
from pytmx import pytmx
import abstract
import components
from resourceManager import ResourceManager


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
    def __init__(self, tmx, name="tilemap", pos=(0, 0),
                 back_group=None, front_group=None):
        super().__init__(name, pos)
        self.tmx       = ResourceManager.getTileMap(tmx)
        self.reachable = [[]]
        self._render_map(back_group, front_group)

    def update(self, dt):
        pass  # chunk sprites are updated via their sprite groups in the scene

    def _render_map(self, back_group, front_group):
        cfg        = ResourceManager.getConfig()
        scale      = cfg.getint("video", "scale")
        chunk_size = cfg.getint("engine", "chunk_size", fallback=32)
        map_w      = self.tmx.width
        map_h      = self.tmx.height
        tw         = self.tmx.tilewidth
        th         = self.tmx.tileheight
        self.reachable = [[0] * map_w for _ in range(map_h)]

        # Classify layers: "reachable" mask only; Z>0 → foreground; rest → background
        bg_layers = []
        fg_layers = []
        for layer in self.tmx.layers:
            if not isinstance(layer, pytmx.TiledTileLayer) or not layer.visible:
                continue
            if layer.name and layer.name.lower() == "reachable":
                for x, y, gid in layer:
                    props = self.tmx.get_tile_properties_by_gid(gid)
                    if props and props.get("reachable"):
                        self.reachable[y][x] = 1
                continue
            props_lower = {k.lower(): v for k, v in (layer.properties or {}).items()}
            z = int(props_lower.get("z", 0))
            if z > 0:
                fg_layers.append(layer)
            else:
                bg_layers.append(layer)

        def _build_chunks(layer_list, group):
            if not layer_list or group is None:
                return
            chunk_surfs = {}  # (cx, cy) -> Surface
            for layer in layer_list:
                for x, y, gid in layer:
                    props = self.tmx.get_tile_properties_by_gid(gid)
                    if props and props.get("reachable"):
                        self.reachable[y][x] = 1
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if not tile:
                        continue
                    cx, cy = x // chunk_size, y // chunk_size
                    lx, ly = x % chunk_size, y % chunk_size
                    key = (cx, cy)
                    if key not in chunk_surfs:
                        tx0 = cx * chunk_size
                        ty0 = cy * chunk_size
                        w_px = (min(tx0 + chunk_size, map_w) - tx0) * tw
                        h_px = (min(ty0 + chunk_size, map_h) - ty0) * th
                        chunk_surfs[key] = pygame.Surface((w_px, h_px), pygame.SRCALPHA)
                    chunk_surfs[key].blit(tile, (lx * tw, ly * th))

            for (cx, cy), surf in chunk_surfs.items():
                tx0 = cx * chunk_size
                ty0 = cy * chunk_size
                if scale != 1:
                    w_px, h_px = surf.get_size()
                    surf = pygame.transform.scale(surf, (w_px * scale, h_px * scale))
                # offset in unscaled pixels; Graphic.__init__ applies scale
                g = components.Graphic(self, None, offset=(tx0 * tw, ty0 * th))
                g.image = surf
                g.rect  = surf.get_rect()
                g.add(group)

        _build_chunks(bg_layers, back_group)
        _build_chunks(fg_layers, front_group)


class LightObject(abstract.Object):
    """Fuente de luz estática colocada desde Tiled (type='Light').
    Propiedades Tiled: atlas (str), offset_x (int), offset_y (int).
    """
    def __init__(self, pos=(0, 0), light_group=None,
                 atlas="light1", **kwargs):
        super().__init__("light_object", pos)
        self.light = components.Graphic(
            self, ResourceManager.getAtlas(atlas),
            offset=(-128, -128), primary=False
        )
        if light_group:
            self.light.add(light_group)
        self.light.addState("on", [0])
        self.light.setState("on")

    def update(self, dt):
        self.light.update(dt)

    def serialize(self):
        return {}


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