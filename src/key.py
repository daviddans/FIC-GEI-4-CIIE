import abstract
from resourceManager import ResourceManager
import components
import pygame


class Key(abstract.Object):
    def __init__(self, pos, **kwargs):
        super().__init__("key", pos)
        self.key_id = kwargs.get("key_id", "default_key")
        self.graphic = components.Graphic(self, ResourceManager.getAtlas("key"))
        self.graphic.setState("idle")

    def interact(self, player):
        # Añadir el ID a la lista del jugador
        if self.key_id not in player.keys:
            player.keys.append(self.key_id)
            print(f"Llave {self.key_id} recogida")
            self.kill() # Desaparece del mundo