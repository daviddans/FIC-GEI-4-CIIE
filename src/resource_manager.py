import pygame
import os
import json

class ResourceManager:
    _resources = {}

    def get(cls, key):
        if key not in cls._resources:
            if "." in key: #si no se ha registrado el recurso, se intenta buscar en disco
                cls._resources[key] = cls.load_from_disk(key)
            else:
                print(f"Error: El recurso '{key}' no está registrado ni es un archivo.")
                return None
        return cls._resources[key]
    
    def register(cls, key, instance):
        #almacena instancias en _resources
        cls._resources[key] = instance
    
    #para recursos estáticos tipo imagenes, jsons y sonidos (de momento)
    def load_from_disk(cls, path):

        base_path = cls.get("config").get("engine", "assets_path")
        full_path = os.path.join(base_path, path)
        extension = path.split('.')[-1].lower()
        
        if extension in ['png', 'jpg']:
            return pygame.image.load(full_path).convert_alpha()
        elif extension == 'json':
            with open(full_path, 'r') as f:
                return json.load(f)
            
        elif extension in ['wav', 'ogg', 'mp3']:
            return pygame.mixer.Sound(full_path)
        
        raise Exception(f"Formato no soportado: {extension}")