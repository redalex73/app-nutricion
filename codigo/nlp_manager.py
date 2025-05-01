import spacy
from collections import defaultdict
import csv

# Cargar el modelo de spaCy para el procesamiento del lenguaje natural
nlp = spacy.load("es_core_news_sm")

class NLPManager:
    def __init__(self, food_data):
        self.food_data = food_data  # Diccionario con los datos de alimentos y su información nutricional
        self.food_dict = self.load_food_data(food_data)
    
    def load_food_data(self, food_data):
        food_dict = {}
        for food_item in food_data:
            food_dict[food_item['nombre'].lower()] = food_item
        return food_dict

    def interpret_text(self, text):
        """
        Interpreta el texto proporcionado y descompone los ingredientes del plato.
        """
        doc = nlp(text.lower())  # Procesa el texto usando spaCy
        ingredients = set()

        for token in doc:
            # Compara si el token coincide con alguno de los alimentos en la base de datos
            if token.text in self.food_dict:
                ingredients.add(token.text)
        
        if len(ingredients) == 0:
            return "No se pudo identificar los ingredientes del plato."

        # Devolver los ingredientes identificados y sus valores nutricionales
        return self.get_nutritional_info(ingredients)

    def get_nutritional_info(self, ingredients):
        """
        Devuelve la información nutricional de los ingredientes identificados.
        """
        nutritional_info = defaultdict(lambda: {'calorias': 0, 'proteinas': 0, 'grasas': 0, 'carbohidratos': 0, 'fibra': 0})
        for ingredient in ingredients:
            ingredient_data = self.food_dict.get(ingredient)
            if ingredient_data:
                nutritional_info[ingredient]['calorias'] = ingredient_data['calorias']
                nutritional_info[ingredient]['proteinas'] = ingredient_data['proteinas']
                nutritional_info[ingredient]['grasas'] = ingredient_data['grasas']
                nutritional_info[ingredient]['carbohidratos'] = ingredient_data['carbohidratos']
                nutritional_info[ingredient]['fibra'] = ingredient_data['fibra']
        
        return nutritional_info

    def get_ingredient_list(self):
        """
        Devuelve una lista de todos los ingredientes disponibles en la base de datos.
        """
        return list(self.food_dict.keys())

    def add_new_food(self, food_name, calories, proteins, fats, carbs, fiber):
        """
        Agrega un nuevo alimento a la base de datos de alimentos.
        """
        self.food_dict[food_name.lower()] = {
            'nombre': food_name,
            'calorias': calories,
            'proteinas': proteins,
            'grasas': fats,
            'carbohidratos': carbs,
            'fibra': fiber
        }

    def load_data_from_csv(self, csv_file):
        """
        Carga los datos de alimentos desde un archivo CSV.
        """
        food_data = []
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                food_data.append({
                    'nombre': row['nombre'],
                    'calorias': int(row['calorias']),
                    'proteinas': float(row['proteinas']),
                    'grasas': float(row['grasas']),
                    'carbohidratos': float(row['carbohidratos']),
                    'fibra': float(row['fibra'])
                })
        return food_data
