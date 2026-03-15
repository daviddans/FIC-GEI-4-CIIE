import abstract
from resourceManager import ResourceManager
import components
import pygame
from debugLogger import DebugLogger

class Switch(abstract.Object, abstract.Observable):
    def __init__(self, pos, name="switch", graphic_group=None, light_group=None, **kwargs):
        abstract.Object.__init__(self, name, pos)
        abstract.Observable.__init__(self)
        self.is_pressed = kwargs.get("is_pressed", "false").lower() == "true"
        self.target = kwargs.get("target_object", None)
        self.already_pressed = False
        self.atlas = ResourceManager.getAtlas("interruptor")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.add(graphic_group)
        self.graphic.addState("switch-off", [0])
        self.graphic.addState("switch-on", [1])
        self.graphic.setState("switch-off")

        if self.is_pressed:
            self.graphic.setState("switch-on")
        else:
            self.graphic.setState("switch-off")
        DebugLogger.log("Switch init: name=%s pos=%s is_pressed=%s", name, pos, self.is_pressed)


    def on_collision(self, _other):
        if pygame.key.get_pressed()[pygame.K_e] and not self.already_pressed:
            self.toggle()
            self.already_pressed = True

    def update(self, dt):
        if not pygame.key.get_pressed()[pygame.K_e]:
            self.already_pressed = False
        self.graphic.update(dt)

    def toggle(self):
        self.is_pressed = not self.is_pressed
        
        if self.is_pressed:
            self.graphic.setState("switch-on")
            DebugLogger.log("Interruptor encendido")
            self.notify(self, 'SWITCH_ON')
        else:
            self.graphic.setState("switch-off")
            DebugLogger.log("Interruptor apagado")
            self.notify(self, 'SWITCH_OFF')

    def serialize(self): 
        return {"is_pressed": self.is_pressed}

    def unserialize(self, data):
        self.is_pressed = data["is_pressed"]
        if self.is_pressed: self.graphic.setState("switch-on")
        else: self.graphic.setState("switch-off")  