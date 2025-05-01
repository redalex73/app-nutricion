import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit
from PyQt5.QtCore import Qt

class GUI(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('IA de Nutrición')
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        """Inicializa los elementos de la interfaz."""
        layout = QVBoxLayout()

        # Botón de Ajustes
        self.settings_button = QPushButton("Ajustes", self)
        self.settings_button.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_button)

        # Etiqueta para mostrar el modo
        self.mode_label = QLabel("Modo: Claro", self)
        layout.addWidget(self.mode_label)

        # Selector para cambiar modo
        self.mode_combobox = QComboBox(self)
        self.mode_combobox.addItem("Claro")
        self.mode_combobox.addItem("Oscuro")
        self.mode_combobox.currentIndexChanged.connect(self.change_mode)
        layout.addWidget(self.mode_combobox)

        # Campo para ingresar comida
        self.food_input = QLineEdit(self)
        self.food_input.setPlaceholderText("Ingresa lo que comiste...")
        layout.addWidget(self.food_input)

        # Botón para guardar comida
        self.save_food_button = QPushButton("Guardar Comida", self)
        self.save_food_button.clicked.connect(self.save_food)
        layout.addWidget(self.save_food_button)

        # Botón para ver las recomendaciones
        self.recommendations_button = QPushButton("Recomendaciones", self)
        self.recommendations_button.clicked.connect(self.show_recommendations)
        layout.addWidget(self.recommendations_button)

        # Conectar el layout y mostrar la interfaz
        self.setLayout(layout)

    def open_settings(self):
        """Abre el menú de ajustes."""
        print("Abrir configuración")

    def change_mode(self):
        """Cambia el modo (oscuro/claro)."""
        selected_mode = self.mode_combobox.currentText()
        self.controller.update_mode(selected_mode)
        self.mode_label.setText(f"Modo: {selected_mode}")

    def save_food(self):
        """Guarda la comida que el usuario ingresa."""
        food = self.food_input.text()
        self.controller.save_food(food)
        self.food_input.clear()

    def show_recommendations(self):
        """Muestra las recomendaciones al usuario."""
        recommendations = self.controller.get_recommendations()
        print("Recomendaciones:", recommendations)
