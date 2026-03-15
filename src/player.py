import pygame
import abstract
import components
import objects
from resourceManager import ResourceManager
from debugLogger import DebugLogger

class Player(abstract.Object):
    def __init__(self, pos=(0,0), name="player", graphic_group=None, light_group=None, **kwargs):
        super().__init__(name, pos)
        speed            = float(kwargs.get("speed", 0.1))
        max_hp           = int(kwargs.get("max_hp", 3))
        animation_speed  = int(kwargs.get("animation_speed", 400))

        self.atlas = ResourceManager.getAtlas("player-base")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.add(graphic_group)

        self.light = components.Graphic(self, ResourceManager.getAtlas("light1"), offset=(-120,-120), primary=False)
        self.light.add(light_group)

        self.graphic.addState("move", [1,2])
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=speed)
        self.health = components.Health(max_hp=max_hp)
        self.animation_time_elapsed = 0
        self.move_animation_speed = animation_speed

        self.light.addState("on", [0,1,2,3,4,5,6])
        self.light.setState("on")
        DebugLogger.log("Player init: name=%s pos=%s speed=%s max_hp=%d", name, pos, speed, max_hp)

    def update(self, dt, map=None):
        self.input.update()
        vector = self.input.get_vector()

        if  vector != (0,0) : 
            self.graphic.setState("move")
            self.move.update(vector, dt, map)
        else :
            self.graphic.setState("idle")
        #Si en la actualizacion anterior se resetea la animacion

        #Actualizar animaciones
        self.animation_time_elapsed += dt
        if self.animation_time_elapsed >= self.move_animation_speed:
            self.animation_time_elapsed = 0
            if self.graphic.updateFrame():
                self.graphic.resetFrame()
            if self.light.updateFrame():
                self.light.resetFrame()

    def events(self):
        pass

    #para que el jugador guarde su posicion (de momento solo posicion)
    def serialize(self):
        return {
            "pos": self.pos.topleft 
        }
    
    # para recuperar la posición del diccionario de guardado
    def unserialize(self, data):
        if "pos" in data:         
            self.pos.topleft = data["pos"]

