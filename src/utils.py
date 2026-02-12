import pygame
from configparser import ConfigParser

def getConfig():
    conf = ConfigParser()
    try:
        conf.read(filenames="config.ini", encoding="utf-8")
    except:
        raise FileNotFoundError("No se encuentra config.ini")
    return conf