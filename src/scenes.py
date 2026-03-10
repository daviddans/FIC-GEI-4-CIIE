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
    def __init__(self, game, name=None):
        super().__init__(game, name)

        self.entities_dict = {} 
        self.testGroup = pygame.sprite.Group()


        config = ResourceManager.getConfig()
        assets_path = config.get("engine", "assets_path")
        self.bg = pygame.image.load(assets_path + "background.png")

        self.map = objects.tileMap("testMap")
        self.camera = objects.Camera()

        self.map.sprite.add(self.testGroup)
        self.camera.addGroup(self.testGroup)

        self.load_from_tiled()
        SaveManager.load(self)
        if self.player:
            self.camera.setReference(self.player)
     

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: 
                    SaveManager.save(self)

    def update(self, dt):
        self.player.update(dt, map=self.map.reachable)
        
        for ent_id, ent in self.entities_dict.items():
            if ent_id != "player":
                ent.update(dt, self.player.pos.topleft)

        self.testGroup.update(dt)
        self.camera.update(dt)

    def draw(self):
        screen = self.game.screen
        screen.fill("black")
        self.camera.draw(screen)
    
    def load_from_tiled(self):
        # Mapeo de clases
        classes = {
            "Player": player.Player,
            "Switch": switch.Switch,
            "Door": door.Door
        }

        tmx_data = self.map.tmx
        scale = ResourceManager.getConfig().getint("video", "scale")

        for obj in tmx_data.objects:
          
            clase_obj = classes.get(obj.type)
            
            if clase_obj:
                props = obj.properties 
                scaled_pos = (obj.x * scale, obj.y * scale)
                
                nuevo_obj = clase_obj(pos=scaled_pos, **props)
            
                ent_id = obj.name if obj.name else str(obj.id)
                self.entities_dict[ent_id] = nuevo_obj
                
                nuevo_obj.graphic.add(self.testGroup)
                
                # Referencia para la cámara
                if obj.type == "Player":
                    self.player = nuevo_obj

        for ent_id, ent in self.entities_dict.items():
            if hasattr(ent, 'target') and ent.target:
                # ahora mismo se implementa en el tiled como (door1,door2)
                target_names = str(ent.target).split(",")
                ent.target_objects = [] 

                for name in target_names:
                    receptor_name = name.strip()
                    receptor = self.entities_dict.get(receptor_name)
                    
                    if receptor:
                        ent.add_observer(receptor)
                        ent.target_objects.append(receptor)
                        if len(target_names) == 1:
                            ent.target = receptor
                            
                        print(f"Lógica conectada: {ent_id} -> {receptor_name}")

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


