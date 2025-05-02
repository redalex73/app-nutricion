# modules/user_data_manager.py
import json

class UserDataManager:
    def __init__(self, data_file="user_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        """Carga los datos de usuario desde un archivo JSON."""
        try:
            with open(self.data_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def save_data(self):
        """Guarda los datos de usuario en un archivo JSON."""
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=4)

    def set_user_data(self, key, value):
        """Establece un dato del usuario."""
        self.data[key] = value
        self.save_data()

    def get_user_data(self, key):
        """Obtiene un dato del usuario."""
        return self.data.get(key)

    def clear_user_data(self):
        """Elimina todos los datos del usuario."""
        self.data = {}
        self.save_data()
