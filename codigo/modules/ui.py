from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from settings_ui import SettingsTab
from nutrition_ui import NutritionTab
from graphs_ui import GraphsTab
import sys

class NutritionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IA Nutrición Avanzada")
        self.setGeometry(100, 100, 1000, 700)

        self.tabs = QTabWidget()
        self.tabs.addTab(NutritionTab(), "Registro Diario")
        self.tabs.addTab(GraphsTab(), "Gráficas")
        self.tabs.addTab(SettingsTab(), "Ajustes")

        self.setCentralWidget(self.tabs)


def launch_app():
    app = QApplication(sys.argv)
    window = NutritionApp()
    window.show()
    sys.exit(app.exec_())
