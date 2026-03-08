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
        self.graphic = components.Graphic(self, self.atlas, True, True)
        self.graphic.addName("idle", 0, 2)
        self.graphic.set("idle")
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=speed)
        self.pos = self.graphic.rect.copy()
        self.pos.topleft = pos
        
    def collide(self):
        pass

    def update(self, dt, map=None):
        self.input.update()
        vector = self.input.get_vector()
        if  vector != (0,0) : 
            self.move.update(vector, dt, map)

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