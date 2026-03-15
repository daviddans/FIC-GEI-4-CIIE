import pygame
import abstract
import components
from resourceManager import ResourceManager
from debugLogger import DebugLogger


class Portal(abstract.Object, abstract.Observable, abstract.Observer):
    _FADE_SPEED = 255  # alpha/segundo 

    def __init__(self, pos, graphic_group=None, light_group=None,
                 trigger_group=None, width=0, height=0, target=None, **kwargs):
        abstract.Object.__init__(self, "portal", pos)
        abstract.Observable.__init__(self)
        abstract.Observer.__init__(self)
        scale = ResourceManager.getConfig().getint("video", "scale")
        self.pos.width = int(float(width) * scale)
        self.pos.height = int(float(height) * scale)
        self.target = target.strip('"') if isinstance(target, str) else target
        self.cooldown = False
        self._fade = None           # None | "out" | "teleport" | "in"
        self._alpha = 0.0
        self._trigger = components.Graphic(self,None) #Overrided graphich to not show anything. We just want a sprite to collide with
        self._trigger.rect = self.pos.copy()
        self._trigger.image = pygame.surface.Surface((0,0))
        if trigger_group:
            self._trigger.add(trigger_group)
        DebugLogger.log("Portal init: pos=%s target=%s", self.pos, target)

    @property
    def is_active(self):
        return self._fade is not None

    def activate(self):
        self._fade = "out"
        self._alpha = 0.0
        if isinstance(self.target, Portal):
            self.target.cooldown = True

    def update(self, dt, player):
        if self._fade == "out":
            self._alpha = min(255.0, self._alpha + self._FADE_SPEED * dt / 1000)
            if self._alpha >= 255:
                self._fade = "teleport"
        elif self._fade == "teleport":
            player.pos.topleft = self.target.pos.topleft
            self._fade = "in"
        elif self._fade == "in":
            self._alpha = max(0.0, self._alpha - self._FADE_SPEED * dt / 1000)
            if self._alpha <= 0:
                self._fade = None

    def draw(self, screen):
        if self._fade is None:
            return
        surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        surf.fill((0, 0, 0, int(self._alpha)))
        screen.blit(surf, (0, 0))

    def on_notify(self, entity, event):
        if event == "collision_enter":
            if not self.cooldown and isinstance(self.target, Portal):
                DebugLogger.log("Portal activate: triggered by '%s'", getattr(entity, "name", "?"))
                self.activate()
            else:
                DebugLogger.log("Portal collision_enter IGNORED: cooldown=%s target=%s",
                                self.cooldown, type(self.target).__name__)
        elif event == "collision_exit":
            DebugLogger.log("Portal collision_exit: cooldown cleared")
            self.cooldown = False
        else:
            self.activate()