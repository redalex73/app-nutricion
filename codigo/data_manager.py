import os
import json
from datetime import datetime

DATA_DIR = "user_data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
DATA_FILE = os.path.join(DATA_DIR, "progress.json")
FOOD_DB = os.path.join(DATA_DIR, "ingredients.json")
PLATOS_DB = os.path.join(DATA_DIR, "combinados.json")


def ensure_data_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [CONFIG_FILE, DATA_FILE, FOOD_DB, PLATOS_DB]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({} if 'json' in file else [], f)


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_config(config):
    save_json(CONFIG_FILE, config)


def load_config():
    return load_json(CONFIG_FILE)


def save_progress(progress):
    save_json(DATA_FILE, progress)


def load_progress():
    return load_json(DATA_FILE)


def export_data():
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_path = os.path.join(DATA_DIR, f"export_{now}.json")
    data = {
        "config": load_config(),
        "progress": load_progress(),
        "ingredients": load_json(FOOD_DB),
        "combinados": load_json(PLATOS_DB)
    }
    save_json(export_path, data)
    return export_path


def import_data(import_file):
    with open(import_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        save_json(CONFIG_FILE, data.get("config", {}))
        save_json(DATA_FILE, data.get("progress", {}))
        save_json(FOOD_DB, data.get("ingredients", {}))
        save_json(PLATOS_DB, data.get("combinados", {}))
