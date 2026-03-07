#Main script for run the game, contains the scene handling

import pygame
import sys
from pygame.locals import *
import scenes
from configparser import ConfigParser
from resourceManager import ResourceManager
from hud import DebugHUD

#ToDo: implement game as singletone for more security.
class Game:
    def __init__(self):
        pygame.init()
        # Buffer: 4096 (recomendado en apuntes para evitar cortes)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        self.config = ResourceManager.getConfig()
        self.screen = pygame.display.set_mode((self.config.getint("video", "xres"), self.config.getint("video", "xres")), 0, 32)
        self.sceneStack = [scenes.MainMenu(self,"mainmenu")]
        self.clock = pygame.time.Clock()

        # HUD de debug
        self.hud = DebugHUD(
            self.screen,
            self.config.getint("video", "xres"),
            self.config.getint("video", "xres")
        )
        
    def game_loop(self,scene):  
        self.sceneQuitFlg = False
        pygame.event.clear()
        while not self.sceneQuitFlg:
            dt = self.clock.tick(self.config.getint("video", "maxfps"))
            events = pygame.event.get()

            # Toggle HUD con F3
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.hud.toggle()

            scene.events(events)
            scene.update(dt)
            scene.draw()

            # HUD encima de todo
            # Buscamos el player en el stack (puede estar en una escena por debajo del diálogo)
            player_pos = (0, 0)
            for s in reversed(self.sceneStack):
                if hasattr(s, 'player'):
                    player_pos = s.player.pos
                    break

            dialogo_activo = scene.name if scene.name == "dialog" else None
            escena_nombre = next((s.name for s in reversed(self.sceneStack) if s.name != "dialog"), scene.name)

            self.hud.draw(
                fps=self.clock.get_fps(),
                jugador_pos=player_pos,
                escena=escena_nombre,
                dialogo_activo=dialogo_activo
            )

            pygame.display.update()

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



if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()