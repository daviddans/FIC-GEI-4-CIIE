#Main script for run the game, contains the scene handling

import pygame
import sys
from pygame.locals import *
import settings
import scenes
#ToDo: implement game as singletone for more security.
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((settings.XSIZE,settings.YSIZE),0,32)
        self.sceneStack = [scenes.MainMenu(self,"mainmenu")]
        self.clock = pygame.time.Clock()

    def game_loop(self,scene):
        self.sceneQuitFlg = False
        pygame.event.clear()
        while not self.sceneQuitFlg:
            dt = self.clock.tick(settings.MAXFPS)
            scene.events(pygame.event.get())
            scene.update(dt)
            scene.draw()

    def run(self):
        while (len(self.sceneStack) > 0):
            scene = self.sceneStack[-1]
            self.game_loop(scene)
    
    def quitScene(self):
        try:
            self.sceneStack.pop()
        except IndexError:
            pass
    
    def quitGame(self):
        self.sceneStack.clear()
        self.sceneQuitFlg = True

    def changeScene(self, scene):
        self.quitScene() #without comebakc
        self.sceneStack.append(scene)

    def switchScene(self, scene):
        self.sceneQuitFlg = True #with comeback
        self.sceneStack.append(scene)



if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()