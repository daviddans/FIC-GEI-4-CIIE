import pygame
import abstract
import components
import math
import utils
class Player(abstract.Object):
    def __init__(self):
        super().__init__("player", 1)
        self.pos = (0,0)
        self.sprite = components.Graphic(self, True)
        sprites = utils.sliceAtlas("player-base.png")
        self.sprite.addSprites("idle", sprites)
        self.sprite.setSprites("idle")
        self.sprite.update(0)
    def input(self):
        keys = pygame.key.get_pressed()
        vector = (0,0)
        if keys[pygame.K_w]:
            vector = (0,-1)
        if keys[pygame.K_s]:
            vector = (0,1)
        if keys[pygame.K_a]:
            vector = (-1,0) 
        if keys[pygame.K_d]:
            vector = (1,0)
        return vector

    def move(self, vector):
        self.pos = (self.pos[0]+vector[0], self.pos[1]+vector[1])
        
    def collide(self):
        pass

    def update(self, dt):
        vector = self.input()
        vector = (vector[0]* dt, vector[1]*dt)
        self.move(vector)
        self.sprite.update(dt)

    def events(self):
        pass