import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import numpy as np

class GraphicsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gráficas de Progreso")
        self.setGeometry(200, 100, 600, 400)

        layout = QVBoxLayout()

        self.graph_label = QLabel("Gráfico de Déficit Calórico y Macronutrientes", self)
        layout.addWidget(self.graph_label)

        self.plot_button = QPushButton("Generar Gráfico")
        self.plot_button.clicked.connect(self.plot_graph)
        layout.addWidget(self.plot_button)

        self.setLayout(layout)

    def plot_graph(self):
        # Aquí usaremos datos simulados para mostrar un ejemplo de gráfico
        days = ["01", "02", "03", "04", "05", "06", "07"]
        deficit_calories = [500, 600, 700, 800, 300, 1200, 950]
        proteins = [30, 32, 35, 40, 28, 50, 38]
        carbs = [70, 80, 75, 60, 90, 85, 65]
        fats = [20, 25, 30, 15, 10, 40, 30]

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.plot(days, deficit_calories, label="Déficit Calórico (kcal)", color='red', marker='o')
        ax.plot(days, proteins, label="Proteínas (g)", color='blue', marker='o')
        ax.plot(days, carbs, label="Carbohidratos (g)", color='green', marker='o')
        ax.plot(days, fats, label="Grasas (g)", color='purple', marker='o')

        ax.axhline(y=1000, color='black', linestyle='--', label="Límite Déficit Insano")

        ax.set_xlabel("Días")
        ax.set_ylabel("Cantidad")
        ax.set_title("Progreso de Déficit Calórico y Macronutrientes")
        ax.legend(loc="upper right")

        plt.show()
