import csv
import os

class FoodManager:
    def __init__(self, food_data_file='food_data.csv'):
        self.food_data_file = food_data_file
        self.food_data = self.load_food_data()

    def load_food_data(self):
        """Carga los datos de alimentos desde un archivo CSV."""
        if not os.path.exists(self.food_data_file):
            return {}
        
        food_data = {}
        with open(self.food_data_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                food_name = row[0]
                calories = float(row[1])
                protein = float(row[2])
                carbs = float(row[3])
                fat = float(row[4])
                fiber = float(row[5])
                food_data[food_name.lower()] = {
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fat': fat,
                    'fiber': fiber
                }
        return food_data

    def save_food_data(self):
        """Guarda los datos de alimentos en un archivo CSV."""
        with open(self.food_data_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for food_name, data in self.food_data.items():
                writer.writerow([food_name, data['calories'], data['protein'], data['carbs'], data['fat'], data['fiber']])

    def get_food_info(self, food_name):
        """Obtiene la información nutricional de un alimento."""
        return self.food_data.get(food_name.lower())

    def add_new_food(self, food_name, calories, protein, carbs, fat, fiber):
        """Agrega un nuevo alimento al sistema."""
        self.food_data[food_name.lower()] = {
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat,
            'fiber': fiber
        }
        self.save_food_data()
        
    def calculate_macros(self, food_name, quantity):
        """Calcula los macronutrientes de un alimento en función de la cantidad."""
        food_info = self.get_food_info(food_name)
        if not food_info:
            return None
        # Suponemos que la cantidad dada es en gramos
        macros = {
            'calories': food_info['calories'] * quantity / 100,
            'protein': food_info['protein'] * quantity / 100,
            'carbs': food_info['carbs'] * quantity / 100,
            'fat': food_info['fat'] * quantity / 100,
            'fiber': food_info['fiber'] * quantity / 100
        }
        return macros
