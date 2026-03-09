import pygame
import components
import player
import objects
import abstract
import audio
import utils
from resourceManager import ResourceManager
from dialog import Dialog, DialogManager, DialogScene
import switch
import door


class TestScene(abstract.Scene, abstract.Observer):
    def __init__(self, game, name="unamed"):
        abstract.Scene.__init__(self, game, name)
        self.player = player.Player((400, 200))
        config = ResourceManager.getConfig()
        self.bg = pygame.image.load(config.get("engine", "assets_path") + "background.png")

        self.switch1 = switch.Switch(pos=(400, 300))
        self.switch2 = switch.Switch(pos=(800, 300))
        self.door1 = door.Door(pos=(600, 200), is_locked=True)
        self.door2 = door.Door(pos=(600, 400), is_locked=True)
        self.door3 = door.Door(pos=(600, 600), is_locked=True)

        # Observadores originales: puertas escuchan a switches
        self.switch1.add_observer(self.door1)
        self.switch1.add_observer(self.door2)
        self.switch2.add_observer(self.door3)

        # ── La escena se registra como Observer en cada Observable ───
        # Cuando un switch haga notify(), on_notify() de la escena
        # recoge el diálogo del propio objeto y lo lanza.
        self.switch1.add_observer(self)
        self.switch2.add_observer(self)

        self.camera = objects.Camera()
        self.testGroup = pygame.sprite.Group()
        self.map = objects.tileMap("testMap")
        self.map.sprite.add(self.testGroup)
        for i in range(0, 10):
            tree = objects.testTree()
            tree.sprite.add(self.testGroup)
        self.player.graphic.add(self.testGroup)
        self.switch1.graphic.add(self.testGroup)
        self.switch2.graphic.add(self.testGroup)
        self.door1.graphic.add(self.testGroup)
        self.door2.graphic.add(self.testGroup)
        self.door3.graphic.add(self.testGroup)
        self.camera.addGroup(self.testGroup)
        self.camera.setReference(self.player)

    def on_notify(self, entity, event: str):
        print(f"[on_notify] entity={entity.name}, event={event}")
        if not hasattr(entity, "get_dialog"):
            print("[on_notify] sin get_dialog, ignorado")
            return
        lines = entity.get_dialog(event)
        print(f"[on_notify] lineas={lines}")
        if lines:
            self._launch_dialog(lines)

    def _launch_dialog(self, lines: list[Dialog]) -> None:
        print(f"[_launch_dialog] lanzando DialogScene con {len(lines)} lineas")
        dm = DialogManager()
        for d in lines:
            dm.add_dialog(d)
        scene = DialogScene(self.game, dm)
        print(f"[_launch_dialog] stack antes: {[s.name for s in self.game.sceneStack]}")
        self.game.switchScene(scene)
        print(f"[_launch_dialog] stack despues: {[s.name for s in self.game.sceneStack]}")


    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

    def update(self, dt):
        # Si hay una DialogScene encima en el stack, pausamos la lógica
        # para que los objetos no sigan disparando notificaciones
        if self.game.sceneStack[-1] is not self:
            return

        self.player.update(dt, map=self.map.reachable)
        self.switch1.update(dt, self.player.pos.topleft)
        self.switch2.update(dt, self.player.pos.topleft)
        self.door1.update(dt, self.player.pos.topleft)
        self.door2.update(dt, self.player.pos.topleft)
        self.door3.update(dt, self.player.pos.topleft)
        self.testGroup.update(dt)
        self.camera.update(dt)
        self.testGroup.update(dt)

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
        text = pygame.font.SysFont("Arial", 32).render("Play", False, (100, 100, 100))
        self.playButton = components.Button(text, 100, 100, 3)
        text = pygame.font.SysFont("Arial", 32).render("Settings", False, (100, 100, 100))
        self.settingsButton = components.Button(text, 100, 200, 3)
        text = pygame.font.SysFont("Arial", 32).render("Quit", False, (100, 100, 100))
        self.quitButton = components.Button(text, 100, 300, 3)

    def update(self, dt):
        if self.playButton.update():
            print("COMIENZA EL JUEGO")
            self.audio.play_sound("pum")
            self.game.switchScene(TestScene(self.game, name="test"))
        if self.settingsButton.update():
            print("Se abren ajustes")
        if self.quitButton.update():
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