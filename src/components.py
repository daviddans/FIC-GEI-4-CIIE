import pygame
import abstract
from resourceManager import ResourceManager
from debugLogger import DebugLogger
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
        # convert_alpha acelera todos los blits posteriores (una sola vez al cargar)
        self.atlas = self.atlas.convert_alpha()
        DebugLogger.log("Atlas init: original=%dx%d scale=%d -> %dx%d sprites=%d",
                        size[0], size[1], self.scale,
                        size[0] * self.scale, size[1] * self.scale,
                        len(self.coordinates))
        
    def getSprite(self, id):
        info = self.coordinates.get(str(id))

        if not info:
            DebugLogger.log("Error: ID %s no encontrado en el atlas", id)
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

El offset nos permite modificar la posicion de dibujado respecto al padre ( ideal pa la luz)
primary es un fix pocho, para que un objeto pueda generar varios sprites pero no todos modifiquen su hitbox. (Ej: la luz)
"""


class Graphic(pygame.sprite.Sprite):
    def __init__(self, parent:abstract.Object, atlas:Atlas, offset= (0, 0), primary=True):
        super().__init__()
        self.image = None
        self.rect = None
        self.current_state = None
        self._current_frame = 0
        self._states = dict()
        self.animate= False
        self.parent = parent
        self._atlas = atlas
        scale = ResourceManager.getConfig().getint("video", "scale")
        self._offset = (offset[0] * scale, offset[1] * scale)
        self._camera_pos = (0,0)
        self.primary = primary
        DebugLogger.log("Graphic init: parent='%s' offset=%s primary=%s",
                        getattr(parent, "name", "?"), self._offset, primary)
        
    def addState(self, name, ids:list[int]):
        if len(ids) <= 0 :
            raise Exception("No se puede añadir un estado sin frames al componente grafico")
        self._states.update({name : ids})

    def setState(self, name):
        updated_state = False
        if name != self.current_state :
            DebugLogger.log("Graphic setState: parent='%s' '%s' -> '%s'",
                            getattr(self.parent, "name", "?"), self.current_state, name)
            #Ponemos el estado escogido como actual
            self.current_state = name
            self.animate = len(self._states[self.current_state]) > 0 
            self._current_frame = 0
            self.image = self._atlas.getSprite(self._states[self.current_state][self._current_frame])
            self.rect = self.image.get_rect()
            if self.primary : self.parent.pos.size = self.rect.size #Actualizar rect del padre.
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
            self.rect = self.image.get_rect() 
            if self.primary : self.parent.pos.size = self.rect.size #Actualizar rect del padre.
            self._current_frame = self._current_frame + 1
            if self._current_frame == len(self._states[self.current_state]):

                last_frame = True
        #Retornar flag de ultimo frame
        return last_frame
    
    def update(self, dt, *args):
        pos = (self.parent.pos[0] - self._camera_pos[0] + self._offset[0], self.parent.pos[1] - self._camera_pos[1] + self._offset[1])
        #Actualizar posicion
        self.rect.topleft = pos
        # Y-sort: actualizar layer en grupos LayeredUpdates
        for group in self.groups():
            if isinstance(group, pygame.sprite.LayeredUpdates):
                group.change_layer(self, self.rect.bottom)

    def cameraUpdate(self, pos):
        self._camera_pos = pos


class Input():
    def __init__(self,parent:abstract.Object):
        self.parent = parent
        self.direction = pygame.Vector2(0, 0)
        cfg = ResourceManager.getConfig()

        #getint porque pygame maneja teclas como numeros
        self.keys_map = {
            "up":    cfg.getint("controls", "up"),
            "down":  cfg.getint("controls", "down"),
            "left":  cfg.getint("controls", "left"),
            "right": cfg.getint("controls", "right")
        }

    def get_vector(self):
        return self.direction
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        x = 0
        y = 0
        if keys[self.keys_map["right"]]: x += 1
        if keys[self.keys_map["left"]]:  x -= 1
        if keys[self.keys_map["down"]]:  y += 1
        if keys[self.keys_map["up"]]:    y -= 1
        
        self.direction.x = x
        self.direction.y = y
        
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

class Movement():
    def __init__(self, parent:abstract.Object, speed):
        self.parent = parent
        cfg = ResourceManager.getConfig()
        scale = cfg.getint("video", "scale")
        self._scale     = scale
        self._tile_size = cfg.getint("engine", "tile_size")
        self.correction = 3 * scale
        self.speed = speed * scale
        self._x = float(parent.pos.left)
        self._y = float(parent.pos.top)

    def update(self, vector, dt, map):
        # Sync externo: si el rect fue movido externamente (ej. unserialize)
        if abs(self._x - self.parent.pos.left) > 1:
            self._x = float(self.parent.pos.left)
        if abs(self._y - self.parent.pos.top) > 1:
            self._y = float(self.parent.pos.top)

        new_x = self._x + vector.x * self.speed * dt
        new_y = self._y + vector.y * self.speed * dt

        w = self.parent.pos.width
        h = self.parent.pos.height

        #Comprobar que todas las esquinas vayan a una casilla accesible
        if vector.x > 0 : #Derecha
            if ( not self.reachable(new_x + w, self._y + self.correction, map)
                or not self.reachable(new_x + w, self._y + h - self.correction, map) ):
                new_x = self._x
        elif vector.x < 0: #Izquierda
            if ( not self.reachable(new_x, self._y + self.correction, map)
                or not self.reachable(new_x, self._y + h - self.correction, map) ):
                new_x = self._x

        if vector.y > 0 : #Abajo
            if ( not self.reachable(new_x + self.correction, new_y + h, map)
                or not self.reachable(new_x + w - self.correction, new_y + h, map) ):
                new_y = self._y
        elif vector.y < 0 : #Arriba
            if ( not self.reachable(new_x + self.correction, new_y, map)
                or not self.reachable(new_x + w - self.correction, new_y, map) ):
                new_y = self._y

        self._x = new_x
        self._y = new_y
        self.parent.pos.topleft = (int(self._x), int(self._y))
        #print(f"move target to: {self.parent.pos.topleft}")

    #Comprobar si es una posicion alcanzable en una matriz de mapa
    def reachable(self, x_pixel, y_pixel, matrix):
        if matrix is None:
            return True
        grid_x = int(x_pixel // (self._tile_size * self._scale))
        grid_y = int(y_pixel // (self._tile_size * self._scale))
        #print(f"Grid reachability tested:({grid_x}, {grid_y})")
        if 0 <= grid_x < len(matrix[0]) and 0 <= grid_y < len(matrix):
            return matrix[grid_y][grid_x]
        return False

    
class Health:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.is_dead = False
        DebugLogger.log("Health init: max_hp=%d", max_hp)

    def take_damage(self, amount=1):
        hp_before = self.current_hp
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
        DebugLogger.log("Health take_damage: amount=%d %d -> %d dead=%s",
                        amount, hp_before, self.current_hp, self.is_dead)
        return self.is_dead # Avisa si ha muerto
    
    def heal(self, amount=1):
        if not self.is_dead:
            self.current_hp = min(self.max_hp, self.current_hp + amount)
            DebugLogger.log("Curado. Vida actual: %s/%s", self.current_hp, self.max_hp)
    
    def reset(self):
        self.current_hp = self.max_hp
        self.is_dead = False

class ChasePlayer(abstract.Behavior):
    def __init__(self, vision_range=300):
        self.vision_range = vision_range * ResourceManager.getConfig().getint("video","scale")

    def update(self, npc, dt, player_pos):
        target = pygame.math.Vector2(player_pos)
        current = pygame.math.Vector2(npc.pos.topleft)
        direction = target - current
        distance = direction.length()

        if 5 < distance < self.vision_range:
            direction.normalize_ip()
            # Aplicamos el movimiento al NPC que nos pasen
            npc.move_vec += direction * npc.speed * dt
            npc.pos.topleft = (npc.move_vec.x, npc.move_vec.y)