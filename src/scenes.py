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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.switchScene(PauseScene(self.game, "Pause-Scene"))
        
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
 
        s    = ResourceManager.getConfig().getint("video", "scale")
        font = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 18 * s)
 
        self.playButton     = objects.TextButton(font, "Play",     20 * s, 40 * s)
        self.settingsButton = objects.TextButton(font, "Settings", 20 * s, 60* s)
        self.quitButton     = objects.TextButton(font, "Quit",     20 * s, 80 * s)
 
        self.sprite_group = pygame.sprite.Group(
            self.playButton.graphic,
            self.settingsButton.graphic,
            self.quitButton.graphic,
        )
 
    def update(self, dt):
        self.sprite_group.update(dt)
 
        if self.playButton.update(dt):
            self.game.changeScene(TestScene(self.game, name="test"))
        if self.settingsButton.update(dt):
            self.game.switchScene(SettingsScene(self.game,"setings-menu"))
        if self.quitButton.update(dt):
            self.game.quitGame()
 
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
 
    def draw(self):
        self.game.screen.fill((255, 255, 255))
        self.sprite_group.draw(self.game.screen)


# Categorías de ajustes — cada una es una lista de (etiqueta, valor_mockup)
SECTIONS = {
    "Video":      [("Resolucion", "800x800"), ("Escala", "4x"), ("Fullscreen", "Off"), ("FPS max", "1000")],
    "Audio":      [("Musica", "70%"), ("Efectos", "90%")],
    "Controles":  [("Arriba", "W"), ("Abajo", "S"), ("Izquierda", "A"), ("Derecha", "D"), ("Interactuar", "E"), ("Guardar", "G")],
    "Juego":      [("Idioma", "ES")],
}
class SettingsScene(abstract.Scene):

    def __init__(self, game, name="settings"):
        super().__init__(game, name)

        s    = ResourceManager.getConfig().getint("video", "scale")
        font = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 10 * s)

        # Tabs: un TextButton por sección
        tab_x_base = 10 * s
        tab_gap    = 60 * s
        self._tab_buttons = {
            section: objects.TextButton(font, section, tab_x_base + i * tab_gap, 10 * s)
            for i, section in enumerate(SECTIONS)
        }
        self._active_section = list(SECTIONS.keys())[0]

        # Botón Back
        self.backButton = objects.TextButton(font, "Back", 10 * s, 170 * s)

        self.sprite_group = pygame.sprite.Group(
            *[btn.graphic for btn in self._tab_buttons.values()],
            self.backButton.graphic,
        )

    def update(self, dt):
        self.sprite_group.update(dt)

        for section, btn in self._tab_buttons.items():
            if btn.update(dt):
                self._active_section = section

        if self.backButton.update(dt):
            self.game.quitScene()

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.quitScene()


    def draw(self):
        screen = self.game.screen
        s = ResourceManager.getConfig().getint("video", "scale")
        font = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 7 * s)

        screen.fill((255, 255, 255))

        # Línea separadora bajo las tabs
        tab_line_y = 22 * s
        pygame.draw.line(screen, (180, 180, 180), (10 * s, tab_line_y), (190 * s, tab_line_y), 1)

        # Filas de la sección activa
        rows = SECTIONS[self._active_section]
        row_x     = 15 * s
        value_x   = 120 * s
        row_y     = 30 * s
        row_gap   = 12 * s

        for label, value in rows:
            label_surf = font.render(label, False, (80, 80, 80))
            value_surf = font.render(value, False, (120, 120, 120))
            label_surf.set_colorkey(label_surf.get_at((0, 0)))
            value_surf.set_colorkey(value_surf.get_at((0, 0)))
            screen.blit(label_surf, (row_x, row_y))
            screen.blit(value_surf, (value_x, row_y))
            row_y += row_gap

        self.sprite_group.draw(screen)

class PauseScene(abstract.Scene):
 
    def __init__(self, game, name="pause"):
        super().__init__(game, name)
        self.parent_scene = game.sceneStack[-1]
 
        s    = ResourceManager.getConfig().getint("video", "scale")
        font = ResourceManager.getFont("CaskaydiaCoveNerdFont-Regular.ttf", 12 * s)
 
        self.resumeButton   = objects.TextButton(font, "Resume",   20 * s, 50 * s)
        self.settingsButton = objects.TextButton(font, "Settings", 20 * s, 100 * s)
        self.quitButton     = objects.TextButton(font, "Quit",     20 * s, 150 * s)
 
        self.sprite_group = pygame.sprite.Group(
            self.resumeButton.graphic,
            self.settingsButton.graphic,
            self.quitButton.graphic,
        )
 
    def update(self, dt):
        self.sprite_group.update(dt)
 
        if self.resumeButton.update(dt):
            self.game.quitScene()
        if self.settingsButton.update(dt):
            self.game.switchScene(SettingsScene(self.game, "settings-menu"))
        if self.quitButton.update(dt):
            self.game.changeScene(MainMenu(self.game, "main_menu"))
 
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.quitScene()
 
    def draw(self):
        # Dibuja la escena de juego detrás para que se vea el estado actual
        self.parent_scene.draw()
 
        # Overlay semitransparente
        overlay = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.game.screen.blit(overlay, (0, 0))
 
        self.sprite_group.draw(self.game.screen)