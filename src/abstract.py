from abc import ABC, abstractmethod
import pygame

class Scene: 
    def __init__(self, game, name="unamed"):
        self.game = game
        self.name = name
        self.objects = []
    
    def addObject(self, obj):
        self.objects.append(obj)

    def getObjects(self):
        return self.objects

    def removeObject(self, obj):
        self.objects.remove(obj)

    def update(self, dt):
        raise NotImplementedError("Scene: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Scene: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Scene: " + self.name + ". Draw method not found, must be given an implementation.\n")

class Object:
    def __init__(self, name="unamed", pos = (0,0)):
        self.name = name
        self.pos = pygame.rect.Rect(pos, (0,0))
  
    def update(self, dt):
        raise NotImplementedError("Object: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Object: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Object: " + self.name + ". Draw method not found, must be given an implementation.\n")
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
        for observer in self.observers:
            observer.on_notify(entity, event)