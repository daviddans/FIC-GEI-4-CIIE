import abstract
from resourceManager import ResourceManager
import components
import pygame
from debugLogger import DebugLogger

class Door(abstract.Object, abstract.Observer):
    def __init__(self, pos, graphic_group=None, light_group=None, **kwargs):
        super().__init__("door", pos)
        
        # Aseguramos que is_locked sea booleano
        is_locked_val = kwargs.get("is_locked", "True")
        self.is_locked = str(is_locked_val).lower() == "true"
        
        self.is_open = False
        self.key_required = kwargs.get("key_required", None) 
        
        # Rango de interacción (si no viene de Tiled, 60 píxeles)
        self.proximity_range = int(kwargs.get("proximity_range", 200))
        
        self.atlas = ResourceManager.getAtlas("puerta")
        self.graphic = components.Graphic(self, self.atlas)
        if graphic_group:
            self.graphic.add(graphic_group)

        self.graphic.addState("locked", [0])   
        self.graphic.addState("unlocked", [1])  
        self.graphic.addState("opening", [2,3])   
        
        # Estado inicial visual
        if self.is_locked:
            self.graphic.setState("locked")
        else:
            self.graphic.setState("unlocked")

    def on_notify(self, entity, event):
        if event == 'SWITCH_ON' or event == 'KEY_PICKED':
            self.unlock()
        elif event == 'SWITCH_OFF':
            self.lock()

    def unlock(self):
        if self.is_locked:
            self.is_locked = False
            self.graphic.setState("unlocked")
            print(f"Puerta desbloqueada. Ya puedes pulsar 'O' para abrir.")

    def lock(self):
        self.is_locked = True
        self.is_open = False
        self.graphic.setState("locked")

    def update(self, dt, player_pos, player_keys=[]):
     self.graphic.update(dt)

     p_vec = pygame.Vector2(player_pos)
     d_vec = pygame.Vector2(self.pos.center)
     distance = d_vec.distance_to(p_vec)

     keys = pygame.key.get_pressed()

     if distance < self.proximity_range:
        if keys[pygame.K_o] and not self.is_open:
            if self.is_locked:
                if self.key_required and self.key_required in player_keys:
                    player_keys.remove(self.key_required)
                    self.unlock()
                    self.open_door()
                elif not self.key_required:
                    self.unlock()
                    self.open_door()
                else:
                    print(f"Necesitas la llave: {self.key_required}")
            else:
                self.open_door()
     else:
        if self.is_open:
            self.close_door()

    def open_door(self):
        self.is_open = True
        self.graphic.animate = True 
        self.graphic.loop = False
        self.graphic.setState("opening")
        print("Abriendo puerta...")

    def close_door(self):
        self.is_open = False
        self.graphic.animate = False
        self.graphic.setState("unlocked") 
        print("Puerta cerrada.")