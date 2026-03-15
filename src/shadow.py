import pygame
import abstract
from components import ChasePlayer, Graphic
from resourceManager import ResourceManager
from debugLogger import DebugLogger
class Shadow(abstract.Object):
    def __init__(self, pos, name="shadow", graphic_group=None, **kwargs):
        super().__init__(name, pos)
        self.speed    = float(kwargs.get("speed", 0.01))
        vision_range  = int(kwargs.get("vision_range", 700))
        self.move_vec  = pygame.math.Vector2(pos)
        self.behavior  = ChasePlayer(vision_range=vision_range)
        self._player_pos = None
        self.atlas = ResourceManager.getAtlas("shadow")
        self.graphic = Graphic(self, self.atlas)
        self.graphic.add(graphic_group)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        DebugLogger.log("Shadow init: name=%s pos=%s speed=%s vision_range=%d",
                        name, pos, self.speed, vision_range)

    def on_collision(self, other):
        self._player_pos = other.pos.topleft
        other.health.take_damage(1)

    def update(self, dt):
        if self.behavior and self._player_pos:
            self.behavior.update(self, dt, self._player_pos)
        self._player_pos = None
        self.graphic.update(dt)


    def serialize(self):
        return {
            "pos": self.pos.topleft,
            "move_vec": (self.move_vec.x, self.move_vec.y)
        }
    
    def unserialize(self, data):
        # se recupera la posicion del rect
        if "pos" in data:
            self.pos.topleft = data["pos"]
        # se recupera el vector para mantener la fisica 
        if "move_vec" in data:
            self.move_vec = pygame.math.Vector2(data["move_vec"])

