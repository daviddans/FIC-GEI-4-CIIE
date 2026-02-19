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
        #move the camera
        self.pos = (self.pos[0]+ vector[0],self.pos[1]+vector[1])
        self.box.topleft = self.pos 
        self.bounding.center = self.box.center 
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.box.topleft)

        print("Camera moved. Amount: " + str(vector) +  " Box:" + str(self.box.topleft) + " bound: " + str(self.bounding.topleft))

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos):
                offx = 0
                offy = 0
                if self.reference.pos[0] < self.bounding.left:
                    offx = self.reference.pos[0] - self.box.left
                elif self.reference.pos[0] > self.bounding.right:
                    offx = self.reference.pos[0] - self.box.right

                if self.reference.pos[1] < self.bounding.top:
                    offy = self.reference.pos[1] - self.box.top
                elif self.reference.pos[1] > self.bounding.bottom:
                    offy = self.reference.pos[1] - self.box.bottom
                self.move((offx,offy))
            
    def draw(self, screen):
        for group in self.spriteGroups:
            group.draw(screen,self.pos)