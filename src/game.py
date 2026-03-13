#Main script for run the game, contains the scene handling

import pygame
import sys
from pygame.locals import *
import scenes
from resourceManager import ResourceManager

DEF_FLAGS = pygame.SHOWN | pygame.NOFRAME
#ToDo: implement game as singletone for more security.
class Game:
    def __init__(self):
        pygame.init()
        # Buffer: 4096 (recomendado en apuntes para evitar cortes)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        self.config = ResourceManager.getConfig()
        self.updateDisplay()
        self.sceneStack = [scenes.MainMenu(self,"MainMenu")]
        self.clock = pygame.time.Clock()
        
    def game_loop(self,scene):  
        self.sceneQuitFlg = False
        pygame.event.clear()
        while not self.sceneQuitFlg:
            dt = self.clock.tick(self.config.getint("video", "maxfps"))
            events = pygame.event.get()

            scene.events(events)
            scene.update(dt)
            scene.draw()
            pygame.display.flip()

            if dt != 0 : print(f"FPS:{1 / dt * 1000}")

    def run(self):
        while (len(self.sceneStack) > 0):
            scene = self.sceneStack[-1]
            self.game_loop(scene)
    
    def quitScene(self):
        try:
            self.sceneStack.pop()
            self.sceneQuitFlg = True  # salir del game_loop para que run() coja la siguiente escena
        except IndexError:
            pass
    
    def quitGame(self):
        self.sceneStack.clear()
        self.sceneQuitFlg = True

    def changeScene(self, scene):
        self.sceneQuitFlg = True #para actualizar el motor
        self.quitScene() #without comeback
        self.sceneStack.append(scene)
        

    def switchScene(self, scene):
        self.sceneQuitFlg = True #with comeback
        self.sceneStack.append(scene)

    def updateDisplay(self):
        #Reload config
        ResourceManager.remove_key("config")
    
        xres = ResourceManager.getConfig().getint("video", "xres")
        yres = ResourceManager.getConfig().getint("video", "yres")
        fullscren = ResourceManager.getConfig().getint("video", "fullscreen")
        #Aply new settings
        if fullscren : flags = DEF_FLAGS | pygame.FULLSCREEN
        else : flags = DEF_FLAGS
        self.screen = pygame.display.set_mode((xres, yres), flags=flags)
        pygame.display.set_caption(ResourceManager.getConfig().get("engine", "title", fallback="Unighted"))
    
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()