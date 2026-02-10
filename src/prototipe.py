import pygame
import sys
from pygame.locals import *

#GlobalSettings (this belongs to another file )
XSIZE = 800
YSIZE = 800
MAXFPS = 10

class Scene:
    def __init__(self, game, name="unamed"):
        self.game = game
        self.name = name
    
    def update(self, dt):
        raise NotImplementedError("Scene: " + self.name + ". Update method not found, must be given an implementation.\n")
    
    def events(self, events):
        raise NotImplementedError("Scene: " + self.name + ". Events method not found, must be given an implementation.\n")
    
    def draw(self):
        raise NotImplementedError("Scene: " + self.name + ". Draw method not found, must be given an implementation.\n")

#tutorial from pygamece docs for testing
class TestScene01(Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        self.playerpos= pygame.Vector2(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2)
    
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

    def update(self, dt):
        print(dt)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.playerpos.y -= 1 * dt
        if keys[pygame.K_s]:
            self.playerpos.y += 1 * dt
        if keys[pygame.K_a]:
            self.playerpos.x -= 1 * dt
        if keys[pygame.K_d]:
            self.playerpos.x += 1 * dt

    def draw(self):
        screen = self.game.screen
        screen.fill("purple")
        pygame.draw.circle(screen, "red", self.playerpos, 40)
        pygame.display.flip()

#ToDo: implement game as singletone for more security.
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((XSIZE,YSIZE),0,32)
        self.sceneStack = [TestScene01(self,name="01")]
        self.clock = pygame.time.Clock()

    def game_loop(self,scene):
        self.sceneQuitFlg = False
        pygame.event.clear()
        while not self.sceneQuitFlg:
            dt = self.clock.tick(MAXFPS)
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