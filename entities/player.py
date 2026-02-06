import pygame
from src.settings import *

#Un objecto Sprite que tiene self.image (dibujo visual) y self.rect (es el esqueleto que define coordenadas, movimiento etc) 
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):

        super().__init__()

        #Ahora mismo un cuadrado rojo para hacer una prueba pero HAY QUE CAMBIARLO
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
         
        # x,y es 100 (su posicion) y de self-image ha copiado el alto y ancho (32 definido en settings). Rect sería (100, 100, 32, 32) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # valor de prueba
        self.speed = 5

 #Logica del jugador (movimientos etc). Ahora mismo vacío
    def update(self):
        self.input()   

# Lógica de teclas
    def input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed