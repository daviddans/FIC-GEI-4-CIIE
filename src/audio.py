import pygame
import os
from configparser import ConfigParser
import utils

class SoundManager:
    def __init__(self):
        # Buffer: 4096 (recomendado en apuntes para evitar cortes)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()
        self.sounds = {}
        self.music_loaded = None

        self.config = utils.getConfig()

   # ---------------------- SONIDOS ---------------------------------------------------------------

    def load_sound(self, name, relative_path):
        path = os.path.join(self.config.get("engine", "assets_path"), relative_path)
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Error cargando sonido {name}: {e}")


    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

  # ------------------------- MUSICA ----------------------------------------------------------------

    def load_music(self, relative_path):
        path = os.path.join(self.config.get("engine", "assets_path"), relative_path)
        try:
            pygame.mixer.music.load(path)
            self.music_loaded = path
        except pygame.error as e:
            print(f"Error cargando musica: {e}")

    def play_music(self, loop=True):
        # loops=-1 significa infinito, loops=0 es una sola vez
        loops = -1 if loop else 0
        try:
            pygame.mixer.music.play(loops)
        except Exception as e:
            print(f"Error al reproducir música: {e}")
