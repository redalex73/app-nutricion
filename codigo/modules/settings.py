import json
import os

class Settings:
    DEFAULT_SETTINGS = {
        "dark_mode": False,
        "tutorial_mode": True,
        "language": "es"
    }

    @staticmethod
    def load_settings(path="data/config.json"):
        """Carga la configuración desde un archivo JSON o crea una por defecto si no existe."""
        if not os.path.exists(path):
            Settings.save_settings(Settings.DEFAULT_SETTINGS, path)
            return Settings.DEFAULT_SETTINGS

        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def save_settings(settings, path="data/config.json"):
        """Guarda la configuración en un archivo JSON."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)
