import abstract
from resourceManager import ResourceManager
import components
import pygame

class Switch(abstract.Object, abstract.Observable):
    def __init__(self, pos, target_object=None):
        abstract.Object.__init__(self, "switch", pos)
        abstract.Observable.__init__(self)
        self.is_pressed = False 
        self.target = target_object
        self.atlas = ResourceManager.getAtlas("interruptor")
        self.graphic = components.Graphic(self, self.atlas, False, False)
        
        self.graphic.addName("switch-off", 0, 0) 
        self.graphic.addName("switch-on", 1, 1)   
        self.graphic.set("switch-off") 
        self.interact_range = 50
        
        self.already_pressed = False 

    def update(self, dt, player_pos):
        self.graphic.update(dt)
        
        p_vec = pygame.Vector2(player_pos)
        s_vec = pygame.Vector2(self.pos)
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
        # Cambiar al estado contrario si ya está encendido
        self.is_pressed = not self.is_pressed
        
        if self.is_pressed:
            self.graphic.set("switch-on")
            print("Interruptor encendido")
            self.notify(self, 'SWITCH_ON')
        else:
            self.graphic.set("switch-off")
            print("Interruptor apagado")
            if self.target: self.target.lock()
            self.notify(self, 'SWITCH_OFF')

    def serialize(self):
        return {"is_pressed": self.is_pressed}

    def unserialize(self, data):
        self.is_pressed = data["is_pressed"]
        # Actualizamos el gráfico para que coincida
        if self.is_pressed: self.graphic.set("switch-on")
        else: self.graphic.set("switch-off")