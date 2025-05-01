# modules/recommendation_system.py
import random

class RecommendationSystem:
    def __init__(self, food_database):
        self.food_database = food_database

    def generate_recommendation(self, missing_macros=None):
        """Genera recomendaciones de comida según los macros que faltan o aleatoriamente si no se especifica."""
        if missing_macros:
            # Filtrar alimentos según los macros que faltan (por ejemplo, falta de grasa, proteínas, etc.)
            recommended_foods = self.filter_by_macros(missing_macros)
            return random.choice(recommended_foods) if recommended_foods else "No hay recomendaciones disponibles."
        else:
            # Si no se especifica, retorna una comida aleatoria de la base de datos
            return random.choice(self.food_database)

    def filter_by_macros(self, missing_macros):
        """Filtra los alimentos que cumplen con los requisitos de los macros faltantes."""
        recommended_foods = []
        for food in self.food_database:
            if all(food.get(macro, 0) >= value for macro, value in missing_macros.items()):
                recommended_foods.append(food)
        return recommended_foods
