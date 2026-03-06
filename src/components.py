import pygame
import abstract
import objects
import json
from resourceManager import ResourceManager
"""
Class to load a full spritesheet ( atlas ) and give subsurface to be used 

"""
class Atlas():
    def __init__(self, image, coords):
        self.atlas = image
        self.coordinates = coords
        size = self.atlas.get_size()
        self.scale = ResourceManager.getConfig().getint("video", "scale")
        self.atlas = pygame.transform.scale(self.atlas,(size[0]*self.scale, size[1]*self.scale))
        
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

#Wrapper to make the surface in the tilemap behave like a sprite, so we can use the same camera logic for the map and the objects
class Tile(pygame.sprite.Sprite):
    def __init__(self, parent:abstract.Object, layers: list):
        super().__init__()
        self.parent = parent
        self.layers = layers
        # build a single surface containing every layer in order so that the map
        # can be treated as a single sprite.  keep the original list around in
        # case other systems need access to individual layers later.
        if layers:
            width = max(layer.get_width() for layer in layers)
            height = max(layer.get_height() for layer in layers)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            for layer in layers:
                self.image.blit(layer, (0, 0))
        else:
            self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=parent.pos)
        self.camera_pos = (0, 0)

    def update(self, dt):
        pos = (self.parent.pos[0] - self.camera_pos[0],
               self.parent.pos[1] - self.camera_pos[1])
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

class Input():
    def __init__(self,parent:abstract.Object):
        self.parent = parent
        self.direction = pygame.Vector2(0, 0)

    def get_vector(self):
        return self.direction
    
    def update(self):
        keys = pygame.key.get_pressed()
        x = keys[pygame.K_d] - keys[pygame.K_a]
        y = keys[pygame.K_s] - keys[pygame.K_w]
        
        self.direction.update(x,y)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

class Movement():
    def __init__(self, parent:abstract.Object, speed):
        self.parent = parent
        self.speed = speed
     
    def update(self, vector, dt, map):
        scale = ResourceManager.getConfig().getint("video", "scale")
        correction = 3 * scale # Correccion para evitar errores pixel perfect
        #Calcular movimiento
        move = (vector.x * self.speed * dt, vector.y *self.speed * dt)
        #Calcular posicion resultante
        target = (self.parent.pos.left + move[0], self.parent.pos.top + move[1])
        #Comprobar que todas las esquinas vayan a una casilla accesible
        if vector.x > 0 : #Derecha
            if ( not self.reachable(self.parent.pos.right + move[0], self.parent.pos.top + correction, map) 
                or not self.reachable(self.parent.pos.right + move[0], self.parent.pos.bottom - correction, map) ):
                target = (self.parent.pos.left, target[1])
        elif vector.x < 0: #Izquierda
            if ( not self.reachable(self.parent.pos.left + move[0], self.parent.pos.top + correction, map) 
                or not self.reachable(self.parent.pos.left + move[0], self.parent.pos.bottom - correction, map) ):
                target = (self.parent.pos.left, target[1])

        if vector.y > 0 : #Abajo
            if ( not self.reachable(self.parent.pos.left + correction, self.parent.pos.bottom + move[1], map) 
                or not self.reachable(self.parent.pos.right - correction, self.parent.pos.bottom + move[1], map) ):
                target = (target[0], self.parent.pos.top)
        elif vector.y < 0 : #Arriba
            if ( not self.reachable(self.parent.pos.left + correction, self.parent.pos.top + move[1], map) 
                or not self.reachable(self.parent.pos.right - correction, self.parent.pos.top + move[1], map) ):
                 target = (target[0], self.parent.pos.top)

        #actualizar posicion
        self.parent.pos.topleft = target
        print(f"move target to: {target}")

    #Comprobar si es una posicion alcanzable en una matriz de mapa
    def reachable(self, x_pixel, y_pixel, matrix):
        if matrix is None:
            return True
        tile_size = ResourceManager.getConfig().getint("engine", "tile_size")
        scale = ResourceManager.getConfig().getint("video", "scale")
        grid_x = int(x_pixel // (tile_size*scale))
        grid_y = int(y_pixel // (tile_size*scale))
        print(f"Grid reachability tested:({grid_x}, {grid_y})")
        if 0 <= grid_x < len(matrix[0]) and 0 <= grid_y < len(matrix):
            return matrix[grid_y][grid_x]
        return False