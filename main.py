import pygame
import sys
from src.settings import *
from entities.player import Player

# Clase Principal que envuelve todo (Patron Game Loop)
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Project Light: Adalario (2D)")
        self.clock = pygame.time.Clock()
        self.running = True

        # 1. Crear el grupo de sprites
        self.all_sprites = pygame.sprite.Group()
        
        # Lo pongo en la posicion 100,1000
        self.player = Player(100, 100)

        self.all_sprites.add(self.player)

 # 2. El Bucle Principal (Game Loop)
    def run(self):
        while self.running:
            self.events()
            #self.update()
            self.draw()
            self.clock.tick(FPS)

# Necesario para poder cerrar la ventana
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

# Para los sprites
    def update(self):
        self.all_sprites.update()

# Necesario para pintar el fondo negro
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen) 
        pygame.display.flip()


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
