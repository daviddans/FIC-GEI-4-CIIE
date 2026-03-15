from abc import ABC, abstractmethod
import pygame
from resourceManager import ResourceManager
from debugLogger import DebugLogger

class Scene:
    def __init__(self, game, name="unnamed"):
        self.game = game
        self.name = name
        DebugLogger.log("\n---Scene init: '%s'---\n", name)

    def update(self, dt):
        raise NotImplementedError("Scene: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Scene: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Scene: " + self.name + ". Draw method not found, must be given an implementation.\n")

class Object:
    def __init__(self, name="unnamed", pos = (0,0)):
        DebugLogger.log("Object init: '%s'", name)
        scale = ResourceManager.getConfig().getint("video", "scale")
        self.name = name
        self.pos = pygame.rect.Rect((pos[0] * scale , pos[1] * scale), (0,0))
  
    def update(self, dt):
        raise NotImplementedError("Object: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Object: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def on_collision(self, _other):
        pass
    
    #para que las entidades guarden sus datos para el json de fase
    def serialize(self):
        raise NotImplementedError("Object: " + self.name + ". Serialize method not found, must be given an implementation.\n")
    #para recuperar los datos guardados
    def unserialize(self, data):
        raise NotImplementedError("Object: " + self.name + ". Serialize method not found, must be given an implementation.\n")
    

class Observer(ABC):
    # Cualquier objeto que reacciona a algo (puertas)
    @abstractmethod
    def on_notify(self, entity, event):
        pass

class Observable:
    # Cualquier objeto que sea un emisor de eventos (interruptores)
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify(self, entity, event):
        DebugLogger.log("Observable notify: entity='%s' event='%s' observers=%d",
                        getattr(entity, "name", repr(entity)), event, len(self.observers))
        for observer in self.observers:
            observer.on_notify(entity, event)

class Behavior(ABC):
    @abstractmethod
    def update(self, npc, dt):
        pass