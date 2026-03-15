import pygame
import numpy as np
from resourceManager import ResourceManager

#Deprecated since the new atlas system
def sliceAtlas(image_path, discard_uniform=False, variance_threshold=8, ratio_threshold=0.95):
    pygame.init()
    conf = ResourceManager.getConfig()
    tile_size = conf.getint("engine","tile_size")
    img = pygame.image.load(conf.get("engine", "assets_path") + image_path)
    img_width, img_height = img.get_size()
    tiles_x = img_width // tile_size
    tiles_y = img_height // tile_size
    sprites = []

    for y in range(tiles_y):
        for x in range(tiles_x):
            # Extraer tile
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            tile = img.subsurface(rect).copy()

            # Verificar si es uniforme (si está activado)
            if discard_uniform:
                # arr tiene forma (ancho, alto, 3)
                arr = pygame.surfarray.array3d(tile)
                # intercambiamos ancho y alto para porocesar filas y columnas correctamente
                arr = np.transpose(arr, (1, 0, 2))
                # calculamos color promedio
                mean_color = np.mean(arr.reshape(-1, 3), axis=0)
                # distancia al color promedio
                diff = np.linalg.norm(arr - mean_color, axis=2)
                # comparamos distancia con umbral
                similar = diff <= variance_threshold
                # ratio de pixeles similares
                ratio = np.sum(similar) / similar.size

                if ratio >= ratio_threshold:
                    continue  # Saltar tiles uniformes

            sprites.append(tile)
    return sprites

class FadeTransition:
    def __init__(self, screen, speed=300):
        self.screen = screen
        self.speed = speed # Velocidad del fundido
        self.alpha = 0
        self.finished = False
        # Creamos una superficie negra del tamaño de la pantalla
        self.surface = pygame.Surface(self.screen.get_size())
        self.surface.fill((0, 0, 0))

    def update(self, dt):
        if self.finished: return
        
        # Subimos el alpha basándonos en el tiempo (dt)
        self.alpha += self.speed * dt
        if self.alpha >= 255:
            self.alpha = 255
            self.finished = True
        
        self.surface.set_alpha(int(self.alpha))

    def draw(self):
        self.screen.blit(self.surface, (0, 0))