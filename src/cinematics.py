"""
cinematic.py  –  Sistema de cinemáticas por pasos.

Sección 1 – Pasos base:   CinematicStep, DialogStep, WaitStep, FadeStep
Sección 2 – Motor:        CinematicScene
Sección 3 – Fábricas:     make_*  →  devuelven CinematicScene listo para switchScene

Uso desde scenes.py (solo llamadas, sin lógica):
    self.game.switchScene(make_tree_cinematic(self.game, tree, parent_scene=self))
    self.game.switchScene(make_intro_cinematic(self.game, parent_scene=self))
"""
from __future__ import annotations

import pygame
import abstract
from dialog import Dialog, DialogManager


# ══════════════════════════════════════════════════════════════
#  PASOS  (cada uno implementa  start / update / is_done / draw)
# ══════════════════════════════════════════════════════════════

class CinematicStep:
    """Clase base de un paso de cinemática."""
    def start(self, scene: "CinematicScene"):
        pass

    def update(self, dt: float, scene: "CinematicScene"):
        pass

    def is_done(self) -> bool:
        return True

    def draw(self, screen: pygame.Surface, scene: "CinematicScene"):
        pass

    def events(self, events, scene: "CinematicScene"):
        pass


class DialogStep(CinematicStep):
    TYPEWRITER_SPEED = 40   # ms por carácter

    def __init__(self, lines: list[Dialog]):
        self.lines = lines
        self._dm: DialogManager | None = None
        self._done = False

        self._visible_chars = 0
        self._time_acc = 0
        self._typewriter_done = False
        self._full_text = ""
        self._speaker = ""

        self._font_name = None
        self._font_text = None
        self._font_hint = None

    def start(self, scene):
        self._dm = DialogManager()
        for d in self.lines:
            self._dm.add_dialog(d)
        self._done = False
        self._font_name = pygame.font.SysFont("Arial", 20, bold=True)
        self._font_text = pygame.font.SysFont("Arial", 22)
        self._font_hint = pygame.font.SysFont("Arial", 16)
        self._load_current()

    def _load_current(self):
        dlg = self._dm.get_current_dialog()
        if dlg is None:
            self._done = True
            return
        self._full_text = dlg.text
        self._speaker = dlg.name
        self._visible_chars = 0
        self._time_acc = 0
        self._typewriter_done = False

    def _advance(self):
        if not self._typewriter_done:
            self._visible_chars = len(self._full_text)
            self._typewriter_done = True
        else:
            self._dm.next_dialog()
            if self._dm.is_finished():
                self._done = True
            else:
                self._load_current()

    def update(self, dt, scene):
        if self._typewriter_done:
            return
        self._time_acc += dt
        self._visible_chars = min(
            int(self._time_acc / self.TYPEWRITER_SPEED),
            len(self._full_text)
        )
        if self._visible_chars >= len(self._full_text):
            self._typewriter_done = True

    def events(self, events, scene):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._advance()

    def is_done(self):
        return self._done

    def draw(self, screen, scene):
        width, height = screen.get_size()
        padding = 20
        box_w = width - 100
        box_h = 160
        box_x = 50
        box_y = height - box_h - 30

        pygame.draw.rect(screen, (10, 10, 30),  (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (200, 200, 255),(box_x, box_y, box_w, box_h), 2, border_radius=8)

        name_surf = self._font_name.render(self._speaker, True, (255, 220, 80))
        screen.blit(name_surf, (box_x + padding, box_y + padding))

        visible_text = self._full_text[:self._visible_chars]
        inner_w = box_w - padding * 2
        lines = self._wrap(visible_text, inner_w, self._font_text)

        text_y = box_y + padding + name_surf.get_height() + 6
        for line in lines:
            surf = self._font_text.render(line, True, (255, 255, 255))
            screen.blit(surf, (box_x + padding, text_y))
            text_y += surf.get_height() + 4

        if self._typewriter_done:
            tick = pygame.time.get_ticks()
            if (tick // 500) % 2 == 0:
                hint_surf = self._font_hint.render("[ ESPACIO / ENTER ]", True, (160, 160, 160))
                screen.blit(hint_surf,
                            (box_x + box_w - hint_surf.get_width() - padding,
                             box_y + box_h - hint_surf.get_height() - padding))

    @staticmethod
    def _wrap(text, max_width, font):
        words, lines, current = text.split(" "), [], ""
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


class WaitStep(CinematicStep):
    """Pausa la cinemática N milisegundos sin bloquear el render."""
    def __init__(self, duration_ms: int):
        self._duration = duration_ms
        self._elapsed = 0

    def start(self, scene):
        self._elapsed = 0

    def update(self, dt, scene):
        self._elapsed += dt

    def is_done(self):
        return self._elapsed >= self._duration


class FadeStep(CinematicStep):
    """
    Fade in (negro → transparente) o fade out (transparente → negro).
    direction: "in" | "out"
    """
    def __init__(self, direction: str = "out", duration: int = 600,
                 color: tuple = (0, 0, 0)):
        assert direction in ("in", "out")
        self._direction = direction
        self._duration  = duration
        self._color     = color
        self._elapsed   = 0
        self._overlay: pygame.Surface | None = None

    def start(self, scene):
        self._elapsed = 0
        screen = scene.game.screen
        self._overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

    def update(self, dt, scene):
        self._elapsed = min(self._elapsed + dt, self._duration)

    def is_done(self):
        return self._elapsed >= self._duration

    def draw(self, screen, scene):
        t = self._elapsed / self._duration           # 0 → 1
        alpha = int(255 * t) if self._direction == "out" else int(255 * (1 - t))
        self._overlay.fill((*self._color, alpha))
        screen.blit(self._overlay, (0, 0))


class CinematicScene(abstract.Scene):

    def __init__(self, game, steps: list[CinematicStep],
                 parent_scene: abstract.Scene | None = None,
                 on_complete=None,
                 name: str = "cinematic"):
        super().__init__(game, name)
        self._steps = steps
        self._step_index = 0
        self.parent_scene = parent_scene or (game.sceneStack[-1] if game.sceneStack else None)
        self._on_complete = on_complete
        self._finished = False

        # Arrancamos el primer paso
        if self._steps:
            self._steps[0].start(self)

    @property
    def _current_step(self) -> CinematicStep | None:
        if self._step_index < len(self._steps):
            return self._steps[self._step_index]
        return None

    def _advance_step(self):
        self._step_index += 1
        if self._step_index < len(self._steps):
            self._steps[self._step_index].start(self)
        else:
            # Todos los pasos completados
            self._finished = True
            if self._on_complete:
                self._on_complete()
            self.game.quitScene()

    def events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.quitGame()

        step = self._current_step
        if step:
            step.events(events, self)

    def update(self, dt):
        step = self._current_step
        if step is None:
            return
        step.update(dt, self)
        if step.is_done():
            self._advance_step()

    def draw(self):
        screen = self.game.screen

        # Primero la escena de fondo (el juego sigue visible)
        if self.parent_scene:
            self.parent_scene.draw()

        # Luego el paso actual dibuja lo suyo encima
        step = self._current_step
        if step:
            step.draw(screen, self)


# ══════════════════════════════════════════════════════════════
#  FÁBRICAS  –  cada función construye y devuelve una
#  CinematicScene lista para pasarle a game.switchScene().
# ══════════════════════════════════════════════════════════════

def make_tree_cinematic(game, tree, parent_scene=None, on_complete=None) -> "CinematicScene":
    lines = tree.get_dialog("TREE_COLLISION")
    steps = [
        FadeStep("out", duration=400),
        WaitStep(300),
        DialogStep(lines),
        FadeStep("in", duration=400),
    ]
    return CinematicScene(game, steps, parent_scene=parent_scene, on_complete=on_complete)

def make_intro_cinematic(game, parent_scene=None) -> "CinematicScene":
    """
    Cinemática de introducción al entrar en la escena:
      fade in desde negro → diálogos de bienvenida → pausa
    """
    steps = [
        FadeStep("in", duration=800),
        DialogStep([
            Dialog("Sistema", "Bienvenido al mundo de prueba."),
            Dialog("Sistema", "Explora el entorno."),
        ]),
        WaitStep(500),
    ]
    return CinematicScene(game, steps, parent_scene=parent_scene)