from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class NutritionTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label = QLabel("Aquí se registrará lo que has comido")
        self.button = QPushButton("Añadir Comida")

        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)
