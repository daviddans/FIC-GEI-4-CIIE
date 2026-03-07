# Script containing the logic for the various scenes composing the game.

import pygame
import components
import player
import objects
import abstract
import audio
import utils
import dialog
from resourceManager import ResourceManager



class TestScene(abstract.Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        self.player = player.Player()

        config = ResourceManager.getConfig()
        self.bg = pygame.image.load(config.get("engine","assets_path") + "background.png")
        self.camera = objects.Camera()
        self.testGroup = pygame.sprite.Group()
        self.map = objects.tileMap("testMap")
        self.map.sprite.add(self.testGroup)

        self.trees = []
        for i in range(0, 10):
            tree = objects.testTree()
            tree.sprite.add(self.testGroup)
            self.trees.append(tree)

        self.player.graphic.add(self.testGroup)
        self.camera.addGroup(self.testGroup)
        self.camera.setReference(self.player)

        self._in_tree_collision = False

    def _check_tree_collision(self):
        px, py = self.player.pos
        touching_tree = False
        for tree in self.trees:
            if tree.get_rect().collidepoint(px, py):
                touching_tree = True
                if not self._in_tree_collision:
                    self._in_tree_collision = True
                    dm = dialog.DialogManager()
                    dm.add_dialog(dialog.Dialog("", "Esto es un árbol."))
                    self.game.switchScene(dialog.DialogScene(self.game, dm))
                return
        # si ya no toca ningún árbol, resetea el flag
        if not touching_tree:
            self._in_tree_collision = False
        
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:

                    dm = dialog.DialogManager()
                    dm.load_from_csv("dialogs/test_dialog.csv")

                    dialog_scene = dialog.DialogScene(self.game, dm)
                    self.game.switchScene(dialog_scene)

    def update(self, dt):
        self.player.update(dt)
        self.testGroup.update(dt)
        self.camera.update(dt)
        self._check_tree_collision()
        
    def draw(self):
        screen = self.game.screen
        screen.blit(self.bg, (0,0))
        self.camera.draw(screen)

class MainMenu(abstract.Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        self.audio = audio.SoundManager()
        self.audio.load_music("musiquita.mp3")
        self.audio.load_sound("pum", "choque.mp3")    
        self.audio.play_music()
        text = pygame.font.SysFont("Arial",32).render("Play",False,(100,100,100))
        self.playButton = components.Button(text, 100, 100, 3)
        text = pygame.font.SysFont("Arial",32).render("Settings",False,(100,100,100))
        self.settingsButton = components.Button(text, 100, 200, 3)
        text = pygame.font.SysFont("Arial",32).render("Quit",False,(100,100,100))
        self.quitButton = components.Button(text, 100, 300, 3)

    def update(self, dt):
        if self.playButton.update() == True :
            print("COMIENZA EL JUEGO")
            self.audio.play_sound("pum")
            self.game.switchScene(TestScene(self.game, name="test"))
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
