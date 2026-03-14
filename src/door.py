import abstract
from resourceManager import ResourceManager
import components
import pygame
from debugLogger import DebugLogger

class Door(abstract.Object, abstract.Observer):
    def __init__(self, pos, is_locked=True, proximity_range=80, graphic_group=None, light_group=None, **kwargs):
        graphic_group = graphic_group or []
        light_group = light_group or []
        super().__init__("door", pos)
        
        self.is_locked = is_locked
        self.is_open = False
        self.proximity_range = proximity_range # Distancia para que se abra sola
        
        self.atlas = ResourceManager.getAtlas("puerta")
        self.graphic = components.Graphic(self, self.atlas)
        
       
        self.graphic.add(graphic_group)
        self.graphic.addState("locked", [0])   
        self.graphic.addState("unlocked", [1])  
        self.graphic.addState("opening", [2,3])   
        
        # Estado inicial
        if self.is_locked:
            self.graphic.setState("locked")
        else:
            self.graphic.setState("unlocked")
        DebugLogger.log("Door init: pos=%s is_locked=%s proximity_range=%s",
                        pos, is_locked, proximity_range)

    def on_notify(self, entity, event):
        if event == 'SWITCH_ON':
            self.unlock()
            DebugLogger.log("Puerta desbloqueada (evento SWITCH_ON)")
        elif event == 'SWITCH_OFF':
            self.lock()
            DebugLogger.log("Puerta bloqueada (evento SWITCH_OFF)")

    def unlock(self):
        self.is_locked = False
        self.graphic.setState("unlocked")
       

    def lock(self):
        self.is_locked = True
        self.is_open = False
        self.graphic.setState("locked")

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
        self.graphic.setState("opening") # Pasa del frame 2 al 3
        DebugLogger.log("Puerta abierta por proximidad.")

    def close_door(self):
        self.is_open = False
        self.graphic.animate = False
        self.graphic.setState("unlocked") # Vuelve al frame 1 (cerrada pero sin candado)
        DebugLogger.log("Puerta cerrada.")

    def serialize(self):
        return {"is_locked": self.is_locked}

    def unserialize(self, data):
        self.is_locked = data["is_locked"]
        if self.is_locked: self.graphic.setState("locked")
        else: self.graphic.setState("unlocked")
