import os
import pygame
import abstract
import components
from resourceManager import ResourceManager
from debugLogger import DebugLogger
from dialog import Dialog, DialogManager, DialogScene, load_dialogs_from_csv


class Table(abstract.Object):
    """
    Mesa interactiva. Al pulsar E en colisión muestra un diálogo del CSV.

    Propiedades esperadas desde Tiled:
        atlas       str   nombre del atlas de sprites. Default "table"
        dialog_key  str   clave en table.csv.          Default "TABLE_INTERACT"
    """

    def __init__(self, pos, name="table", graphic_group=None, light_group=None, **kwargs):
        super().__init__(name, pos)

        self.game        = kwargs.get("game", None)
        cfg              = ResourceManager.getConfig()
        self._dialog_key = kwargs.get("dialog_key", "TABLE_INTERACT")

        # ── Gráfico ───────────────────────────────────────────────────────────
        atlas_name   = kwargs.get("atlas", "table")
        self.atlas   = ResourceManager.getAtlas(atlas_name)
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.add(graphic_group)
        self.graphic.addState("idle", [0])
        self.graphic.setState("idle")

        # ── Control de pulsación (igual que Switch) ───────────────────────────
        self._already_pressed = False

        # ── Diálogos ─────────────────────────────────────────────────────────
        _base    = cfg.get("PATH", "assets_path")
        csv_path = os.path.join(_base, "dialogs", "table.csv")
        try:
            self._dialogs = load_dialogs_from_csv(csv_path, key_column="event")
        except FileNotFoundError:
            DebugLogger.log("Table '%s': no se encontró table.csv en %s", name, csv_path)
            self._dialogs = {}

        DebugLogger.log("Table init: name=%s pos=%s dialog_key=%s", name, pos, self._dialog_key)

    def on_collision(self, _other):
        if pygame.key.get_pressed()[pygame.K_e] and not self._already_pressed:
            self._already_pressed = True
            self._launch_dialog()

    def update(self, dt):
        if not pygame.key.get_pressed()[pygame.K_e]:
            self._already_pressed = False
        self.graphic.update(dt)

    def _launch_dialog(self):
        lines = self._dialogs.get(self._dialog_key, [])
        if not lines or not self.game:
            return
        dm = DialogManager()
        for d in lines:
            dm.add_dialog(d)
        self.game.switchScene(DialogScene(self.game, dm))

    def serialize(self):
        return {}

    def unserialize(self, data):
        pass