import json
import os
from datetime import datetime # Importante para la fecha
from resourceManager import ResourceManager
from debugLogger import DebugLogger

class SaveManager:
    @staticmethod
    def get_save_path():
        base_path = ResourceManager.getConfig().get("PATH", "user_path")
        return os.path.join(base_path, "saved_game.json")

    @staticmethod
    def save(scene):
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y %H:%M:%S")
        data = {
            "scene_name": scene.name,
            "date": date_str,
            "player": scene.player.serialize() if scene.player else {},
        }
        path = SaveManager.get_save_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        DebugLogger.log("Partida guardada el %s en: %s", date_str, path)

    @staticmethod
    def load(scene):
        path = SaveManager.get_save_path()
        if not os.path.exists(path):
            DebugLogger.log("No hay partida guardada en %s", path)
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "date" in data:
            DebugLogger.log("Cargando partida: %s", data["date"])
        if scene.player and "player" in data:
            scene.player.unserialize(data["player"])
        DebugLogger.log("Partida cargada")