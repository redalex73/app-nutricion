# ai_nutrition.py
import re
import json

class NutritionAI:
    def __init__(self, ingredient_data_file="data/ingredients.json", combined_data_file="data/combined_dishes.json"):
        self.ingredient_data_file = ingredient_data_file
        self.combined_data_file = combined_data_file
        self.ingredients = self.load_json_data(self.ingredient_data_file)
        self.combined_dishes = self.load_json_data(self.combined_data_file)

    def load_json_data(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_json_data(self, path, data):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def interpret_meal(self, text):
        meal_items = []
        text = text.lower()

        for dish_name, ingredients in self.combined_dishes.items():
            if dish_name in text:
                return ingredients, dish_name

        # If no combined dish, try to find ingredients
        found_ingredients = []
        for item in self.ingredients:
            if item in text:
                found_ingredients.append(item)

        return found_ingredients, None

    def calculate_nutrition(self, ingredients):
        total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0}
        for ing in ingredients:
            data = self.ingredients.get(ing)
            if data:
                for key in total_nutrition:
                    total_nutrition[key] += data.get(key, 0)
        return total_nutrition

    def add_unknown_combined_dish(self, name, ingredients):
        if name not in self.combined_dishes:
            self.combined_dishes[name] = ingredients
            self.save_json_data(self.combined_data_file, self.combined_dishes)

    def add_unknown_ingredient(self, name, data):
        if name not in self.ingredients:
            self.ingredients[name] = data
            self.save_json_data(self.ingredient_data_file, self.ingredients)

    def recommend_meals(self, needs):
        # Example: needs = {"fiber": True, "fat": False, ...}
        suggestions = []
        for name, data in self.ingredients.items():
            match = all(
                (needs.get(k) and data.get(k, 0) >= 5) or (not needs.get(k))
                for k in needs
            )
            if match:
                suggestions.append(name)
        return suggestions[:5]  # limit to top 5 for now
