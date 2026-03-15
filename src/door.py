import abstract
from resourceManager import ResourceManager
import components
import pygame
from debugLogger import DebugLogger

class Door(abstract.Object, abstract.Observer):
    def __init__(self, pos, name="door", graphic_group=None, light_group=None, **kwargs):
        super().__init__(name, pos)

        self.is_locked = kwargs.get("is_locked", "true").lower() == "true"
        self.is_open = False
        
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
        DebugLogger.log("Door init: name=%s pos=%s is_locked=%s", name, pos, self.is_locked)

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

    def on_collision(self, other):
        if not self.is_locked and not self.is_open:
            self.open_door()

    def update(self, dt):
        self.graphic.update(dt)

    def open_door(self):
        self.is_open = True
        self.graphic.animate = True
        self.graphic.setState("opening")
        DebugLogger.log("Puerta abierta por proximidad.")

    def close_door(self):
        self.is_open = False
        self.graphic.animate = False
        self.graphic.setState("unlocked") 
        print("Puerta cerrada.")