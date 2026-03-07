from configparser import ConfigParser

import pygame
import objects
import components
import os
import json
from configparser import ConfigParser
from pytmx.util_pygame import load_pygame

class ResourceManager:
    #Cache dictionary
    _resources = {}
    #Gets an atlas component from cache or disk if it is not cached yet.
    @classmethod
    def getAtlas(cls, name):
        if name not in cls._resources:
                image, cood = cls._read_Atlas(name)
                atlas = components.Atlas(image, cood)
                cls._resources[name] = atlas
                return atlas
        else:
            return cls._resources[name]
    #Gets a sound from cache or disk if it is not cached yet.
    @classmethod
    def getSound(cls, name):
        if name not in cls._resources:
            sound = cls._read_Sound(name)
            cls._resources[name] = sound
            return sound
        else:
            return cls._resources[name]
    #Gets the config parser from cache or disk if it is not cached yet.
    @classmethod
    def getConfig(cls):
        if "config" not in cls._resources:
            config = cls._read_Config()
            cls._resources["config"] = config
            return config
        else:
            return cls._resources["config"]
    #Gets a tilemap from cache or disk if it is not cached yet.
    @classmethod
    def getTileMap(cls, name):
        if name not in cls._resources:
            tmx = cls._read_TileMap(name)
            cls._resources[name] = tmx
            return tmx
        else:
            return cls._resources[name]
    
    @classmethod
    def getJSON(cls, name):
        if name not in cls._resources:
            json_data = cls._read_JSON(name)
            cls._resources[name] = json_data
            return json_data
        else:
            return cls._resources[name]

    #Cargar un archivo tmx
    def _read_TileMap(name):
        base_path = ResourceManager.getConfig().get("engine", "assets_path")
        full_path = os.path.join(base_path, name +".tmx")
        if os.path.exists(full_path):
            try:
                tmx_data = load_pygame(full_path)
                return tmx_data
            except Exception as e:
                print(f"Error loading tilemap '{full_path}': {e}")
                raise e
        return tmx_data
    
    #Cargar archivos que componen un atlas.
    def _read_Atlas(name):
        base_path = ResourceManager.getConfig().get("engine", "assets_path")
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
        base_path = ResourceManager.getConfig().get("engine", "assets_path")
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
    
    @staticmethod
    def _read_JSON(name):
        # Usamos el config para saber dónde están los assets
        base_path = ResourceManager.getConfig().get("engine", "assets_path")
        
        # Si el nombre ya trae extensión (como .tmj), lo usamos; si no, ponemos .json
        filename = name if "." in name else name + ".json"
        full_path = os.path.join(base_path, filename)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error fatal leyendo JSON en '{full_path}': {e}")
                raise e
        else:
            raise FileNotFoundError(f"No se encontró el archivo JSON en: {full_path}")
    

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