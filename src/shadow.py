import pygame
import abstract
import components
from resourceManager import ResourceManager
class Shadow(abstract.Object):
    def __init__(self, pos, behavior, **kwargs):
        super().__init__("Shadow", pos)
        self.behavior = behavior # Aquí guardamos el ChasePlayer que viene de Tiled
        self.speed = 0.1
        self.move_vec = pygame.math.Vector2(pos)
        
        # Gráficos
        self.atlas = ResourceManager.getAtlas("shadow")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")

    def update(self, dt, player_pos):
        if self.behavior:
            self.behavior.update(self, dt, player_pos)
        
        self.graphic.update(dt)

