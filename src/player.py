import pygame
import abstract
import components
import math
import utils
import objects
from resourceManager import ResourceManager

class Player(abstract.Object):
    def __init__(self, pos=(0,0)):
        super().__init__("player", 1)
        self.pos = pos  
        self.atlas = ResourceManager.getAtlas("player-base")
        self.graphic = components.Graphic(self, self.atlas, True)
        self.graphic.addName("idle", 0, 2)
        self.graphic.set("idle")
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=0.5)
        self.pos = self.graphic.rect.topleft
    def collide(self):
        pass

    def update(self, dt, map=None):
        self.input.update()
        self.move.update(self.input.get_vector(), dt, map)

    def events(self):
        pass

    