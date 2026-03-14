import abstract
from resourceManager import ResourceManager
import components
import pygame
from debugLogger import DebugLogger

class Switch(abstract.Object, abstract.Observable):
    def __init__(self, pos, is_pressed=False, interact_range=50, target_object=None, graphic_group=None, light_group=None, **kwargs):
        graphic_group = graphic_group or []
        light_group = light_group or []
        abstract.Object.__init__(self, "switch", pos)
        abstract.Observable.__init__(self)
        self.is_pressed = is_pressed
        self.interact_range = interact_range
        self.target = target_object
        self.already_pressed = False
        self.atlas = ResourceManager.getAtlas("interruptor")
        self.graphic = components.Graphic(self, self.atlas)
        
        self.graphic.add(graphic_group)
        
        self.graphic.addState("switch-off", [0]) 
        self.graphic.addState("switch-on", [1])
        self.graphic.setState("switch-off") 
        self.interact_range = 50
        
        if self.is_pressed:
            self.graphic.setState("switch-on")
        else:
            self.graphic.setState("switch-off")
        DebugLogger.log("Switch init: pos=%s is_pressed=%s interact_range=%s",
                        pos, is_pressed, self.interact_range)


    def update(self, dt, player_pos):
        self.graphic.update(dt)
        
        p_vec = pygame.Vector2(player_pos)
        s_vec = pygame.Vector2(self.pos.topleft)
        distance = s_vec.distance_to(p_vec)

        keys = pygame.key.get_pressed()
        
        # de momento se pulsa una tecla para encenderlo hasta que se implemente la luz (que es lo que debería activar el interruptor) 
        if distance < self.interact_range and keys[pygame.K_e]:
            if not self.already_pressed:
                self.toggle() 
                self.already_pressed = True 
        else:
            self.already_pressed = False

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