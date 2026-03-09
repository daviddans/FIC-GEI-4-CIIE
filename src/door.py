import abstract
from resourceManager import ResourceManager
import components
import pygame

class Door(abstract.Object, abstract.Observer):
    def __init__(self, pos, is_locked=True, **kwargs):
        super().__init__("door", pos)
        
        self.is_locked = is_locked
        self.is_open = False
        self.proximity_range = 80 # Distancia para que se abra sola
        
        self.atlas = ResourceManager.getAtlas("puerta")
        self.graphic = components.Graphic(self, self.atlas)
        self.need_key = kwargs.get("need_key", "key1")
        self.graphic.addState("locked", [0])   
        self.graphic.addState("unlocked", [1])  
        self.graphic.addState("opening", [2,3])   
        
        # Estado inicial
        if self.is_locked:
            self.graphic.setState("locked")
        else:
            self.graphic.setState("unlocked")

    def on_notify(self, entity, event):
        if event == 'SWITCH_ON' or event == 'KEY_PICKED':
            self.unlock()
            print("Puerta desbloqueada (evento SWITCH_ON o KEY_PICKED)")
        elif event == 'SWITCH_OFF':
            self.lock()
            print("Puerta bloqueada (evento SWITCH_OFF)")

    def unlock(self):
        self.is_locked = False
        self.graphic.setState("unlocked")
       

    def lock(self):
        self.is_locked = True
        self.is_open = False
        self.graphic.setState("locked")

    def update(self, dt, player):
        self.graphic.update(dt)
        
        p_vec = pygame.Vector2(player.pos.topleft)
        d_vec = pygame.Vector2(self.pos.topleft)
        distance = p_vec.distance_to(d_vec)
        
        # Lógica de desbloqueo (tecla O)
        if self.is_locked and distance < 60:
            if pygame.key.get_pressed()[pygame.K_o]:
                if self.need_key in player.keys:
                    self.unlock()

        # Lógica de apertura por proximidad (solo si no hay candado)
        if not self.is_locked:
            if distance < self.proximity_range:
                # SOLO llamamos si no estaba ya abierta
                if not self.is_open: 
                    self.open_door()
            else:
                # SOLO llamamos si estaba abierta y ahora Nix se ha alejado
                if self.is_open:
                    self.close_door()
                    
    def open_door(self):
        self.is_open = True
        self.graphic.animate = True 
        self.graphic.loop = False
        self.graphic.setState("opening") # Pasa del frame 2 al 3
        print("Puerta abierta por proximidad.")

    def close_door(self):
        self.is_open = False
        self.graphic.animate = False
        self.graphic.setState("unlocked") # Vuelve al frame 1 (cerrada pero sin candado)
        print("Puerta cerrada.")

    def interact(self, player):
     required_key = self.kwargs.get("need_key", "default_key")
    
     if required_key in player.keys:
        self.open_door() 
        
        # se borra la llave de la lista del jugador
        player.keys.remove(required_key)
        
        print(f"Puerta abierta. La llave {required_key} se ha gastado.")
     else:
        print("Esta puerta está cerrada. Necesitas una llave.")