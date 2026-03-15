import pygame
import abstract
from components import ChasePlayer, Graphic
from resourceManager import ResourceManager
from debugLogger import DebugLogger
class Shadow(abstract.Object):
    def __init__(self, pos, graphic_group=None, **kwargs):
        graphic_group = graphic_group 
        super().__init__("Shadow", pos)
        self.speed = 0.1
        self.move_vec = pygame.math.Vector2(pos)
        self.behavior = ChasePlayer(vision_range=400)
        # Gráficos
        self.atlas = ResourceManager.getAtlas("shadow")
        self.graphic = Graphic(self, self.atlas)
        self.graphic.add(graphic_group)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        DebugLogger.log("Shadow init: pos=%s speed=%s vision_range=%s",
                        pos, self.speed, self.behavior.vision_range)

    def update(self, dt, player_pos):
        if self.behavior:
            self.behavior.update(self, dt, player_pos)
        
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

