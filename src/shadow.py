import pygame
import abstract
import components
from resourceManager import ResourceManager

# Hereda de abstract.Object para que sea compatible con tu motor
class Shadow(abstract.Object):
    def __init__(self, pos, player, **kwargs):
        # Usamos el constructor de la clase base
        super().__init__("Shadow", pos)
        self.player = player 
        
        # IA y stats
        self.move_vec = pygame.math.Vector2(pos)
        self.speed = 0.1 # Bajamos la velocidad, 1.2 es muchísimo para el dt que manejas
        self.damage = 0.5 
        
        # Gráficos
        self.atlas = ResourceManager.getAtlas("ShadowTrooper")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.addState("idle", [0]) 
        self.graphic.setState("idle") 

    def update(self, dt):
        # Persecución suave
        target = pygame.math.Vector2(self.player.pos.center)
        current = pygame.math.Vector2(self.pos.topleft)
        
        direction = target - current
        distance = direction.length()

        if 5 < distance < 300: # Rango de visión
            direction.normalize_ip()
            self.move_vec += direction * self.speed * dt
            
        # Actualizamos la posición física (self.pos es el Rect de abstract.Object)
        self.pos.topleft = (self.move_vec.x, self.move_vec.y)

    def draw(self, surface):
        # Este método ahora es compatible con lo que espera tu Cámara
        self.graphic.draw(surface)