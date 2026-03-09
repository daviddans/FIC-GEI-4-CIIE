import pygame
import math
from resourceManager import ResourceManager
import components

class Shadow(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.player = player 
        
      
        self.pos = pygame.Rect(x, y, 32, 32)
        self.rect = self.pos
        self.move_vec = pygame.math.Vector2(x, y)
        
        self.speed = 1.2 
        self.damage = 0.5 
        
        self.atlas = ResourceManager.getAtlas("ShadowTrooper")
        self.graphic = components.Graphic(self, self.atlas)
        
        self.graphic.addState("0", [0]) 
        self.graphic.setState("0") 

    def update(self, dt):
        
        player_pos = pygame.math.Vector2(self.player.pos.x, self.player.pos.y)
        direction = player_pos - self.move_vec
        distance = direction.length()

        if 10 < distance < 250:
            direction.normalize_ip()
            self.move_vec += direction * self.speed
        
       
        self.pos.topleft = (self.move_vec.x, self.move_vec.y)
        self.rect.topleft = self.pos.topleft

    def draw(self, screen, camera_offset):
        draw_pos = (self.pos.x - camera_offset[0], self.pos.y - camera_offset[1])
        screen.blit(self.graphic.image, draw_pos)