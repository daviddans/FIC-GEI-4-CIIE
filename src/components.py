import pygame
import abstract
import utils
#---El animador esta hecho sin contemplar excepciones como
# que la animacion no exista en el animator etc por lo que había que
# hacerlo mas seguro a errores y tal (le dejo la revision a otra persona
# que yo no voy a hacerlo todo)


class Animator(pygame.sprite.Sprite):
    def __init__(self, rectangle):
        self.animations = dict()
        self.playing = False
        self.frame = 0
        self.idle = None
        self.current = None
        self.rect = rectangle
        self.image = None

    def addAnimation(self, name, file_name):
        #todo slice and create an image array automatic from file_name
        sprites = []
        sprites.append(utils.sliceAtlas())
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
