import json
import os
from datetime import datetime # Importante para la fecha
from resourceManager import ResourceManager

class SaveManager:
    @staticmethod
    def get_save_path():
        base_path = ResourceManager.getConfig().get("engine", "assets_path")
        return os.path.join(base_path, "saved_game.json")

    @staticmethod
    def save(scene):
        
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y %H:%M:%S")

        data = {
            "scene_name": scene.name,
            "date": date_str, 
            "player_pos": list(scene.player.pos.topleft),
            "entities": {
                name: obj.serialize() for name, obj in scene.entities_dict.items()
            }
        }
        
        path = SaveManager.get_save_path()
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        print(f"Partida guardada el {date_str} en: {path}")

    @staticmethod
    def load(scene):
        path = SaveManager.get_save_path()
        
        if not os.path.exists(path):
            print(f"No hay partida guardada en {path}")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

      
        if "date" in data:
            print(f" Cargando partida: {data['date']}")

        # restaurar la posición de Nix
        scene.player.pos.topleft = data["player_pos"]

        # restaurar el estado de cada objeto
        for name, state in data["entities"].items():
            if name in scene.entities_dict:
                scene.entities_dict[name].unserialize(state)
        
        print(" Partida cargada ")