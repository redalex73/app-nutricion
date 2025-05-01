# modules/graphing.py
import matplotlib.pyplot as plt

class Graphing:
    def __init__(self):
        self.fig, self.ax = plt.subplots()

    def plot_calorie_deficit(self, dates, deficit_values, threshold_value=1000):
        """Dibuja la gráfica de déficit calórico con una línea roja de umbral."""
        self.ax.plot(dates, deficit_values, label="Déficit Calórico")
        self.ax.axhline(y=threshold_value, color='r', linestyle='--', label="Umbral Insano (-1000 kcal)")
        self.ax.set_xlabel("Fecha")
        self.ax.set_ylabel("Déficit Calórico (kcal)")
        self.ax.legend()
        self.ax.set_title("Gráfico de Déficit Calórico Diario")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_macros(self, dates, macro_values, macro_type):
        """Dibuja la gráfica de los macronutrientes (proteínas, grasas, carbohidratos, etc.)."""
        self.ax.clear()
        self.ax.plot(dates, macro_values, label=f"{macro_type} Diario")
        self.ax.set_xlabel("Fecha")
        self.ax.set_ylabel(f"{macro_type} (g)")
        self.ax.legend()
        self.ax.set_title(f"Gráfico de {macro_type} Diario")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
