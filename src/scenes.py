import pygame
import player, objects, abstract, audio, switch, door
from resourceManager import ResourceManager
from saveManager import SaveManager
from switch import Switch
from door import Door
from shadow import Shadow
from components import ChasePlayer, Health
from healthHUD import HealthHUD

# ─────────────────────────────────────────────────────────────────────
# TestScene
# ─────────────────────────────────────────────────────────────────────
class TestScene(abstract.Scene):
    def __init__(self, game, name=None):
        super().__init__(game, name)
        self.groups = {"game": pygame.sprite.Group(), "lights": pygame.sprite.Group()}
        self.entities_dict = {}
        self.light_screen  = self.game.screen.copy()
        self.map    = objects.tileMap("TestMap")
        self.camera = objects.Camera()
        self.map.sprite.add(self.groups["game"])
        self.camera.addGroup(self.groups["game"])
        self.camera.addGroup(self.groups["lights"])
        self._load_from_tiled()
        if self.player:
            self.camera.setReference(self.player)
            self.health_hud = HealthHUD(self.player)
        #SaveManager.load(self)

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    self.player.health.take_damage(0.5)
                if event.key == pygame.K_g:      SaveManager.save(self)
                if event.key == pygame.K_ESCAPE: self.game.switchScene(PauseScene(self.game))

    def update(self, dt):
        self.player.update(dt, map=self.map.reachable)
        if self.player.health.is_dead:
            self.game.switchScene(GameOverScene(self.game))
            return
        for eid, ent in self.entities_dict.items():
            if eid != "player":
                ent.update(dt, self.player.pos.topleft)
        self.groups["game"].update(dt)
        self.groups["lights"].update(dt)
        self.camera.update(dt)

    def draw(self):
        self.light_screen.fill("grey10")
        self.game.screen.fill("black")
        self.groups["game"].draw(self.game.screen)
        self.groups["lights"].draw(self.light_screen)
        self.game.screen.blit(self.light_screen, (0, 0), special_flags=pygame.BLEND_MULT)
        if hasattr(self, 'health_hud'):
            self.health_hud.draw(self.game.screen)

    def _load_from_tiled(self):
        classes = {"Player": player.Player, "Switch": Switch, "Door": Door, "Shadow": Shadow}
        behaviors = { "chase": ChasePlayer(vision_range=400)}
        for obj in self.map.tmx.objects:
            cls = classes.get(obj.type)
            if not cls:
                continue
            if obj.type == "Shadow":
                behavior = obj.properties.get("behavior","chase")
                ent = cls(pos=(obj.x, obj.y), behavior=behaviors.get(behavior))
            else:    
             ent = cls(pos=(obj.x, obj.y), graphic_group=self.groups["game"],
                      light_group=self.groups["lights"], **obj.properties)
            eid = obj.name or str(obj.id)
            self.entities_dict[eid] = ent
            ent.graphic.add(self.groups["game"])
            if obj.type == "Player":
                self.player = ent
        for eid, ent in self.entities_dict.items():
            if not hasattr(ent, "target") or not ent.target:
                continue
            names = str(ent.target).split(",")
            ent.target_objects = []
            for name in names:
                r = self.entities_dict.get(name.strip())
                if r:
                    ent.add_observer(r)
                    ent.target_objects.append(r)
                    if len(names) == 1:
                        ent.target = r


# ─────────────────────────────────────────────────────────────────────
# MainMenu
# ─────────────────────────────────────────────────────────────────────
class MainMenu(abstract.Scene):
    def __init__(self, game, name="main_menu"):
        super().__init__(game, name)
        self.audio    = audio.SoundManager()
        self.play     = objects.TextButton("Play",     20, 50)
        self.settings = objects.TextButton("Settings", 20, 70)
        self.quit     = objects.TextButton("Quit",     20, 90)
        self.sprites  = pygame.sprite.Group(
            self.play.graphic, self.settings.graphic, self.quit.graphic)

    def update(self, dt):
        self.sprites.update(dt)
        if self.play.update(dt):     self.game.changeScene(TestScene(self.game))
        if self.settings.update(dt): self.game.switchScene(SettingsScene(self.game))
        if self.quit.update(dt):     self.game.quitGame()

    def events(self, events):
        for e in events:
            if e.type == pygame.QUIT: self.game.quitGame()

    def draw(self):
        self.game.screen.fill((255, 255, 255))
        self.sprites.draw(self.game.screen)


# ─────────────────────────────────────────────────────────────────────
# SettingsScene
# Para añadir una pestaña:
#   1. Crear clase que herede _SettingsTab
#   2. Añadir instancia a self.TABS en SettingsScene.__init__
# ─────────────────────────────────────────────────────────────────────
class _SettingsTab:
    def update(self, dt):          pass
    def events(self, events):      pass
    def draw(self, screen, s, font): pass


class _VideoTab(_SettingsTab):
    RESOLUTIONS = [(1920, 1080), (2560, 1440)]  # añade resoluciones aquí
    FPS_OPTIONS = [30, 60, 120, 144,  240, 360, 500, 1000]

    # Layout base (unidades sin escalar)
    _LX  = 20   # x etiquetas
    _VX = 60 # x del valor
    _BX  = 120   # x botón <
    _BX2 = 130  # x botón >
    _Y   = [60, 80, 100]   # y de cada fila: resolución, fullscreen, fps

    def __init__(self):
        cfg = ResourceManager.getConfig()
        cur = (cfg.getint("video", "xres"), cfg.getint("video", "yres"))
        self._res_i = next((i for i, r in enumerate(self.RESOLUTIONS) if r == cur), 0)
        self._fps_i = next((i for i, v in enumerate(self.FPS_OPTIONS)
                            if v == cfg.getint("video", "maxfps")), 0)
        self._fs = cfg.getboolean("video", "fullscreen")

        y = self._Y
        self.res_prev = objects.TextButton("<",      self._BX,  y[0])
        self.res_next = objects.TextButton(">",      self._BX2, y[0])
        self.fs_btn   = objects.TextButton("Toggle", self._BX,  y[1])
        self.fps_prev = objects.TextButton("<",      self._BX,  y[2])
        self.fps_next = objects.TextButton(">",      self._BX2, y[2])

        self.sprites = pygame.sprite.Group(
            self.res_prev.graphic, self.res_next.graphic,
            self.fs_btn.graphic,
            self.fps_prev.graphic, self.fps_next.graphic,
        )

    @property
    def resolution(self): return self.RESOLUTIONS[self._res_i]
    @property
    def fullscreen(self): return self._fs
    @property
    def maxfps(self):     return self.FPS_OPTIONS[self._fps_i]

    def update(self, dt):
        self.sprites.update(dt)
        if self.res_prev.update(dt): self._res_i = (self._res_i - 1) % len(self.RESOLUTIONS)
        if self.res_next.update(dt): self._res_i = (self._res_i + 1) % len(self.RESOLUTIONS)
        if self.fs_btn.update(dt):   self._fs    = not self._fs
        if self.fps_prev.update(dt): self._fps_i = (self._fps_i - 1) % len(self.FPS_OPTIONS)
        if self.fps_next.update(dt): self._fps_i = (self._fps_i + 1) % len(self.FPS_OPTIONS)

    def draw(self, screen, s, font):
        rows = [
            ("Resolucion", self._Y[0], f"{self.resolution[0]}x{self.resolution[1]}"),
            ("Fullscreen", self._Y[1], "On" if self._fs else "Off"),
            ("FPS max",    self._Y[2], str(self.maxfps)),
        ]
        for label, y, val in rows:
            ls = font.render(label, False, (80, 80, 80)); ls.set_colorkey(ls.get_at((0, 0)))
            vs = font.render(val,   False, (40, 40, 40)); vs.set_colorkey(vs.get_at((0, 0)))
            screen.blit(ls, (self._LX * s, y * s))
            screen.blit(vs, (self._VX * s + 12 * s, y * s))
        self.sprites.draw(screen)


class SettingsScene(abstract.Scene):
    def __init__(self, game, name="settings"):
        super().__init__(game, name)
        # scale fijado en construcción — no cambia en caliente
        self._s = ResourceManager.getConfig().getint("video", "scale")
        s = self._s

        self._video  = _VideoTab()
        self.TABS    = {"Video": self._video}
        self._active = "Video"
        self._pending = False

        # Tab buttons — espaciado horizontal de 55 unidades base
        self._tab_btns = {
            k: objects.TextButton(k, 10 + i * 60, 12)
            for i, k in enumerate(self.TABS)
        }
        self.apply = objects.TextButton("Apply", 15, 200)
        self.back  = objects.TextButton("Back",  15, 220)

        self._static_sprites = pygame.sprite.Group(
            *[b.graphic for b in self._tab_btns.values()],
            self.apply.graphic, self.back.graphic,
        )
        # Fuente para etiquetas en draw — tamaño base 7, escalado fijo
        self._font = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 7 * s)

    def _apply(self):
        cfg = ResourceManager.getConfig()
        vid = self._video
        if vid.fullscreen:
            info = pygame.display.Info()
            w, h = info.current_w, info.current_h
        else:
            w, h = vid.resolution
        rw = cfg.getint("engine", "width")
        rh = cfg.getint("engine", "height")
        # Guardar como pendiente: no se aplica al config live hasta apply_pending() en exit
        ResourceManager.set_pending("video", "xres",       str(w))
        ResourceManager.set_pending("video", "yres",       str(h))
        ResourceManager.set_pending("video", "fullscreen", "1" if vid.fullscreen else "0")
        ResourceManager.set_pending("video", "maxfps",     str(vid.maxfps))
        ResourceManager.set_pending("video", "scale",      str(min(w // rw, h // rh)))
        self._pending = True

    def update(self, dt):
        self._static_sprites.update(dt)
        self.TABS[self._active].update(dt)
        for k, btn in self._tab_btns.items():
            if btn.update(dt): self._active = k
        if self.apply.update(dt): self._apply()
        if self.back.update(dt):  self.game.quitScene()

    def events(self, events):
        for e in events:
            if e.type == pygame.QUIT: self.game.quitGame()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.quitScene()
            self.TABS[self._active].events([e])

    def draw(self):
        s = self._s  # scale fijo — no lee config en caliente
        screen = self.game.screen
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (180, 180, 180), (10 * s, 24 * s), (200 * s, 24 * s), 1)
        self.TABS[self._active].draw(screen, s, self._font)
        if self._pending:
            surf = self._font.render("Reinicia para aplicar", False, (200, 80, 80))
            surf.set_colorkey(surf.get_at((0, 0)))
            screen.blit(surf, (15 * s, 150 * s))
        self._static_sprites.draw(screen)


# ─────────────────────────────────────────────────────────────────────
# PauseScene
# ─────────────────────────────────────────────────────────────────────
class PauseScene(abstract.Scene):
    def __init__(self, game, name="pause"):
        super().__init__(game, name)
        self._parent  = game.sceneStack[-1] if game.sceneStack else None
        self.resume   = objects.TextButton("Resume",   20,  50)
        self.settings = objects.TextButton("Settings", 20,  70)
        self.quit     = objects.TextButton("Quit",     20,  90)
        self.sprites  = pygame.sprite.Group(
            self.resume.graphic, self.settings.graphic, self.quit.graphic)

    def update(self, dt):
        self.sprites.update(dt)
        if self.resume.update(dt):   self.game.quitScene()
        if self.settings.update(dt): self.game.switchScene(SettingsScene(self.game))
        if self.quit.update(dt):     self.game.changeScene(MainMenu(self.game))

    def events(self, events):
        for e in events:
            if e.type == pygame.QUIT: self.game.quitGame()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.game.quitScene()

    def draw(self):
        if self._parent: self._parent.draw()
        ov = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 120))
        self.game.screen.blit(ov, (0, 0))
        self.sprites.draw(self.game.screen)

# ─────────────────────────────────────────────────────────────────────
# Game Over Scene
# ─────────────────────────────────────────────────────────────────────

class GameOverScene(abstract.Scene):
    def __init__(self, game, name="game_over"):
        super().__init__(game, name)
        self._parent = game.sceneStack[-1] if game.sceneStack else None
        
        # Botones: Uno para reintentar y otro para salir
        self.retry = objects.TextButton("Retry", 20, 60)
        self.quit  = objects.TextButton("Main Menu", 20, 80)
        
        self.sprites = pygame.sprite.Group(self.retry.graphic, self.quit.graphic)
        self.font_big = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 30)

    def update(self, dt):
        self.sprites.update(dt)
        # Si pulsa Retry, se cambia la escena actual por una nueva TestScene
        if self.retry.update(dt): 
            self._parent.player.health.reset()
            SaveManager.load(self._parent)
            self.game.quitScene()
        # Si pulsa Quit, se vuelve al menú principal
        if self.quit.update(dt): 
            self.game.changeScene(MainMenu(self.game))

    def events(self, events):
        for e in events:
            if e.type == pygame.QUIT: self.game.quitGame()

    def draw(self):
        # Dibujamos el juego de fondo (donde murió Nix)
        if self._parent: self._parent.draw()
        
        # Capa roja semitransparente para dar efecto de muerte
        ov = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        ov.fill((150, 0, 0, 150)) # Rojo oscuro
        self.game.screen.blit(ov, (0, 0))
        
        # Título de GAME OVER
        text = self.font_big.render("GAME OVER", True, (255, 255, 255))
        self.game.screen.blit(text, (20, 20))
        
        self.sprites.draw(self.game.screen)