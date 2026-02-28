import pygame
import os
from configparser import ConfigParser
import utils
from resource_manager import ResourceManager 
class SoundManager:
    def __init__(self):
        # Buffer: 4096 (recomendado en apuntes para evitar cortes)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.mixer.init()
        self.sounds = {}
        self.music_loaded = None
        self.config = utils.conf

    def play_sound(self, path):
        sound = ResourceManager().get(path)
        if sound:
            sound.play()

#He metido la carga y el play de la música en una función para evitar tener funciones separadas por simplicidad
    def play_music(self, path, loop=True):    
        base_path = self.config.get("engine", "assets_path")
        full_path = os.path.join(base_path, path)
        
        pygame.mixer.music.load(full_path)
        loops = -1 if loop else 0
        pygame.mixer.music.play(loops)
