from PIL import Image
import numpy as np

def load_image(image_path):
    img = Image.open(image_path)
    return img

def is_background_tile(tile, bg_color=(0, 0, 0), threshold=0.95):
    tile_rgb = tile.convert("RGB")
    arr = np.array(tile_rgb)
    
    # Comparamos cada pixel con el color de fondo
    matches = np.all(arr == np.array(bg_color), axis=2)

    # Porcentaje de pixels que son fondo
    bg_ratio = np.sum(matches) / matches.size

    return bg_ratio >= threshold

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

if __name__ == "__main__":
    image_path = "TilesmapDavid.png"
    tile_size = 16
    img = load_image(image_path)
    tilemap = create_tilemap(img, tile_size)

    useful_tiles = []
    discarded = 0

    for tile_data in tilemap:
        tile = tile_data["image"]
        pos = tile_data["position"]
        
        if is_background_tile(tile, bg_color=(0, 0, 0), threshold=0.95):
            discarded += 1
        else:
            useful_tiles.append(tile_data)

    for index, tile_data in enumerate(useful_tiles):
        tile = tile_data["image"]
        pos = tile_data["position"]
        tile.save(f"tile_{index}_pos{pos[0]}x{pos[1]}.png")
        print(f"  Guardado tile_{index} en posicion {pos}")