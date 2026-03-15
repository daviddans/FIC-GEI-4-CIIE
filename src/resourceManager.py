from configparser import ConfigParser
import pygame
import os
import json
from pytmx.util_pygame import load_pygame

class ResourceManager:
    #Cache dictionary
    _resources = {}
    # Cambios de config pendientes — no se aplican al config live hasta apply_pending()
    _pending = {}  # {(section, key): value}
    #Gets an atlas component from cache or disk if it is not cached yet.
    @classmethod
    def getAtlas(cls, name):
        import components
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
    #Gets a json file 
    @classmethod
    def getJSON(cls, name):
        if name not in cls._resources:
            json_data = cls._read_JSON(name)
            cls._resources[name] = json_data
            return json_data
        else:
            return cls._resources[name]
    @classmethod
    def getFont(cls, name, size):
        key = f"{name}:{size}"
        if key not in cls._resources:
            base_path = cls.getConfig().get("PATH", "fonts_path")
            full_path = os.path.join(base_path, name)
            try:
                font = pygame.font.Font(full_path, size)
            except Exception as e:
                print(f"Error cargando fuente '{full_path}': {e}")
                raise e
            cls._resources[key] = font
        return cls._resources[key]

    @classmethod
    def set_pending(cls, section, key, value):
        """Guarda un cambio de config sin aplicarlo al config live."""
        cls._pending[(section, key)] = value

    @classmethod
    def apply_pending(cls):
        """Vuelca los cambios pendientes al config en memoria (llamar antes de escribir a disco)."""
        cfg = cls.getConfig()
        for (section, key), value in cls._pending.items():
            cfg.set(section, key, value)
        cls._pending.clear()

    @classmethod
    def remove_key(cls, name):
        try:
            cls._resources.pop(name)
        except KeyError:
            print(f"Key {name} not found in cache")
        except Exception as e :
            raise e
    
    @classmethod
    def clear_cache(cls):
        try:
            cls._resources.clear()
        except Exception as e :
            raise e

    #Cargar de disco un archivo tmx
    def _read_TileMap(name):
        base_path = ResourceManager.getConfig().get("PATH", "maps_path")
        full_path = os.path.join(base_path, name +".tmx")
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"No se encontró el tilemap: {full_path}")
        try:
            return load_pygame(full_path)
        except Exception as e:
            print(f"Error loading tilemap '{full_path}': {e}")
            raise e
    
    #Cargar de disco archivos que componen un atlas.
    def _read_Atlas(name):
        base_path = ResourceManager.getConfig().get("PATH", "sprites_path")
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
            raise FileNotFoundError(f"No se encontró el archivo de imagen para el atlas {name}")
        try:
            with open(full_path + ".json", "r") as f:
                cood = json.load(f)
        except Exception as e:
            print(f"Error loading coordinates for atlas '{full_path}': {e}")
            raise e
        if cood is None:
            raise FileNotFoundError(f"No se encontró el archivo de coordenadas para el atlas '{name}'")
        return image, cood
    
    #Cargar de disco archivos de sonido
    def _read_Sound(name):
        base_path = ResourceManager.getConfig().get("PATH", "sounds_path")
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

    #Leer archivo de configuración de disco
    def _read_Config():
        conf = ConfigParser()
        try:
            conf.read(filenames="config.ini", encoding="utf-8")
        except:
            raise FileNotFoundError("No se encuentra config.ini")
        return conf
    
    #Leer un json de disco
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