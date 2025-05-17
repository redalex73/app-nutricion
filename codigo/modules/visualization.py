import os
import matplotlib.pyplot as plt
from datetime import datetime

class Visualization:
    @staticmethod
    def plot_caloric_deficit(data, output_path="data/deficit_plot.png"):
        dates = [entry["date"] for entry in data]
        deficits = [float(entry["deficit"]) for entry in data]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, deficits, marker='o', label="Déficit calórico")
        plt.axhline(y=-1000, color='red', linestyle='--', label="Límite insano (-1000 kcal)")
        plt.fill_between(dates, deficits, -1000, where=[d < -1000 for d in deficits], color='red', alpha=0.3)
        plt.xticks(rotation=45)
        plt.xlabel("Fecha")
        plt.ylabel("Déficit calórico (kcal)")
        plt.title("Déficit calórico diario")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_macros(data, output_path="data/macros_plot.png"):
        dates = [entry["date"] for entry in data]
        proteins = [float(entry["protein"]) for entry in data]
        fats = [float(entry["fat"]) for entry in data]
        carbs = [float(entry["carbs"]) for entry in data]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, proteins, marker='o', label="Proteínas")
        plt.plot(dates, fats, marker='o', label="Grasas")
        plt.plot(dates, carbs, marker='o', label="Carbohidratos")
        plt.xticks(rotation=45)
        plt.xlabel("Fecha")
        plt.ylabel("Gramos")
        plt.title("Macronutrientes diarios")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_alert_trend(metric_name, values, dates, threshold, output_path):
        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o', label=metric_name)
        plt.axhline(y=threshold, color='red', linestyle='--', label="Límite insano")
        plt.xticks(rotation=45)
        plt.xlabel("Fecha")
        plt.ylabel(metric_name)
        plt.title(f"{metric_name} diario")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
