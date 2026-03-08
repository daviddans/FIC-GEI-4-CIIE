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
Implentacion de la clase grafica como una maquina de estados
Cada estado tiene una lista de ids 
Durante el update se ira cambiando entre cada id mostrando el subsurface correspondiente del Atlas
El update devolvera True si se alcanzo el ultimo frame o es unoe
"""


class Graphic(pygame.sprite.Sprite):
    def __init__(self, parent:abstract.Object, atlas:Atlas):
        super().__init__()
        self.image = None
        self.rect = None
        self.current_state = None
        self._current_frame = 0
        self._states = dict()
        self.animate= False
        self.parent = parent
        self._atlas = atlas
        self._camera_pos = (0,0)
        
    def addState(self, name, ids:list[int]):
        if len(ids) <= 0 :
            raise Exception("No se puede añadir un estado sin frames al componente grafico")
        self._states.update({name : ids})

    def setState(self, name):
        updated_state = False
        if name != self.current_state :
            #Ponemos el estado escogido como actual
            self.current_state = name
            self.animate = len(self._states[self.current_state]) > 0 
            self._current_frame = 0
            self.image = self._atlas.getSprite(self._states[self.current_state][self._current_frame])
            self.rect = self.image.get_rect()
            #Actualizar rect del padre.
            self.parent.pos.size = self.rect.size
            updated_state = True
        return updated_state
    
    def resetFrame(self):
        self._current_frame = 0

    def updateFrame(self):
        last_frame = None # Devuelve None si no es animacion
        #Actualizar frame si es animacion
        if self.animate :
            self.time_elapsed = 0
            last_frame = False
            self.image = self._atlas.getSprite(self._states[self.current_state][self._current_frame])
            self.rect = self.image.get_rect() #Actualizar rect del padre.
            self.parent.pos.size = self.rect.size
            self._current_frame = self._current_frame + 1
            print(f"FRAME UPDATED. Current frame: {self._current_frame}")
            if self._current_frame == len(self._states[self.current_state]):

                last_frame = True
        #Retornar flag de ultimo frame
        return last_frame
    
    def update(self, dt):
        pos = (self.parent.pos[0] - self._camera_pos[0], self.parent.pos[1] - self._camera_pos[1])
        #Actualizar posicion
        self.rect.topleft = pos


    def cameraUpdate(self, pos):
        self._camera_pos = pos

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
        self.rect = self.image.get_rect(topleft=parent.pos.topleft)
        self.camera_pos = (0, 0)

    def update(self, dt):
        pos = (self.parent.pos[0] - self._camera_pos[0],
               self.parent.pos[1] - self._camera_pos[1])
        self.rect.topleft = pos

    def cameraUpdate(self, pos):
        self._camera_pos = pos


#Button may not be an component but a object instead consider refactor
class Button(abstract.Object):
    def __init__(self, img, x=0, y=0, scale=1):
        super().__init__("button",(x, y))
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
        #esto es un poco sucio porque fuerza a pygame a actualizar su estado, hay que revisar como hacerlo bien porque no se mueve el player si no
        pygame.event.pump() 
        
        keys = pygame.key.get_pressed()
        
        x = 0
        y = 0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: x += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  x -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  y += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    y -= 1
        
        self.direction.x = x
        self.direction.y = y
        
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
        #print(f"move target to: {target}")

    #Comprobar si es una posicion alcanzable en una matriz de mapa
    def reachable(self, x_pixel, y_pixel, matrix):
        if matrix is None:
            return True
        tile_size = ResourceManager.getConfig().getint("engine", "tile_size")
        scale = ResourceManager.getConfig().getint("video", "scale")
        grid_x = int(x_pixel // (tile_size*scale))
        grid_y = int(y_pixel // (tile_size*scale))
        #print(f"Grid reachability tested:({grid_x}, {grid_y})")
        if 0 <= grid_x < len(matrix[0]) and 0 <= grid_y < len(matrix):
            return matrix[grid_y][grid_x]
        return False

    
class Health:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.is_dead = False

    def take_damage(self, amount=1):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
        return self.is_dead # Avisa si ha muerto
    
    def heal(self, amount=1):
        """Aumenta la vida actual sin sobrepasar el máximo"""
        if not self.is_dead:
            self.current_hp = min(self.max_hp, self.current_hp + amount)
            print(f"Curado. Vida actual: {self.current_hp}/{self.max_hp}")
    
    def reset(self):
        """Devuelve al componente a su estado inicial"""
        self.current_hp = self.max_hp
        self.is_dead = False