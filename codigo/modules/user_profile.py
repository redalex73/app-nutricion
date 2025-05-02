import json
import os

class UserProfile:
    def __init__(self, profile_file='user_profile.json'):
        self.profile_file = profile_file
        self.profile = self.load_user_profile()

    def load_user_profile(self):
        """Carga el perfil del usuario desde un archivo JSON."""
        if not os.path.exists(self.profile_file):
            return {}
        
        with open(self.profile_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_user_profile(self):
        """Guarda el perfil del usuario en un archivo JSON."""
        with open(self.profile_file, 'w', encoding='utf-8') as file:
            json.dump(self.profile, file, indent=4)

    def get_profile(self):
        """Obtiene el perfil del usuario."""
        return self.profile

    def set_profile(self, age, height, weight, goal_weight=None, birthday=None):
        """Establece o actualiza el perfil del usuario."""
        self.profile['age'] = age
        self.profile['height'] = height
        self.profile['weight'] = weight
        if goal_weight:
            self.profile['goal_weight'] = goal_weight
        if birthday:
            self.profile['birthday'] = birthday
        self.save_user_profile()

    def update_weight(self, weight):
        """Actualiza el peso del usuario."""
        self.profile['weight'] = weight
        self.save_user_profile()

    def update_goal_weight(self, goal_weight):
        """Actualiza el objetivo de peso del usuario."""
        self.profile['goal_weight'] = goal_weight
        self.save_user_profile()
