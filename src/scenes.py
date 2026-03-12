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

        self.groups = {
            "TestGroup": pygame.sprite.Group(),
            "lights": pygame.sprite.Group()
        }

        self.entities_dict = {}  
        self.light_screen = self.game.screen.copy()


        config = ResourceManager.getConfig()

        self.map = objects.tileMap("TestMap")
        self.camera = objects.Camera()

        self.map.sprite.add(self.groups["TestGroup"])
        self.camera.addGroup(self.groups["TestGroup"])
        self.camera.addGroup(self.groups["lights"])

        self.load_from_tiled()
        if self.player:
            self.camera.setReference(self.player)
        SaveManager.load(self)

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: 
                    SaveManager.save(self)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.hud.toggle()
        
    def update(self, dt):
        self.player.update(dt, map=self.map.reachable)
        
        for ent_id, ent in self.entities_dict.items():
            if ent_id != "player":
                ent.update(dt, self.player.pos.topleft)

        self.groups["TestGroup"].update(dt)
        self.groups["lights"].update(dt)
        self.camera.update(dt)

    def draw(self):
        self.light_screen.fill("grey10")
        screen = self.game.screen
        screen.fill("black")
        self.groups["TestGroup"].draw(screen)
        self.groups["lights"].draw(self.light_screen)
        screen.blit(self.light_screen,(0, 0), special_flags=pygame.BLEND_MULT) #cast pseudo light

    
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
                
                nuevo_obj = clase_obj(pos=scaled_pos, graphic_group=self.groups["TestGroup"], light_group=self.groups["lights"],**props)
            
                ent_id = obj.name if obj.name else str(obj.id)
                self.entities_dict[ent_id] = nuevo_obj
                
                nuevo_obj.graphic.add(self.groups["TestGroup"])
                
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
 
    def __init__(self, game, name="main_menu"):
        super().__init__(game, name)
        self.audio = audio.SoundManager()
 
        # El menú trabaja en coordenadas de pantalla (no de mundo),
        # así que las posiciones ya son píxeles finales — no necesitan escala.
        # El texto sí se escala dentro de TextButton igual que hace Atlas.
        font = ResourceManager.getFont("Arial", 32)
 
        self.playButton     = objects.TextButton(font, "Play",     100, 150)
        self.settingsButton = objects.TextButton(font, "Settings", 100, 230)
        self.quitButton     = objects.TextButton(font, "Quit",     100, 310)
 
        self.sprite_group = pygame.sprite.Group()
        self.sprite_group.add(self.playButton.graphic)
        self.sprite_group.add(self.settingsButton.graphic)
        self.sprite_group.add(self.quitButton.graphic)
 
        self._fade_alpha = 255
        self._fade_speed = 180
 
    def update(self, dt):
        if self._fade_alpha > 0:
            self._fade_alpha = max(0, self._fade_alpha - self._fade_speed * dt)
 
        # sprite_group.update() llama Graphic.update() en cada botón,
        # lo que coloca rect.topleft en la posición correcta cada frame.
        self.sprite_group.update(dt)
 
        if self.playButton.update(dt):
            self.game.switchScene(TestScene(self.game, name="test"))
 
        if self.settingsButton.update(dt):
            print("Se abren ajustes")
 
        if self.quitButton.update(dt):
            self.game.quitGame()
 
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
 
    def draw(self):
        screen = self.game.screen
        sw, sh = screen.get_size()
 
        self._draw_gradient(screen, sw, sh, (245, 245, 245), (210, 215, 220))
 
        font_title = ResourceManager.getFont("Arial", 48)
        title_surf = font_title.render("Unlighted", False, (60, 60, 60))
        screen.blit(title_surf, (100, 60))
        pygame.draw.line(screen, (180, 180, 180), (100, 122), (340, 122), 1)
 
        self.sprite_group.draw(screen)
 
        if self._fade_alpha > 0:
            fade_surf = pygame.Surface((sw, sh))
            fade_surf.fill((255, 255, 255))
            fade_surf.set_alpha(int(self._fade_alpha))
            screen.blit(fade_surf, (0, 0))
 
    def _draw_gradient(self, surface, w, h, top_color, bottom_color):
        tr, tg, tb = top_color
        br, bg, bb = bottom_color
        for y in range(h):
            t = y / h
            r = int(tr + (br - tr) * t)
            g = int(tg + (bg - tg) * t)
            b = int(tb + (bb - tb) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (w, y))