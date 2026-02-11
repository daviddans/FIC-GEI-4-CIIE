# Script containing the logic for the various scenes composing the game.

import pygame
import components
import player
import game
import abstract


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

class TestScene02(Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        self.player = player.Player()

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

    def update(self, dt):
        self.player.upddate(dt)

    def draw(self):
        screen = self.game.screen
        screen.fill("purple")
        self.player.draw(screen)
        pygame.display.update()

class MainMenu(Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        text = pygame.font.SysFont("Arial",32).render("Play",False,(100,100,100))
        self.playButton = components.Button(text, 100, 100, 3)
        text = pygame.font.SysFont("Arial",32).render("Settings",False,(100,100,100))
        self.settingsButton = components.Button(text, 100, 200, 3)
        text = pygame.font.SysFont("Arial",32).render("Quit",False,(100,100,100))
        self.quitButton = components.Button(text, 100, 300, 3)

    def update(self, dt):
        if self.playButton.update() == True :
            print("COMIENZA EL JUEGO")
            self.game.switchScene(TestScene02(self.game, name="test"))
        if self.settingsButton.update() == True :
            print("Se abren ajustes")
        if self.quitButton.update() == True :
            print("Adios")
            self.game.quitGame()

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

    def draw(self):
        screen = self.game.screen
        screen.fill("white")
        self.playButton.draw(screen)
        self.settingsButton.draw(screen)
        self.quitButton.draw(screen)
        pygame.display.update()
