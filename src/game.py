import pygame
import sys
from pygame.locals import *
import scenes
from configparser import ConfigParser
from resourceManager import ResourceManager
from hud import DebugHUD


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        self.config = ResourceManager.getConfig()
        self.screen = pygame.display.set_mode((self.config.getint("video", "xres"), self.config.getint("video", "yres")), 0, 32)
        self.sceneStack = [scenes.MainMenu(self, "mainmenu")]
        self.clock = pygame.time.Clock()

        self.hud = DebugHUD(
            self.screen,
            self.config.getint("video", "xres"),
            self.config.getint("video", "yres")
        )

    def game_loop(self, scene):
        self.sceneQuitFlg = False
        pygame.event.clear()
        while not self.sceneQuitFlg:
            dt = self.clock.tick(self.config.getint("video", "maxfps"))
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.hud.toggle()

            active = self.sceneStack[-1]
            active.events(events)
            active.update(dt)
            active.draw()

            player_pos = (0, 0)
            for s in reversed(self.sceneStack):
                if hasattr(s, "player"):
                    player_pos = s.player.pos
                    break

            escena_nombre = next(
                (s.name for s in reversed(self.sceneStack) if s.name != "dialog"),
                active.name
            )

            dialogo_activo = None
            if active.name == "dialog":
                dm = active.dialog_manager
                dlg = dm.get_current_dialog()
                if dlg:
                    current  = dm.current_dialog_index + 1
                    total    = len(dm.dialogs)
                    dialogo_activo = {
                        "hablante": dlg.name,
                        "texto":    dlg.text,
                        "progreso": f"{current}/{total}",
                    }

            self.hud.draw(
                fps=self.clock.get_fps(),
                jugador_pos=player_pos,
                escena=escena_nombre,
                dialogo_activo=dialogo_activo
            )

            pygame.display.update()

    def run(self):
        while len(self.sceneStack) > 0:
            scene = self.sceneStack[-1]
            self.game_loop(scene)

    def quitScene(self):
        try:
            self.sceneStack.pop()
            self.sceneQuitFlg = True
        except IndexError:
            pass

    def quitGame(self):
        self.sceneStack.clear()
        self.sceneQuitFlg = True

    def changeScene(self, scene):
        self.sceneQuitFlg = True
        self.quitScene()
        self.sceneStack.append(scene)

    def switchScene(self, scene):
        self.sceneStack.append(scene)
        self.sceneQuitFlg = True

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()