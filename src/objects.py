import pygame
import abstract

class Button(abstract.Object):
    def __init__(self, img, x=0, y=0, scale=1):
        width = img.get_width()
        height = img.get_height()
        self.img = pygame.transform.scale(img, (int(width*scale), int(height * scale)))
        self.rect = self.img.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def update(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
             if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action
    
    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))
