import pygame
import numpy as np
from configparser import ConfigParser
from resource_manager import ResourceManager

#The __ makes it private (only available inside the module)
def __getConfig():
    conf = ConfigParser()
    try:
        conf.read(filenames="config.ini", encoding="utf-8")
    except:
        raise FileNotFoundError("No se encuentra config.ini")
    return conf

#singleton like pattern (Its not really a singletone but works better on python)
conf = __getConfig()

def sliceAtlas(image_path, discard_uniform=False, variance_threshold=8, ratio_threshold=0.95):
    pygame.init()
    conf = ResourceManager().get("config") 
    tile_size = conf.getint("engine","tile_size")
    img = ResourceManager().get(image_path)
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