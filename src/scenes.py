# Script containing the logic for the various scenes composing the game.

import pygame

class Scene: #abstract
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


class Button():
    def __init__(self, img, x=0, y=0, scale=1):
        width = img.get_width()
        height = img.get_height()
        self.img = pygame.transform.scale(img, (int(width*scale), int(height * scale)))
        self.rect = self.img.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False

    def update(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
             if pygame.mouse.get_pressed()[0] == 1 and self.clicalejked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action
    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))


class MainMenu(Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        text = pygame.font.SysFont("Arial",32).render("Play",False,(100,100,100))
        self.playButton = Button(text, 100, 100, 3)
        text = pygame.font.SysFont("Arial",32).render("Settings",False,(100,100,100))
        self.settingsButton = Button(text, 100, 200, 3)
        text = pygame.font.SysFont("Arial",32).render("Quit",False,(100,100,100))
        self.quitButton = Button(text, 100, 300, 3)

    def update(self, dt):
        if self.playButton.update() == True :
            print("COMIENZA EL JUEGO")
        if self.settingsButton.update() == True :
            print("Se abren ajustes")
        if self.quitButton.update() == True :
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
