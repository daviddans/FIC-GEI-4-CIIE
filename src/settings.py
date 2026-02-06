
import os

# Configuracion de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Colores (R, G, B): colores basicos de momento
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)    
GREEN = (0, 255, 0)   
BLUE  = (0, 0, 255)

# Rutas para la carga de imagenes
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')