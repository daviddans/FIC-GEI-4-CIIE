import pygame
import math
import abstract
import components
from resourceManager import ResourceManager

class Lantern(abstract.Object):
    def __init__(self, owner, graphic_group=None, light_group=None):
        # El farol se sitúa inicialmente en el centro del dueño [cite: 152]
        super().__init__("lantern", owner.pos.center)
        self.owner = owner
        self._scale = ResourceManager.getConfig().getint("video", "scale")
        self.pos.topleft = owner.pos.topleft
        
        # --- Lógica de balanceo y animación ---
        self.angle = 0.0
        self.time = 0.0
        self.float_speed = 0.15
        
        # --- Estados del Desarrollo Artístico ---
        self.state = "ON" # Estados: ON (Luz), OFF (Sigilo), BEAM (Rayo) [cite: 92, 93]
        self.energy = 100.0 # El farol requiere gestión de energía [cite: 97]
        
        # --- Componente Físico (El farol que se ve en la mano) ---
        self.atlas = ResourceManager.getAtlas("lantern")
        # Offset inicial para la mano derecha
        self.graphic = components.Graphic(self, self.atlas, offset=(20, 10),primary=False)
        self.graphic.add(graphic_group)
        if isinstance(graphic_group, pygame.sprite.LayeredUpdates):
         graphic_group.change_layer(self.graphic, 99999)

        self.graphic.addState("idle", [0])    # encendido 
        self.graphic.addState("off", [1])     # apagado
        self.graphic.setState("idle")
        small = pygame.transform.scale(self.graphic.image, (16, 16))
        self.graphic.image = small
        self.graphic.rect = small.get_rect()
            
        # --- Componente de Luz (Efectos lumínicos de Adalario) ---
        # La luz es esencial para la cohesión de la materia [cite: 11, 36]
        self.light_atlas = ResourceManager.getAtlas("light1")
        self.light_graphic = components.Graphic(self, self.light_atlas, offset=(-32, -32), primary=False)
        if light_group: 
            self.light_graphic.add(light_group)

        # Definición de estados de luz para evitar errores de Rect [cite: 148]
        self.light_graphic.addState("normal", [7]) # Halo de luz ambiental [cite: 92]
        self.light_graphic.addState("rayo", [1])   # Rayo concentrado para enemigos 
        
        # Estado inicial: encendido
        self.light_graphic.setState("normal")
        self.pos.size = (64, 64)

    def update(self, dt, player_pos):
        # Al principio de update:
     print("EN GRUPOS:", len(self.graphic.groups()), "VISIBLE:", self.graphic.visible if hasattr(self.graphic, 'visible') else "N/A")
     if not self.owner: return
     keys = pygame.key.get_pressed()
     if not hasattr(self, '_last_keys'):
      self._last_keys = keys

     if keys[pygame.K_1] and not self._last_keys[pygame.K_1]:
      self.set_state("ON")
     elif keys[pygame.K_2] and not self._last_keys[pygame.K_2]:
      self.set_state("OFF")
     elif keys[pygame.K_3] and not self._last_keys[pygame.K_3]:
      self.set_state("BEAM")

     self._last_keys = keys

    # 1. EFECTO DE FLOTACIÓN
     self.time += self.float_speed
    
    # 2. DETERMINAR DIRECCIÓN
     move_vec = self.owner.input.get_vector()
    
     target_angle = 0
     direction_offset = 15

     if move_vec.x > 0: 
        target_angle = -10
        direction_offset = 20
        self.graphic._offset = (0 * self._scale, 0 * self._scale)
     elif move_vec.x < 0: 
        target_angle = 10
        direction_offset = -20
        self.graphic._offset = (0 * self._scale, 0 * self._scale)
     else:
        self.graphic._offset = (0 * self._scale, 0 * self._scale)
    
     self.angle += (target_angle - self.angle) * 0.1

    # 3. SINCRONIZACIÓN DE POSICIÓN
     self.pos.topleft = (player_pos[0] + direction_offset, player_pos[1] + 10)

    # 4. LÓGICA DE ENERGÍA
     if self.state != "OFF":
        drain_rate = 0.01 if self.state == "BEAM" else 0.005
        self.energy -= drain_rate * dt
        if self.energy <= 0: 
            self.energy = 0
            self.set_state("OFF")

    # 5. EFECTO BEAM CONTINUO
     if self.state == "BEAM":
        self._activate_nearby()

    # 6. VISIBILIDAD
     if self.state == "OFF":
        self.owner.hidden = True
        self.light_graphic.visible = False
     else:
        self.owner.hidden = False
        self.light_graphic.visible = True

    # 7. ACTUALIZACIÓN DE COMPONENTES
     cam_pos = self.graphic._camera_pos  # tomar la cam del graphic principal
     self.light_graphic.cameraUpdate(cam_pos)  # sincronizar la cam al light
     print("BEFORE UPDATE image size:", self.graphic.image.get_size())
     self.graphic.update(dt)
     print("AFTER UPDATE image size:", self.graphic.image.get_size())
     for group in self.graphic.groups():
      if isinstance(group, pygame.sprite.LayeredUpdates):
        group.change_layer(self.graphic, self.owner.graphic.rect.bottom + 1)
     self.light_graphic.update(dt)
    
    def set_state(self, new_state):
     self.state = new_state
     if self.state == "ON":
        self.graphic.current_state = None
        self.graphic.setState("idle")
        self._apply_scale()
        self.light_graphic.visible = True
        self.light_graphic.setState("normal")
        self.owner.hidden = False
     elif self.state == "OFF":
        self.graphic.current_state = None
        self.graphic.setState("off")
        self._apply_scale()
        print("AFTER SCALE:", self.graphic.image.get_size()) 
        self.light_graphic.visible = False
        self.owner.hidden = True
     elif self.state == "BEAM":
        self.graphic.current_state = None
        self.graphic.setState("idle")
        self._apply_scale()
        self.light_graphic.visible = True
        self.light_graphic.setState("rayo")
        self.owner.hidden = False
        

    def _apply_scale(self):
     print("APPLY SCALE, state:", self.graphic.current_state, "image size:", self.graphic.image.get_size())
     small = pygame.transform.scale(self.graphic.image, (16, 16))
     self.graphic.image = small
     self.graphic.rect = small.get_rect()

    def _activate_nearby(self):
     """Activa switches/mecanismos en rango del rayo."""
     for ent in self.owner.graphic.groups()[0].sprites():
        if not hasattr(ent, 'parent'):
            continue
        obj = ent.parent
        if obj is self.owner:
            continue
        if hasattr(obj, 'on_notify'):
            dist = pygame.Vector2(self.pos.center).distance_to(
                   pygame.Vector2(obj.pos.center))
            if dist < 150:
                obj.on_notify(self, 'BEAM')