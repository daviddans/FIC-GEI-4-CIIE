import pygame
import sys
from src.settings import *

# Clase Principal que envuelve todo (Patron Game Loop)
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Project Light: Adalario (2D)")
        self.clock = pygame.time.Clock()
        self.running = True