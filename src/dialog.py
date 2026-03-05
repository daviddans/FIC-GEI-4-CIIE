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
        import csv

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


class DialogScene(abstract.Scene):
    def __init__(self, game, dialog_manager, name="dialog"):
        super().__init__(game, name)
        self.dialog_manager = dialog_manager
        self.font = pygame.font.SysFont("Arial", 24)
        self.padding = 20

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                     
                    self.dialog_manager.next_dialog()

                    if self.dialog_manager.get_current_dialog() is None:
                        self.game.quitScene()   
                        return

    def update(self, dt):
        pass

    def draw(self):
        screen = self.game.screen
        width, height = screen.get_size()

        # Dibujar caja de diálogo
        dialog_rect = pygame.Rect(
            50,
            height - 200,
            width - 100,
            150
        )

        pygame.draw.rect(screen, (0, 0, 0), dialog_rect)
        pygame.draw.rect(screen, (255, 255, 255), dialog_rect, 3)

        current_dialog = self.dialog_manager.get_current_dialog()

        if current_dialog:
            full_text = f"{current_dialog.name}: {current_dialog.text}"
            wrapped_lines = self.wrap_text(full_text, dialog_rect.width - self.padding * 2)

            for i, line in enumerate(wrapped_lines):
                text_surface = self.font.render(line, True, (255, 255, 255))
                screen.blit(
                    text_surface,
                    (
                        dialog_rect.x + self.padding,
                        dialog_rect.y + self.padding + i * 30
                    )
                )

        pygame.display.update()

    def wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)
        return lines