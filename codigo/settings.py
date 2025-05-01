# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from modules.food_manager import FoodManager
from modules.chatbot import ChatBot
from modules.settings import Settings
from modules.visualization import Visualization
from PyQt5 import QtCore

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IA de Nutrición")
        self.setGeometry(100, 100, 800, 600)

        # Cargar configuraciones
        self.settings = Settings()

        # Inicializar módulos
        self.food_manager = FoodManager()
        self.chatbot = ChatBot()
        self.visualization = Visualization()

        # Actualizar modo de la interfaz según configuración
        self.update_interface_mode()

    def update_interface_mode(self):
        """Actualiza el modo de la interfaz según la configuración."""
        if self.settings.settings["mode"] == "Oscuro":
            self.setStyleSheet("background-color: black; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")

    def closeEvent(self, event):
        """Se guarda la configuración al cerrar la aplicación."""
        self.settings.save_settings()
        event.accept()

    def update_user_data(self, age, weight, height):
        """Actualiza los datos personales del usuario."""
        self.settings.update_personal_data(age, weight, height)
        self.update_interface_mode()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
