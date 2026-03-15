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
        
        # --- Lógica de balanceo y animación ---
        self.angle = 0.0
        self.time = 0.0
        self.float_speed = 0.15
        self.float_amplitude = 2  # Amplitud suave para no distorsionar la posición
        
        # --- Estados del Desarrollo Artístico ---
        self.state = "ON" # Estados: ON (Luz), OFF (Sigilo), BEAM (Rayo) [cite: 92, 93]
        self.energy = 100.0 # El farol requiere gestión de energía [cite: 97]
        
        # --- Componente Físico (El farol que se ve en la mano) ---
        self.atlas = ResourceManager.getAtlas("lantern")
        # Offset inicial para la mano derecha
        self.graphic = components.Graphic(self, self.atlas, offset=(20, 10))
        if graphic_group:
            self.graphic.add(graphic_group)

        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")
            
        # --- Componente de Luz (Efectos lumínicos de Adalario) ---
        # La luz es esencial para la cohesión de la materia [cite: 11, 36]
        self.light_atlas = ResourceManager.getAtlas("light1")
        self.light_graphic = components.Graphic(self, self.light_atlas)
        if light_group: 
            self.light_graphic.add(light_group)

        # Definición de estados de luz para evitar errores de Rect [cite: 148]
        self.light_graphic.addState("normal", [0]) # Halo de luz ambiental [cite: 92]
        self.light_graphic.addState("rayo", [1])   # Rayo concentrado para enemigos 
        
        # Estado inicial: encendido
        self.light_graphic.setState("normal")

    def update(self, dt, player_pos):
        if not self.owner: return

        # 1. EFECTO DE FLOTACIÓN
        self.time += self.float_speed
        float_offset = math.sin(self.time) * self.float_amplitude
        
        # 2. DETERMINAR DIRECCIÓN (Solución para el error de .vector)
        # Obtenemos el vector de movimiento directamente del input de Nix
        move_vec = self.owner.input.get_vector()
        
        # Ajustamos el lado (mano) y la inclinación por inercia
        target_angle = 0
        direction_offset = 20 # Por defecto a la derecha
        
        if move_vec.x > 0: 
            target_angle = -10
            direction_offset = 20
            self.graphic.offset = (20, 10) # Mano derecha
        elif move_vec.x < 0: 
            target_angle = 10
            direction_offset = -20
            self.graphic.offset = (-20, 10) # Mano izquierda
        
        # Suavizado de la rotación (opcional según soporte del motor)
        self.angle += (target_angle - self.angle) * 0.1

        # 3. SINCRONIZACIÓN DE POSICIÓN
        # El farol sigue al centro del jugador con el balanceo aplicado [cite: 152]
        self.pos.center = (player_pos[0] + direction_offset, player_pos[1] + float_offset)

        # 4. LÓGICA DE ENERGÍA [cite: 97]
        if self.state != "OFF":
            # El Rayo (BEAM) consume el doble de energía que la luz normal [cite: 92, 110]
            drain_rate = 0.01 if self.state == "BEAM" else 0.005
            self.energy -= drain_rate * dt
            
            if self.energy <= 0: 
                self.energy = 0
                self.set_state("OFF")

        # 5. ACTUALIZACIÓN DE COMPONENTES
        self.graphic.update(dt)
        if hasattr(self, 'light_graphic'):
            self.light_graphic.update(dt)

    def set_state(self, new_state):
        """Cambia el modo del Módulo de Inducción Lumínica [cite: 148, 152]"""
        self.state = new_state
        if self.state == "ON":
            self.light_graphic.visible = True
            self.light_graphic.setState("normal")
        elif self.state == "OFF":
            # Apagar para ocultarse de amenazas o ahorrar energía [cite: 93]
            self.light_graphic.visible = False 
        elif self.state == "BEAM":
            # Activar rayo concentrado para enemigos o mecanismos [cite: 72, 92, 96]
            self.light_graphic.visible = True
            self.light_graphic.setState("rayo")