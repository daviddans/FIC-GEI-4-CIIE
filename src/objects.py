import pygame
import abstract
import utils
import components
from random import randint

#just a class for create a simple sprite in  a random places for testing purposes
class testTree(abstract.Object):
    def __init__(self):
        super().__init__()
        image = pygame.image.load(utils.conf.get("engine", "assets_path") + "arbol.png")
        self.pos = (randint(-100, 1000), randint(-100, 1000))
        self.atlas = components.Atlas("arbol.png")
        self.sprite = components.Graphic(self,self.atlas, False)
        self.sprite.addName("tree", 0,0)
        self.sprite.set("tree")

class Camera(abstract.Object):
    def __init__(self, name="camera", pos=(0,0)):
        super().__init__(name, pos)
        self.spriteGroups = list()
        size = (utils.conf.getint("video","xres"), utils.conf.getint("video","yres"))
        self.box = pygame.Rect(self.pos, size)
        print("Camera area:" + str(self.box))
        self.bounding =  self.box.scale_by(0.5, 0.5)
        print("Bound area:" + str(self.bounding))
        self.reference = None

    def addGroup(self, group:pygame.sprite.Group):
        self.spriteGroups.append(group)

    def move(self, vector):
        #move the camera
        self.pos = (self.pos[0]+ vector[0],self.pos[1]+vector[1])
        self.box.topleft = self.pos 
        self.bounding.center = self.box.center 
        #update listeners
        for group in self.spriteGroups:
            for sprite in group.sprites():
                sprite.cameraUpdate(self.box.topleft)
                
        print("Camera moved. Amount: " + str(vector) + "Pos: " + str(self.pos) + " Box:" + str(self.box.topleft) + " bound: " + str(self.bounding.topleft))


    def setReference(self, ref:abstract.Object):
        self.reference = ref
        #initial center on the reference
        offset = (ref.pos[0] - self.box.center[0], ref.pos[1] - self.box.center[1])
        self.move(offset)

    def update(self,dt):
        if self.reference is not None :
            if not self.bounding.collidepoint(self.reference.pos):
                offx = 0
                offy = 0
                if self.reference.pos[0] < self.bounding.left:
                    offx = self.reference.pos[0] - self.bounding.left
                elif self.reference.pos[0] > self.bounding.right:
                    offx = self.reference.pos[0] - self.bounding.right

                if self.reference.pos[1] < self.bounding.top:
                    offy = self.reference.pos[1] - self.bounding.top
                elif self.reference.pos[1] > self.bounding.bottom:
                    offy = self.reference.pos[1] - self.bounding.bottom
                self.move((round(offx * 0.2), round(offy * 0.2)))
            
    def draw(self, screen):
        for group in self.spriteGroups:
            group.draw(screen)
