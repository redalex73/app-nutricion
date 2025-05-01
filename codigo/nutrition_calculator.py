import csv

class NutritionCalculator:
    def __init__(self, food_file='food_data.csv'):
        self.food_file = food_file
        self.food_data = self.load_food_data()

    def load_food_data(self):
        """Carga los datos de alimentos desde un archivo CSV."""
        food_data = []
        try:
            with open(self.food_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    food_data.append(row)
        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo {self.food_file}.")
        return food_data

    def find_food(self, food_name):
        """Busca un alimento por su nombre."""
        for food in self.food_data:
            if food_name.lower() in food['name'].lower():
                return food
        return None

    def calculate_nutrients(self, food_name, quantity):
        """Calcula los nutrientes de un alimento en base a su cantidad."""
        food = self.find_food(food_name)
        if not food:
            return None

        # Convertimos las cantidades a valores numéricos
        calories = float(food['calories']) * quantity
        protein = float(food['protein']) * quantity
        carbohydrates = float(food['carbohydrates']) * quantity
        fats = float(food['fats']) * quantity
        fiber = float(food['fiber']) * quantity

        return {
            'calories': calories,
            'protein': protein,
            'carbohydrates': carbohydrates,
            'fats': fats,
            'fiber': fiber
        }

    def add_food(self, food_name, calories, protein, carbohydrates, fats, fiber):
        """Agrega un alimento a la base de datos."""
        food = {
            'name': food_name,
            'calories': calories,
            'protein': protein,
            'carbohydrates': carbohydrates,
            'fats': fats,
            'fiber': fiber
        }
        self.food_data.append(food)
        self.save_food_data()

    def save_food_data(self):
        """Guarda los datos de los alimentos en un archivo CSV."""
        with open(self.food_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['name', 'calories', 'protein', 'carbohydrates', 'fats', 'fiber']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for food in self.food_data:
                writer.writerow(food)
