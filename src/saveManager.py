import json
import os
from datetime import datetime
from resourceManager import ResourceManager
from debugLogger import DebugLogger

class SaveManager:
    @staticmethod
    def get_save_path():
        base_path = ResourceManager.getConfig().get("PATH", "user_path")
        return os.path.join(base_path, "saved_game.json")

    @staticmethod
    def save(scene):
        path = SaveManager.get_save_path()
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        data.setdefault("maps", {})
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data["date"]        = date_str
        data["current_map"] = scene.map_name
        data["player"]      = scene.player.serialize() if scene.player else {}
        # Serializar entidades del mapa actual (deduplicadas por id de objeto)
        entities = {}
        seen = set()
        for sprite in scene.groups["entities"].sprites():
            ent = sprite.parent
            if id(ent) not in seen and ent is not scene.player:
                seen.add(id(ent))
                entities[ent.name] = ent.serialize()
        data["maps"][scene.map_name] = entities
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
        map_data = data.get("maps", {}).get(scene.map_name, {})
        seen = set()
        for sprite in scene.groups["entities"].sprites():
            ent = sprite.parent
            if id(ent) not in seen:
                seen.add(id(ent))
                if ent.name in map_data:
                    ent.unserialize(map_data[ent.name])
        DebugLogger.log("Partida cargada (mapa: %s)", scene.map_name)

    @staticmethod
    def get_current_map(default="lvl1_tutorial"):
        path = SaveManager.get_save_path()
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("current_map", default)
