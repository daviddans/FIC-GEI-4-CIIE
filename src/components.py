import pygame
import abstract
import utils



class Grapics(pygame.sprite.Sprite):
    def __init__(self, rectangle):
        self.animations = dict()
        self.playing = False
        self.frame = 0
        self.idle = None
        self.current = None
        self.rect = rectangle
        self.image = None

    def addAnimation(self, name, file_name):
        sprites = utils.sliceAtlas(file_name)
        self.animations.update({name : sprites})
    
    def setIdle(self, name):
        self.idle = self.animations[name]

    def playAnimation(self, name):
        if not self.playing :
            self.current = self.animations[name]
            self.playing = True
    
    def update(self, dt):
        self.frame += 1
        if self.frame >= len(self.current):
            self.frame = 0
        self.image = self.current[self.frame]

    def draw(self, screen):
        if self.image != None:
            screen.blit(self.image ,self.rect)


class Button(abstract.Object):
    def __init__(self, img, x=0, y=0, scale=1):
        super().__init__("button",0)
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

class Input():
    def __init__(self,entity):
        self.entity = entity
        self.direction = pygame.Vector2(0, 0)

    def get_vector(self):
        return self.direction
    #habra que generalizar el update cuando hagamos la logica de los npcs
    def update(self):
        keys = pygame.key.get_pressed()
        x = keys[pygame.K_d] - keys[pygame.K_a]
        y = keys[pygame.K_s] - keys[pygame.K_w]
        
        self.direction.update(x,y)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

class Movement():
    def __init__(self, entity, speed):
        self.entity = entity
        self.speed = speed
     
    def update(self, vector, dt):
        self.entity.pos = (self.entity.pos[0] + vector[0] * self.speed * dt, self.entity.pos[1] + vector[1] * self.speed * dt)
        self.entity.rect.topleft = self.entity.pos       
