from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Configuración de la aplicación"))
        self.dark_mode_button = QPushButton("Cambiar modo oscuro/claro")
        layout.addWidget(self.dark_mode_button)

        self.setLayout(layout)
