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
# z_layer attribute may be deprecated as the blit order will now be handled by sprites and groups
class Object:
    def __init__(self, name="unamed", pos = (0,0), z_layer = 99):
        self.name = name
        self.pos = pos
        self.z_layer = z_layer

    def update(self, dt):
        raise NotImplementedError("Object: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Object: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Object: " + self.name + ". Draw method not found, must be given an implementation.\n")
