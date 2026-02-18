import pygame
import abstract
import utils


#Possible bugs may lay when diffrent size sprites are encountered. As now, it loads a rec that is embbeded on the image 
#setting the parent object pos as topletf, but we may want to change this behaviour on future

"""
Component for displaying a set list of images. Each list would be assumed as an animation, 
but a 1 frame animation works as a static sprite.

-parent -> the object that is implemting the component, its possition will be read
-animations -> dictionary with a list of surface for an animation and a name
-current -> list with the current images to show
-image -> actual surface for the superclass 
-rect -> rect of self.image for the superclass
-frame -> current index on the animation
-time_elapsed -> delta time since the last update in ms
-time_animation -> time between frames in ms

·addSprites (sprites, name)-> add a new list of surfaces under a name
·setSprites (name) -> change current animation 
·update (dt) -> updates the frame to show and position respect the parent

"""

class Graphic(pygame.sprite.Sprite):
    def __init__(self, parent, animate, speed = 1000):
        if not hasattr(parent,"pos") : raise NotImplementedError("Error on Graphic component, parent must have a \"pos\" atributte.")
        self.animate = animate
        self.parent = parent
        if animate :
            self.sprites = dict()
            self.current = None
            self.frame = 0
            self.time_elapsed = 0
            self.time_animation = speed
        self.image = None
        self.rect = None
        
    def addSprites(self, name, sprites):
        self.sprites.update({name : sprites})

    def setSprites(self, name):
        if self.animate :
            self.current = self.sprites[name]
        else:
            self.image = self.sprites[name][0]
            self.rect = self.image.get_rect(topleft=self.parent.pos)

    def update(self, dt):
        if self.animate :
            self.time_elapsed += dt 
            if self.time_elapsed >= self.time_animation:
                self.time_elapsed = 0
                self.frame = (self.frame + 1) % len(self.current) 

            self.image = self.current[self.frame]
            self.rect = self.image.get_rect(topleft=self.parent.pos)
        else:
            pass

    def draw(self, screen):
        #Fallback method, use it in a group is encouraged
        screen.blit(self.image, self.rect)


#Button may not be an component but a object instead consider refactor
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


class Camera(pygame.sprite.Group):
    def __init__(self, parent):
        super().__init__()
        self.scale = 1

    def draw(self):
        for sprite in self.sprites :
            pass