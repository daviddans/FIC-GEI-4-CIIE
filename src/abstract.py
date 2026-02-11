class Scene: 
    def __init__(self, game, objects=[], name="unamed"):
        self.game = game
        self.name = name
        self.objects = objects
    
    def update(self, dt):
        raise NotImplementedError("Scene: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Scene: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Scene: " + self.name + ". Draw method not found, must be given an implementation.\n")

class Object:
    def __init__(self, name="unamed", z_layer = -1):
        self.name = name
        self.z_layer = z_layer

    def update(self, dt):
        raise NotImplementedError("Object: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Object: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Object: " + self.name + ". Draw method not found, must be given an implementation.\n")
