import abstract
from resourceManager import ResourceManager
import components
import pygame

class Key(abstract.Object, abstract.Observable): 
    def __init__(self, pos, graphic_group=None,light_group=None, **kwargs):
        super().__init__("key", pos)
        self.pos.size = (32, 32)
        print("KEY POS:", self.pos)
    
        abstract.Observable.__init__(self)
        self.key_id = kwargs.get("name", "default_key")
        self.proximity_range = 50
        self.is_active = True
        self.atlas = ResourceManager.getAtlas("key")
        self.graphic = components.Graphic(self, self.atlas)
        print(self.atlas)
        self.graphic.add(graphic_group)
        
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        print("KEY GRAPHIC GROUPS:", self.graphic.groups())

    def update(self, dt, player_pos):
        if not self.is_active:
            return
            
        self.graphic.update(dt)
        
        # Lógica de recogida con la tecla P
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            p_vec = pygame.Vector2(player_pos)
            k_vec = pygame.Vector2(self.pos.topleft)
            
            if p_vec.distance_to(k_vec) < self.proximity_range:
                self.interact() # Aquí la llave llama a Nix y se guarda

    def on_collision(self, other):
     if self.is_active:
        self.interact()

    def interact(self):
     if not hasattr(self, 'player') or self.player is None:
        print("NO HAY PLAYER EN LA KEY")
        return
     print(f"Llave {self.key_id} guardada. Inventario: {self.player.keys}")
     self.player.keys.append(self.key_id)
     self.notify(self, 'KEY_PICKED')
     for group in self.graphic.groups():
        group.remove(self.graphic)
     self.is_active = False