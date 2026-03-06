import abstract
from resourceManager import ResourceManager
import components
import pygame

class Door(abstract.Object):
    def __init__(self, pos, is_locked=True):
        super().__init__("door", pos)
        
        self.is_locked = is_locked
        self.is_open = False
        self.proximity_range = 80 # Distancia para que se abra dsola
        
        self.atlas = ResourceManager.getAtlas("puerta")
        self.graphic = components.Graphic(self, self.atlas, animate=False, loop=False)
        
        self.graphic.addName("locked", 0, 0)   
        self.graphic.addName("unlocked", 1, 1)  
        self.graphic.addName("opening", 2, 3)   
        
        # Estado inicial
        if self.is_locked:
            self.graphic.set("locked")
        else:
            self.graphic.set("unlocked")

    def unlock(self):
        self.is_locked = False
        self.graphic.set("unlocked")
       

    def lock(self):
        self.is_locked = True
        self.is_open = False
        self.graphic.set("locked")

    def update(self, dt, player_pos):
        self.graphic.update(dt)
        if self.is_locked:
            return

        # Se calcula la distancia al jugador
        p_vec = pygame.Vector2(player_pos)
        d_vec = pygame.Vector2(self.pos)
        distance = d_vec.distance_to(p_vec)

        if distance < self.proximity_range:
            if not self.is_open:
                self.open_door()
        else:
            if self.is_open:
                self.close_door()

    def open_door(self):
        self.is_open = True
        self.graphic.animate = True 
        self.graphic.loop = False
        self.graphic.set("opening") # Pasa del frame 2 al 3
        print("Puerta abierta por proximidad.")

    def close_door(self):
        self.is_open = False
        self.graphic.animate = False
        self.graphic.set("unlocked") # Vuelve al frame 1 (cerrada pero sin candado)
        print("Puerta cerrada.")