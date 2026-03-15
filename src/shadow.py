import pygame
import abstract
from components import ChasePlayer, PatrolBehavior, Graphic, Movement
from resourceManager import ResourceManager
from debugLogger import DebugLogger
class Shadow(abstract.Object):
    def __init__(self, pos, name="shadow", graphic_group=None, **kwargs):
        super().__init__(name, pos)
        self.speed    = float(kwargs.get("speed", 0.05))
        vision_range  = int(kwargs.get("vision_range", 100))
        self.move_vec  = pygame.math.Vector2(pos)
        self.behavior = ChasePlayer(vision_range=vision_range)
        self.patrol = PatrolBehavior(patrol_range=100)
        self.move = Movement(self, speed=self.speed)
        self._player_pos = None
        self._damage_cooldown = 0
        self.atlas = ResourceManager.getAtlas("shadow")
        self.graphic = Graphic(self, self.atlas)
        self.graphic.add(graphic_group)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        DebugLogger.log("Shadow init: name=%s pos=%s speed=%s vision_range=%d",
                        name, pos, self.speed, vision_range)

    def on_collision(self, other):
     self._player_pos = other.pos.topleft
     if self._damage_cooldown <= 0:
          other.health.take_damage(1)
          self._damage_cooldown = 1000 

    def update(self, dt, player_pos=None, map=None):
     if self._damage_cooldown > 0:
        self._damage_cooldown -= dt
     if map:
        self._map = map
     if player_pos:
        self._player_pos = player_pos
    
     if self._player_pos:
        dist = pygame.math.Vector2(self.pos.center).distance_to(
               pygame.math.Vector2(self._player_pos))
        if dist < self.behavior.vision_range:
            self.behavior.update(self, dt, self._player_pos)
        else:
            self.patrol.update(self, dt, self._player_pos)
    
     self.graphic.update(dt)


    def serialize(self):
        return {
            "pos": self.pos.topleft,
            "move_vec": (self.move_vec.x, self.move_vec.y)
        }
    
    def unserialize(self, data):
        
        if "pos" in data:
            self.pos.topleft = data["pos"]
   
        if "move_vec" in data:
            self.move_vec = pygame.math.Vector2(data["move_vec"])

