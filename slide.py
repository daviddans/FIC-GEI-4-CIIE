import pygame
import numpy as np


def slice(image_path, tile_size, discard_uniform=False, variance_threshold=8, ratio_threshold=0.95):
    pygame.init()

    img = pygame.image.load(image_path)
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

            sprites.append({
                "surface": tile,
                "position": (x, y)
            })

    return sprites


# Ejemplo de uso
if __name__ == "__main__":
    image_path = "Assets/test/Tilesmap.png"
    tile_size = 16

    # Obtener la lista de sprites
    sprites = slice(image_path, tile_size, discard_uniform=True)


    # Guardar los sprites
    for index, sprite_data in enumerate(sprites):
        tile = sprite_data["surface"]
        pos = sprite_data["position"]
        filename = f"Assets/test/tile_{index}_pos{pos[0]}x{pos[1]}.png"
        pygame.image.save(tile, filename)
        print(f"Guardado {filename}")

    pygame.quit()