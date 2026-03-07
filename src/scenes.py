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
from datetime import datetime
from saveManager import SaveManager

class TestScene(abstract.Scene):
    def __init__(self, game, name="unamed"):
        super().__init__(game, name)
        
     
        config = ResourceManager.getConfig()
        self.bg = pygame.image.load(config.get("engine","assets_path") + "background.png")
        
       
        self.map = objects.tileMap("testMap")
        self.camera = objects.Camera()
        self.testGroup = pygame.sprite.Group()
        self.map.sprite.add(self.testGroup)
        
        #  carga de las entidades desde el json de fase
        self.fase_data = ResourceManager.getJSON("phase.json")
        self.entities_dict = {} 
        
        self.player = player.Player((400,200)) 

        # Bucle de carga de entidades desde la Fase
        for ent in self.fase_data.get("entities", []):
            pos = ent["pos"]
            tipo = ent["type"]
            id_nombre = ent["id"]
            
            if tipo == "Switch":
                obj = switch.Switch(pos=pos)
                obj.is_pressed = ent.get("is_pressed", False)
                if obj.is_pressed: 
                    obj.graphic.set("switch-on")
                self.entities_dict[id_nombre] = obj
                
            elif tipo == "Door":
                locked = ent.get("is_locked", True)
                obj = door.Door(pos=pos, is_locked=locked)
                self.entities_dict[id_nombre] = obj
                
            elif tipo == "Player":
                self.player.pos.topleft = pos

        if "switch1" in self.entities_dict:
            if "door1" in self.entities_dict: 
                self.entities_dict["switch1"].add_observer(self.entities_dict["door1"])
            if "door2" in self.entities_dict: 
                self.entities_dict["switch1"].add_observer(self.entities_dict["door2"])
        
        if "switch2" in self.entities_dict and "door3" in self.entities_dict:
            self.entities_dict["switch2"].add_observer(self.entities_dict["door3"])

    
        # Árboles 
       # for i in range(0, 10):
    #        tree = objects.testTree()
     #       tree.sprite.add(self.testGroup)
            
        self.player.graphic.add(self.testGroup)
        for ent_obj in self.entities_dict.values():
            ent_obj.graphic.add(self.testGroup)
            
     
        self.camera.addGroup(self.testGroup)
        self.camera.setReference(self.player)

        SaveManager.load(self)

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: 
                    SaveManager.save(self)

    def update(self, dt):   
        self.player.update(dt, map=self.map.reachable)
        
        for ent in self.entities_dict.values():
            ent.update(dt, self.player.pos.topleft)

        self.testGroup.update(dt)
        self.camera.update(dt)

    def draw(self):
        screen = self.game.screen
        screen.fill("black")
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


