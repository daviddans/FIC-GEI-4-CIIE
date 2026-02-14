import pygame
from configparser import ConfigParser

def getConfig():
    conf = ConfigParser()
    try:
        conf.read(filenames="config.ini", encoding="utf-8")
    except:
        raise FileNotFoundError("No se encuentra config.ini")
    return conf

#Funcion para dividir automaticamente un atlas en un array de
#imagenes. La implementacion la esta trabajando elena, queda como 
#mockup porque la necesito yo tmb
def sliceAtlas():
    conf = getConfig()
    return pygame.image.load(conf.get("engine","assets_path") + "/player.png")