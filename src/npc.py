import os
import pygame
import abstract
import components
from resourceManager import ResourceManager
from debugLogger import DebugLogger
from dialog import Dialog, DialogManager, DialogScene, load_dialogs_from_csv


# ─── Estados internos del NPC ────────────────────────────────────────────────
_IDLE    = "idle"
_GUIDING = "guiding"


class NPC(abstract.Object):
    """
    NPC guía.

    Propiedades esperadas desde Tiled:
        atlas            str    nombre del atlas de sprites
        speed            float  velocidad base (unidades/ms, sin escalar). Default 0.05
        dialog_key       str    clave en npcs.csv.                         Default "NPC_TALK"
        waypoint_prefix  str    prefijo de los objetos Waypoint en Tiled.  Default ""

    Flujo:
        IDLE ──colisión──► DialogScene ──termina──► GUIDING ──waypoints agotados──► IDLE
    """

    def __init__(self, pos, name="npc", graphic_group=None, light_group=None, **kwargs):
        super().__init__(name, pos)

        self.game             = kwargs.get("game", None)
        cfg                   = ResourceManager.getConfig()
        scale                 = cfg.getint("video", "scale")
        speed                 = float(kwargs.get("speed", 0.05))
        self.speed            = speed * scale
        self._dialog_key      = kwargs.get("dialog_key", "NPC_TALK")
        self._waypoint_prefix = kwargs.get("waypoint_prefix", "")

        # ── Gráfico ───────────────────────────────────────────────────────────
        atlas_name   = kwargs.get("atlas", "npc")
        self.atlas   = ResourceManager.getAtlas(atlas_name)
        self.graphic = components.Graphic(self, self.atlas)
        self.graphic.add(graphic_group)

        # Ajusta los IDs de frame a tu atlas
        self.graphic.addState("idle", [0])
        self.graphic.addState("walk", [1, 0, 2, 0])
        self.graphic.setState("idle")

        # ── Movimiento ────────────────────────────────────────────────────────
        self._x = float(self.pos.left)
        self._y = float(self.pos.top)

        # ── Waypoints — se rellenan en resolve_waypoints() ───────────────────
        self.waypoints = []
        self._wp_index = 0

        # ── Estado ───────────────────────────────────────────────────────────
        self._state          = _IDLE
        self._already_talked = False

        # ── Diálogos ─────────────────────────────────────────────────────────
        _base    = cfg.get("PATH", "assets_path")
        csv_path = os.path.join(_base, "dialogs", "npcs.csv")
        try:
            self._dialogs = load_dialogs_from_csv(csv_path, key_column="event")
        except FileNotFoundError:
            DebugLogger.log("NPC '%s': no se encontró npcs.csv en %s", name, csv_path)
            self._dialogs = {}

        DebugLogger.log("NPC init: name=%s pos=%s speed=%s dialog_key=%s waypoint_prefix='%s'",
                        name, pos, speed, self._dialog_key, self._waypoint_prefix)

    # ── Resolución de waypoints (llamado desde _load_from_tiled) ─────────────

    def resolve_waypoints(self, all_objects):
        """Recoge los objetos Waypoint cuyo nombre empiece por waypoint_prefix, en orden."""
        if not self._waypoint_prefix:
            return
        pairs = sorted(
            ((n, obj) for n, obj in all_objects.items()
             if n.startswith(self._waypoint_prefix)),
            key=lambda t: t[0]
        )
        self.waypoints = [(obj.pos.x, obj.pos.y) for _, obj in pairs]
        DebugLogger.log("NPC '%s': %d waypoints resueltos -> %s",
                        self.name, len(self.waypoints), self.waypoints)

    # ── API pública ───────────────────────────────────────────────────────────

    def start_guiding(self):
        self._wp_index = 0
        if self.waypoints:
            self._state = _GUIDING
            self.graphic.setState("walk")
            DebugLogger.log("NPC '%s': inicia guiado (%d waypoints)", self.name, len(self.waypoints))
        else:
            self._state = _IDLE
            DebugLogger.log("NPC '%s': sin waypoints, vuelve a idle", self.name)

    # ── Colisión ──────────────────────────────────────────────────────────────

    def on_collision(self, other):
        if self._state == _IDLE and not self._already_talked:
            self._already_talked = True
            self._launch_dialog()

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def update(self, dt):
        if self._state == _GUIDING:
            self._move_to_waypoint(dt)
        self.graphic.update(dt)

    # ── Privados ──────────────────────────────────────────────────────────────

    def _launch_dialog(self):
        lines = self._dialogs.get(self._dialog_key, [])
        if not lines or not self.game:
            self.start_guiding()
            return
        dm = DialogManager()
        for d in lines:
            dm.add_dialog(d)
        self.game.switchScene(_NPCDialogScene(self.game, dm, on_close=self.start_guiding))

    def _move_to_waypoint(self, dt):
        if self._wp_index >= len(self.waypoints):
            self._state = _IDLE
            self.graphic.setState("idle")
            DebugLogger.log("NPC '%s': guiado completado", self.name)
            return

        tx, ty = self.waypoints[self._wp_index]
        dx, dy = tx - self._x, ty - self._y
        dist   = (dx * dx + dy * dy) ** 0.5

        if dist <= 4.0:
            self._x, self._y = float(tx), float(ty)
            self._wp_index  += 1
            return

        self._x += (dx / dist) * self.speed * dt
        self._y += (dy / dist) * self.speed * dt
        self.pos.topleft = (int(self._x), int(self._y))

    # ── Serialización ─────────────────────────────────────────────────────────

    def serialize(self):
        return {"pos": self.pos.topleft, "already_talked": self._already_talked}

    def unserialize(self, data):
        if "pos" in data:
            self.pos.topleft = data["pos"]
            self._x = float(self.pos.left)
            self._y = float(self.pos.top)
        if "already_talked" in data:
            self._already_talked = data["already_talked"]


# ─── DialogScene que avisa al NPC al cerrarse ────────────────────────────────

class _NPCDialogScene(DialogScene):
    def __init__(self, game, dialog_manager, on_close=None, name="npc_dialog"):
        super().__init__(game, dialog_manager, name=name)
        self._on_close = on_close

    def _advance(self):
        if not self._typewriter_done:
            self._visible_chars   = len(self._full_text)
            self._typewriter_done = True
        else:
            self.dialog_manager.next_dialog()
            if self.dialog_manager.is_finished():
                if self._on_close:
                    self._on_close()
                self.game.quitScene()
            else:
                self._load_current_dialog()