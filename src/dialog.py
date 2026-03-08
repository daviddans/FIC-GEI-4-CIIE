import pygame
import abstract
import csv


class Dialog:
    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __str__(self):
        return f"{self.name}: {self.text}"


class DialogManager:
    def __init__(self):
        self.dialogs = []
        self.current_dialog_index = 0

    def add_dialog(self, dialog):
        self.dialogs.append(dialog)

    def load_from_csv(self, filepath):
        self.dialogs = []
        self.current_dialog_index = 0

        with open(filepath, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.dialogs.append(Dialog(row["name"], row["text"]))

    def get_current_dialog(self):
        if self.current_dialog_index < len(self.dialogs):
            return self.dialogs[self.current_dialog_index]
        return None

    def next_dialog(self):
        self.current_dialog_index += 1

    def is_finished(self):
        return self.current_dialog_index >= len(self.dialogs)


class DialogScene(abstract.Scene):
    # Velocidad del efecto typewriter: ms por carácter
    TYPEWRITER_SPEED = 40

    def __init__(self, game, dialog_manager, name="dialog"):
        super().__init__(game, name)
        self.dialog_manager = dialog_manager
        # Guardamos referencia a la escena que hay debajo en el stack
        self.parent_scene = game.sceneStack[-1] if game.sceneStack else None
        self.font_name = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 22)
        self.font_hint = pygame.font.SysFont("Arial", 16)
        self.padding = 20

        # Estado typewriter
        self._visible_chars = 0
        self._time_acc = 0
        self._full_text = ""
        self._wrapped_lines = []   # lista de (line_str, is_name_line)
        self._typewriter_done = False

        self._load_current_dialog()

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _load_current_dialog(self):
        """Prepara el texto del diálogo actual para el efecto typewriter."""
        dlg = self.dialog_manager.get_current_dialog()
        if dlg is None:
            return

        self._visible_chars = 0
        self._time_acc = 0
        self._typewriter_done = False

        # Construimos el texto completo que vamos a mostrar
        self._full_text = dlg.text          # solo el cuerpo para el typewriter
        self._speaker = dlg.name

    def _advance(self):
        """Avanza: si el texto no se ha mostrado completo, lo completa;
        si ya está completo, pasa al siguiente diálogo."""
        if not self._typewriter_done:
            # Mostrar todo de golpe
            self._visible_chars = len(self._full_text)
            self._typewriter_done = True
        else:
            self.dialog_manager.next_dialog()
            if self.dialog_manager.is_finished():
                self.game.quitScene()
            else:
                self._load_current_dialog()

    def _wrap_text(self, text, max_width, font):
        """Divide el texto en líneas que caben en max_width."""
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = current + word + " "
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current.rstrip())
                current = word + " "
        if current:
            lines.append(current.rstrip())
        return lines

    # ------------------------------------------------------------------
    # Ciclo de escena
    # ------------------------------------------------------------------
    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._advance()

    def update(self, dt):
        if not self._typewriter_done:
            self._time_acc += dt
            chars_to_show = int(self._time_acc / self.TYPEWRITER_SPEED)
            self._visible_chars = min(chars_to_show, len(self._full_text))
            if self._visible_chars >= len(self._full_text):
                self._typewriter_done = True

    def draw(self):
        screen = self.game.screen
        width, height = screen.get_size()

        # Primero dibujamos la escena de debajo para que se vea el juego detrás
        if self.parent_scene:
            self.parent_scene.draw()

        box_w = width - 100
        box_h = 160
        box_x = 50
        box_y = height - box_h - 30

        # Fondo de la caja
        pygame.draw.rect(screen, (10, 10, 30),
                         (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (200, 200, 255),
                         (box_x, box_y, box_w, box_h), 2, border_radius=8)

        dlg = self.dialog_manager.get_current_dialog()
        if dlg:
            # Nombre del hablante
            name_surf = self.font_name.render(self._speaker, True, (255, 220, 80))
            screen.blit(name_surf, (box_x + self.padding, box_y + self.padding))

            # Texto visible hasta el carácter actual (typewriter)
            visible_text = self._full_text[:self._visible_chars]
            inner_w = box_w - self.padding * 2
            lines = self._wrap_text(visible_text, inner_w, self.font_text)

            text_y = box_y + self.padding + name_surf.get_height() + 6
            for line in lines:
                surf = self.font_text.render(line, True, (255, 255, 255))
                screen.blit(surf, (box_x + self.padding, text_y))
                text_y += surf.get_height() + 4

            # Indicador "continuar" parpadeante (solo si el texto ya se mostró)
            if self._typewriter_done:
                tick = pygame.time.get_ticks()
                if (tick // 500) % 2 == 0:        # parpadea cada 500 ms
                    hint = "[ ESPACIO / ENTER ]"
                    hint_surf = self.font_hint.render(hint, True, (160, 160, 160))
                    screen.blit(hint_surf,
                                (box_x + box_w - hint_surf.get_width() - self.padding,
                                 box_y + box_h - hint_surf.get_height() - self.padding))