import pygame
import abstract
import components
import math
import utils
import objects
from resourceManager import ResourceManager

class Player(abstract.Object):
    def __init__(self, pos=(0,0), speed=0.5):
        super().__init__("player", 1)
        self.pos = list(pos)  
        self.atlas = ResourceManager.getAtlas("player-base")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.addState("move", [1,2])
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=0.5)
        self.animation_end = False
        self.animation_time_elapsed = 0
        self.move_animation_speed = 400

    def update(self, dt, map=None):
        self.input.update()
        vector = self.input.get_vector()

        if  vector != (0,0) : 
            self.graphic.setState("move")
            self.move.update(vector, dt, map)
        else :
            self.graphic.setState("idle")
        #Si en la actualizacion anterior se resetea la animacion

        #Actualizar animacions
        self.animation_time_elapsed += dt
        if self.animation_time_elapsed >= self.move_animation_speed:
            print("FRAME UPDATE")
            self.animation_time_elapsed = 0
            if self.graphic.updateFrame():
                self.graphic.resetFrame()

    def events(self):
        pass

    #para que el jugador guarde su posicion (de momento solo posicion)
    def serialize(self):
        return {
            "pos": list(self.pos.topleft), 
        }
    
    # para recuperar la posición del diccionario de guardado
    def unserialize(self, data):
        if "pos" in data:         
            self.pos.topleft = data["pos"]
            self.graphic.rect.topleft = data["pos"]
