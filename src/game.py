#Main script for run the game, contains the scene handling

import pygame
import sys
import os
from pygame.locals import *
import scenes
from resourceManager import ResourceManager
from debugLogger import DebugLogger

DEF_FLAGS = pygame.SHOWN | pygame.NOFRAME
#ToDo: implement game as singletone for more security.
class Game:
    def __init__(self):
        pygame.init()
        # Buffer: 4096 (recomendado en apuntes para evitar cortes)
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        self.config = ResourceManager.getConfig()
        cfg = self.config
        DebugLogger.init(
            enabled=cfg.getboolean("debug", "enabled", fallback=False),
            log_path=os.path.join(cfg.get("PATH", "user_path"), "debug.log")
        )

        DebugLogger.log("\n" * 5 + "_" * 100 + "\n" *5 + "*" * 30 +"\n*--- LAUNCHING UNLIGHTED ---*\n" + "*" * 30 + "\n" * 5)

        # Configurar pantalla al arrancar — con validación
        try:
            xres  = cfg.getint('video', 'xres')
            yres  = cfg.getint('video', 'yres')
            fs    = cfg.getboolean('video', 'fullscreen')
            scale = cfg.getint('video', 'scale')
            rw    = cfg.getint('engine', 'width')
            rh    = cfg.getint('engine', 'height')

            desktop = pygame.display.get_desktop_sizes()[0]
            if not fs and (xres > desktop[0] or yres > desktop[1]):
                xres, yres = min(xres, desktop[0]), min(yres, desktop[1])
            if scale < 1:
                scale = max(1, min(xres // rw, yres // rh))

            cfg.set('video', 'xres', str(xres))
            cfg.set('video', 'yres', str(yres))
            cfg.set('video', 'scale', str(scale))
        except (ValueError, KeyError):
            DebugLogger.log("WARN: config video inválido, usando defaults seguros")
            xres, yres, fs = 1920, 1080, False
            cfg.set('video', 'xres', '1920')
            cfg.set('video', 'yres', '1080')
            cfg.set('video', 'fullscreen', '0')
            cfg.set('video', 'scale', '3')

        self.set_video_mode(xres, yres, fs)
        pygame.display.set_caption(self.config.get('engine', 'title', fallback='Unlighted'))
        self.sceneStack = [scenes.MainMenu(self,"MainMenu")]
        self.clock = pygame.time.Clock()
        
    def set_video_mode(self, width, height, fullscreen):
        flags = DEF_FLAGS | pygame.FULLSCREEN if fullscreen else DEF_FLAGS
        self.screen = pygame.display.set_mode((width, height), flags=flags)

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

            if dt != 0: print("FPS: %s", 1 / dt * 1000) # Mostramos los fps por consola

    def run(self):
        while (len(self.sceneStack) > 0):
            scene = self.sceneStack[-1]
            self.game_loop(scene)
    
    def quitScene(self):
        try:
            popped = self.sceneStack.pop()
            DebugLogger.log("quitScene: '%s' (stack size now %d)", popped.name, len(self.sceneStack))
            self.sceneQuitFlg = True  # salir del game_loop para que run() coja la siguiente escena
        except IndexError:
            pass
    
    def quitGame(self):
        ResourceManager.apply_pending()
        cfg = ResourceManager.getConfig()
        with open("config.ini", "w", encoding="utf-8") as f:
            cfg.write(f)
        self.sceneStack.clear()
        self.sceneQuitFlg = True

    def changeScene(self, scene):
        DebugLogger.log("changeScene -> '%s'", scene.name)
        self.sceneQuitFlg = True #para actualizar el motor
        self.quitScene() #without comeback
        self.sceneStack.append(scene)
        

    def switchScene(self, scene):
        DebugLogger.log("switchScene -> '%s' (stack size now %d)", scene.name, len(self.sceneStack) + 1)
        self.sceneQuitFlg = True #with comeback
        self.sceneStack.append(scene)

    
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()