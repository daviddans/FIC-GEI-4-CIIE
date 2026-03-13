# Script containing the logic for the various scenes composing the game.

import pygame
import components
import player
import objects
import abstract
import audio
import utils
from resourceManager import ResourceManager
import switch
import door
from healthHUD import HealthHUD
from shadow import Shadow
class TestScene(abstract.Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        self.player = player.Player((400,200))
        self.health_ui = HealthHUD(self.player)
        config = ResourceManager.getConfig()
        self.bg = pygame.image.load(config.get("engine","assets_path") + "background.png")
        self.switch1 = switch.Switch(pos=(400, 300))
        self.switch2 = switch.Switch(pos=(800, 300))
        self.door1 = door.Door(pos=(600, 200), is_locked=True)
        self.door2 = door.Door(pos=(600, 400), is_locked=True)
        self.door3 = door.Door(pos=(600, 600), is_locked=True)
        self.sin_luz = Shadow((600, 200), self.player)

        self.switch1.add_observer(self.door1)
        self.switch1.add_observer(self.door2)
        self.switch2.add_observer(self.door3)

        self.camera = objects.Camera()
        self.testGroup = pygame.sprite.Group()
        self.map = objects.tileMap("testMap")
        self.map.sprite.add(self.testGroup)
        for i in range(0,10):
            tree = objects.testTree()
            tree.sprite.add(self.testGroup)
        self.player.graphic.add(self.testGroup)
        self.switch1.graphic.add(self.testGroup)
        self.switch2.graphic.add(self.testGroup)
        self.door1.graphic.add(self.testGroup)
        self.door2.graphic.add(self.testGroup)
        self.door3.graphic.add(self.testGroup)
        self.sin_luz.graphic.add(self.testGroup)
        self.camera.addGroup(self.testGroup)
        self.camera.setReference(self.player)

        
        
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN:
                #prueba de que funciona el quitarle vida al player
                if event.key == pygame.K_k:
                    self.player.receive_hit(0.5)
                    print(f"Vida actual: {self.player.health.current_hp}")

    def update(self, dt):
        self.player.update(dt, map=self.map.reachable)
        self.switch1.update(dt, self.player.pos.topleft)
        self.switch2.update(dt, self.player.pos.topleft)
        self.door1.update(dt, self.player.pos.topleft)
        self.door2.update(dt, self.player.pos.topleft)
        self.door3.update(dt, self.player.pos.topleft)
        self.sin_luz.update(dt)
        if self.player.pos.colliderect(self.sin_luz.pos):
          self.player.receive_hit(self.sin_luz.damage)
        self.testGroup.update(dt)
        self.camera.update(dt)
     
        
        
    def draw(self):
        screen = self.game.screen
        screen.fill("black")
        screen.fill("black")
        self.camera.draw(screen)
        self.health_ui.draw(screen)
        
        

    

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
