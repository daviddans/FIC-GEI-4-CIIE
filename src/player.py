import pygame
import abstract
import components
import math
import utils
import objects
from resourceManager import ResourceManager

class Player(abstract.Object):
    def __init__(self, pos=(0,0), **kwargs):
        super().__init__("player", pos)
    
        self.atlas = ResourceManager.getAtlas("player-base")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.addState("move", [1,2])
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        life = int(kwargs.get("hp", 3)) #implementar la variable health en Tiled (de momento 3 por defecto)
        
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=0.5)
        self.health = components.Health(life)
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

        #Actualizar animaciones
        self.animation_time_elapsed += dt
        if self.animation_time_elapsed >= self.move_animation_speed:
            print("FRAME UPDATE")
            self.animation_time_elapsed = 0
            if self.graphic.updateFrame():
                self.graphic.resetFrame()

    def events(self):
        pass

    def receive_hit(self, damage=1):
        dead = self.health.take_damage(damage)
        
        if dead:
            print("Nix ha muerto")
            self.die()
        else:
            print(f" queda {self.health.current_hp} de vida")
          
    def die(self):
        # Lógica de muerte (game over, resucitar etc)
        pass     