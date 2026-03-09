import abstract
from resourceManager import ResourceManager
import components
import pygame

class Key(abstract.Object, abstract.Observable): 
    def __init__(self, pos, **kwargs):
        pygame.sprite.Sprite.__init__(self)
        abstract.Object.__init__(self, "key", pos)
    
        abstract.Observable.__init__(self)
        self.key_id = kwargs.get("key_id", "default_key")
        self.proximity_range = 50
        self.is_active = True
        self.atlas = ResourceManager.getAtlas("key")
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
        

    def update(self, dt, player): 
        if not self.is_active: return
        
        self.graphic.update(dt)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            p_vec = pygame.Vector2(player.pos.topleft) 
            k_vec = pygame.Vector2(self.pos.topleft) 
            
            if p_vec.distance_to(k_vec) < self.proximity_range:
                self.interact(player)

    def interact(self, player):
        print(f"Llave {self.key_id} guardada en el inventario.")
       
        player.keys.append(self.key_id)
        
     
        if hasattr(self, 'graphic'):
            for group in self.graphic.groups():
                group.remove(self.graphic)
        self.is_active = False