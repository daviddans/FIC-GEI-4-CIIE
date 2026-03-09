from resourceManager import ResourceManager
import components

class HealthHUD:
    def __init__(self, player):
        self.player = player
        self.atlas = ResourceManager.getAtlas("hearts")
        self.graphic = components.Graphic(None, self.atlas)
        self.graphic.addState("full", [0])
        self.graphic.addState("half", [1])
        self.graphic.addState("empty", [2])

    def draw(self, screen):
        scale = ResourceManager.getConfig().getint("video", "scale")
        heart_size = 16 * scale
        
        margin_x = 15 
        margin_y = 15
        # se itera según la vida máxima definida (max_hp)
        for i in range(self.player.health.max_hp):
            x = margin_x + (i * heart_size)
            y = margin_y
            
            #  lógica de estado inicial
            if i < int(self.player.health.current_hp):
                self.graphic.setState("full")
            elif i < self.player.health.current_hp:
                self.graphic.setState("half")
            else:
                self.graphic.setState("empty")
            
            self.graphic.rect.topleft = (x, y)
            screen.blit(self.graphic.image, self.graphic.rect)