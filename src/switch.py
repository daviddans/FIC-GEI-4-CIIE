import abstract
from resourceManager import ResourceManager
import components
import pygame
from dialog import Dialog


class Switch(abstract.Object, abstract.Observable):
    def __init__(self, pos, target_object=None):
        abstract.Object.__init__(self, "switch", pos)
        abstract.Observable.__init__(self)
        self.is_pressed = False
        self.target = target_object
        self.atlas = ResourceManager.getAtlas("interruptor")
        self.graphic = components.Graphic(self, self.atlas, False, False)

        self.graphic.addName("switch-off", 0, 0)
        self.graphic.addName("switch-on", 1, 1)
        self.graphic.set("switch-off")
        self.interact_range = 50
        self.already_pressed = False

        # ── Diálogos propios del Switch ───────
        # Cada instancia puede sobreescribir estas listas para
        # tener diálogos distintos según el interruptor.
        self.dialogs = {
            "SWITCH_ON": [
                Dialog("Sistema", "Interruptor activado."),
                Dialog("Sistema", "Algunos caminos se han abierto..."),
            ],
            "SWITCH_OFF": [
                Dialog("Sistema", "Interruptor apagado."),
            ],
        }

    def get_dialog(self, event: str) -> list[Dialog]:
        #La escena llama a esto para obtener las líneas del diálogo.
        return self.dialogs.get(event, [])

    def update(self, dt, player_pos):
        self.graphic.update(dt)
        p_vec = pygame.Vector2(player_pos)
        s_vec = pygame.Vector2(self.pos)
        distance = s_vec.distance_to(p_vec)
        keys = pygame.key.get_pressed()

        if distance < self.interact_range and keys[pygame.K_e]:
            if not self.already_pressed:
                self.toggle()
                self.already_pressed = True
        else:
            self.already_pressed = False

    def toggle(self):
        self.is_pressed = not self.is_pressed
        if self.is_pressed:
            self.graphic.set("switch-on")
            print("Interruptor encendido")
            self.notify(self, "SWITCH_ON")
        else:
            self.graphic.set("switch-off")
            print("Interruptor apagado")
            if self.target:
                self.target.lock()
            self.notify(self, "SWITCH_OFF")