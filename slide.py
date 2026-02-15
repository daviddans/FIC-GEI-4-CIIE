from PIL import Image
import numpy as np


def load_image(image_path):
    return Image.open(image_path)


def is_uniform_tile(tile, variance_threshold=8, ratio_threshold=0.95):
    # Detecta si un tile es de color uniforme.
    arr = np.array(tile.convert("RGB"))
    mean_color = np.mean(arr.reshape(-1, 3), axis=0)
    diff = np.linalg.norm(arr - mean_color, axis=2)
    similar = diff <= variance_threshold
    ratio = np.sum(similar) / similar.size
    return ratio >= ratio_threshold


def create_tilemap(img, tile_size):
    img_width, img_height = img.size
    tiles_x = img_width // tile_size
    tiles_y = img_height // tile_size

    tilemap = []
    for y in range(tiles_y):
        for x in range(tiles_x):
            left = x * tile_size
            upper = y * tile_size
            right = left + tile_size
            lower = upper + tile_size

            tile = img.crop((left, upper, right, lower))
            tilemap.append({
                "image": tile,
                "position": (x, y),
            })

    return tilemap


def export_tiles(tilemap, discard_uniform=False):
    useful_tiles = []
    discarded = 0

    for tile_data in tilemap:
        tile = tile_data["image"]
        pos = tile_data["position"]

        if discard_uniform and is_uniform_tile(tile):
            discarded += 1
            continue

        useful_tiles.append(tile_data)

    for index, tile_data in enumerate(useful_tiles):
        tile = tile_data["image"]
        pos = tile_data["position"]
        filename = f"Assets/test/tile_{index}_pos{pos[0]}x{pos[1]}.png"
        tile.save(filename)
        print(f"Guardado {filename}")


if __name__ == "__main__":
    image_path = "Assets/test/atlas1.png"
    tile_size = 16

    img = load_image(image_path)
    tilemap = create_tilemap(img, tile_size)

    # Exporta los tiles, descartando los uniformes o no
    # En casos como atlas1, desactivarlo y para el resto tenerlo activo
    export_tiles(tilemap, discard_uniform=False)
