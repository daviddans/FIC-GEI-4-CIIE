import pygame
import abstract
import components
import math

class Player(abstract.Object):
    def __init__(self):
        super().__init__("player", 1)
        self.pos = (0,0)
        self.rect = pygame.Rect()
        self.rect.topleft = self.pos

        self.sprite = components.Grapics(self.rect)
        self.sprite.addAnimation("first", "player-base.png")
        self.sprite.playAnimation("first")
        self.input = components.Input(self)
        self.move = components.Movement(self, speed=300)
        self.sprite.update(0)

    def collide(self):
        pass

    def update(self, dt):
        self.input.update()
        vector = self.input.get_vector()
        self.move.update(vector, dt)
        self.sprite.update(dt)

    def events(self):
        pass

    def draw(self, screen):
        self.sprite.draw(screen)
