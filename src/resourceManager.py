from configparser import ConfigParser

import pygame
import objects
import components
import os
import json
from utils import conf
from configparser import ConfigParser
class ResourceManager:
    _resources = {}

    #Gets an atlas component from cache or disk if it is not cached yet.
    @classmethod
    def getAtlas(cls, name):
        if name not in cls._resources:
                image, cood = cls._read_Atlas(name)
                atlas = components.Atlas(image, cood)
                cls._register(name, atlas)
                return atlas
        else:
            return cls._resources[name]
        
    @classmethod
    def getSound(cls, name):
        if name not in cls._resources:
            sound = cls._read_Sound(name)
            cls._register(name, sound)
            return sound
        else:
            return cls._resources[name]
    
    @classmethod
    def getConfig(cls):
        if "config" not in cls._resources:
            config = cls._read_Config()
            cls._register("config", config)
            return config
        else:
            return cls._resources["config"]
        
    #Cargar archivos que componen un atlas.
    def _read_Atlas(name):
        base_path = conf.get("engine", "assets_path")
        full_path = os.path.join(base_path, name)
        image = None
        cood = None
        extensions = [".png", ".jpeg"]
        for ext in extensions:
            if os.path.exists(full_path + ext):
                try:
                    image = pygame.image.load(full_path + ext)
                    break # Si la carga tiene éxito, salimos del bucle
                except Exception as e:
                    print(f"Error loading image '{full_path + ext}' : {e}")
                    raise e
        if image is None:
            raise FileNotFoundError(f"No se encontró el archivo de imagen para el atlas '{name}'")
        try:
            cood = json.load(open(full_path + ".json", "r"))
        except Exception as e:
            print(f"Error loading coordinates for atlas '{full_path}': {e}")
            raise e
        if cood is None:
            raise FileNotFoundError(f"No se encontró el archivo de coordenadas para el atlas '{name}'")
        return image, cood
    
    #Cargar archivos de sonido
    def _read_Sound(name):
        base_path = conf.get("engine", "assets_path")
        full_path = os.path.join(base_path, name)
        extensions = ['.wav', '.ogg', '.mp3']
        for ext in extensions:
            if os.path.exists(full_path + ext):
                try:
                    sound = pygame.mixer.Sound(full_path + ext)
                    return sound
                except Exception as e:
                    print(f"Error loading sound '{full_path + ext}' : {e}")
                    raise e
        raise FileNotFoundError(f"No se encontró el archivo de sonido para '{name}'")

    #Leer archivo de configuración
    def _read_Config():
        conf = ConfigParser()
        try:
            conf.read(filenames="config.ini", encoding="utf-8")
        except:
            raise FileNotFoundError("No se encuentra config.ini")
        return conf
""""
### Funciones antiguas de ale, las conservo de momento por si aca ###
    def get(cls, key):
        if key not in cls._resources:
            if "." in key: #si no se ha registrado el recurso, se intenta buscar en disco
                cls._resources[key] = cls.load_from_disk(key)
            else:
                print(f"Error: El recurso '{key}' no está registrado ni es un archivo.")
                return None
        return cls._resources[key]
    
    def _register(cls, key, instance):
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
    """