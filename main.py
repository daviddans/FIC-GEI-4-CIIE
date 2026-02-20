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

        #Estado del dialogo
        self.dialog_active = False 
        
        #Fuente para el texto 
        self.font = pygame.font.SysFont('Arial', 24)

        # 1. Crear el grupo de sprites
        self.all_sprites = pygame.sprite.Group()
        
        # Lo pongo en la posicion 100,1000
        self.player = Player(100, 100)

        self.all_sprites.add(self.player)

 # 2. El Bucle Principal (Game Loop)
    def run(self):
        while self.running:
            self.events()

            # Solo actualiza si no hay un dialogo activo
            if not self.dialog_active:
                self.update()
                
            self.draw()
            self.clock.tick(FPS)

# Necesario para poder cerrar la ventana
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Activar diálogo con D
                if event.key == pygame.K_d:
                    self.dialog_active = True

                # Cerrar diálogo con ENTER
                if event.key == pygame.K_RETURN and self.dialog_active:
                    self.dialog_active = False


# Para los sprites
    def update(self):
        self.all_sprites.update()

# Necesario para pintar el fondo negro
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen) 

        # Si hay diálogo activo → dibujarlo encima
        if self.dialog_active:
            self.draw_dialog()

        pygame.display.flip()

    def draw_dialog(self):
        # Capa oscura semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Caja de diálogo
        dialog_rect = pygame.Rect(100, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 200, 120)
        pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), dialog_rect, 3)

        # Texto
        text_surface = self.font.render(
            "Has encontrado algo misterioso... (ENTER para continuar)",
            True,
            (0, 0, 0)
        )

        self.screen.blit(text_surface, (dialog_rect.x + 20, dialog_rect.y + 45))


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
