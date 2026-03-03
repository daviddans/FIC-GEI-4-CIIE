import pygame
import abstract
import objects
import utils
import json
import os

"""
Class to load a full spritesheet ( atlas ) and give subsurface to be used 

"""
#Todo: This component should be created and managed by a singletone manager to load only one instance for each atlas
#ToDo: Improve this clase with a coordinateSheet instead of asumme everything is contiguous and 16x16
class Atlas():

    _cached_data = {} # dict para que queden los json cargados en memoria

    def __init__(self, sheetName):
        base_path = utils.conf.get("engine", "assets_path")
        self.atlas = pygame.image.load(base_path + sheetName)

        json_name = sheetName.replace(".png", ".json")
        json_path = base_path + json_name

        if json_name not in Atlas._cached_data:
            try:
                with open(json_path, 'r') as f:
                    Atlas._cached_data[json_name] = json.load(f)
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo {json_path}")
                Atlas._cached_data[json_name] = {}

        self.coordinates = Atlas._cached_data[json_name]
        self.key = sheetName.replace(".png", "") 
        
        size = self.atlas.get_size()
        self.scale = utils.conf.getint("video", "scale")
        self.atlas = pygame.transform.scale(self.atlas,(size[0]*self.scale, size[1]*self.scale))
        
    
    #This should recieve an id, and look in the coordinate sheet the rect of said id.
    #For the moment it will recieve the explicit coordiantes until a better implementation is given
            # In exaple, the testTree is not displayed correctly as it is 16x32 so it asumes only the top part
            # those are the scenearios where the coordinate sheet will automaticaly fit images.
            # The atlas also manages the scaling image, so only one transform will be applied
    def getSprite(self, id):
        info = self.coordinates.get(str(id))

        if not info:
            print(f"Error: ID {id} no encontrado en la seccion {self.key}")
            #Si no existe que recorte por defecto 16x16 para que no pete el juego basicamente
            return pygame.Surface((16 * self.scale, 16 * self.scale))
        
        x = info["x"]
        y = info["y"]
        w = info["w"]
        h = info["h"]
        
        location = pygame.Rect(x * self.scale, y * self.scale, w * self.scale, h * self.scale)
        
        return self.atlas.subsurface(location)

#Possible bugs may lay when diffrent size sprites are encountered. As now, it loads a rec that is embbeded on the image 
#setting the parent object pos as topletf, but we may want to change this behaviour on future

"""
Component for displaying sprites. 
    ·Atributtes:
        -Animate:bool -> true is animation, false is a static sprite
        -Parent:abstract.Object -> Object that has an instance of this component
        -Atlas:component.Atlas -> Atlas to retrieve the surfaces
        -Current:int -> Id of the current sprite to show
        -Names:dict -> Dictionary to store the ids on the atlas related to a name. This way we can play a animation "walk", previously defined instead of play an animation (12, 18) 
    ·Methods:
        -AddName(name, begin, end) -> Set a internal name for a static image or animation, an animation
        will cycle between begin and end id images, for a static image, end will be ignored
        -Set(name) -> Set the ids related to the name given as the current to display
        -Set_id(begin, end)-> Set ids to show related to its atlas. For static sprite begin will used. For animation frame will cicle betwen begin and end
"""


class Graphic(pygame.sprite.Sprite):
    def __init__(self, parent:abstract.Object, atlas:Atlas, animate:bool, speed:int = 1000):
        super().__init__()
        self.animate = animate
        self.parent = parent
        self.atlas = atlas
        self.current = (0,0)
        if animate :
            self.frame = 0
            self.time_elapsed = 0
            self.time_animation = speed
        self.names = dict()
        self.image = None
        self.rect = None
        self.camera_pos = (0,0)
        
    def addName(self, name, begin, end):
        self.names.update({name : (begin, end)})

    def set(self, name):
        self.set_id(self.names[name][0], self.names[name][1])

    def set_id(self, begin, end):
        self.current = (begin, end)
        self.image = self.atlas.getSprite(begin)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.parent.pos
        if self.animate:
            self.frame = begin

    def nextFrame(self):
        if self.animate :
            self.frame = (self.frame + 1) % (self.current[1] - self.current[0]) 
            self.frame += self.current[0]
            self.image = self.atlas.getSprite(self.frame)
            self.rect = self.image.get_rect()

    def update(self, dt):
        if self.animate :
            self.time_elapsed += dt 
            if self.time_elapsed >= self.time_animation:
                self.nextFrame()
                self.time_elapsed = 0
        else:
            pass
        pos = (self.parent.pos[0] - self.camera_pos[0], self.parent.pos[1] - self.camera_pos[1])
        self.rect.topleft = pos

    def cameraUpdate(self, pos):
        self.camera_pos = pos

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

