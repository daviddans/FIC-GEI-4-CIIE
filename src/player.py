import pygame
import math

class Player():
    def __init__(self):
        self.pos = (0,0)

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

    def upddate(self, dt):
        vector = self.input()
        vector = (vector[0]* dt, vector[1]*dt)
        self.move(vector)

    def events(self):
        pass

    def draw(self, screen):
        img = pygame.draw.circle(screen, "red", self.pos, 40)
