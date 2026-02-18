import pygame
import abstract
import utils
class testTree():
    def __init__(self):
        pass

class testBox():
    def __init__(self):
        pass

class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0,0), z_layer=0):
        super().__init__(name, pos, z_layer)
        self.spriteGroups = list()
        size = (utils.conf.getint("video","xres"), utils.conf.getint("video","yres"))
        bound = (size[0] -100, size[1] -100)
        self.box = pygame.Rect(self.pos, size)
        self.bounding = pygame.Rect(self.pos, bound) 
        self.reference = None

    def addGroup(self, group:pygame.sprite.Group):
        self.spriteGroups.append(group)

    def setReference(self, ref:abstract.Object):
        self.reference = ref

    def move(self, vector):
        self.pos = (self.pos[0]+ vector[0],self.pos[1]+vector[1])
        self.box.move_to(topleft=self.pos)
        self.bounding.move_to(center=self.box.center)

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos):
                offx = 0
                offy = 0
                if self.reference.pos[0] < self.bounding.left:
                    offx = self.reference.pos[0] - self.bounding.left
                else:
                    offx = self.reference.pos[0] - self.bounding.right

                if self.reference.pos[1] < self.bounding.topleft[1]:
                    offy = self.reference.pos[1] - self.bounding.top
                else:
                    offy = self.reference.pos[1] - self.bounding.bottom
                self.move((offx,offy))
        print("CAMERA at :" + str(self.pos))
            
    def draw(self, screen):
        for group in self.spriteGroups:
            group.draw(screen,self.pos)