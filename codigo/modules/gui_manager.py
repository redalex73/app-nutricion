import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QMenuBar, QAction, QMenu, QDialog, QFormLayout, QComboBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class GuiManager(QMainWindow):
    def __init__(self, food_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.food_manager = food_manager
        self.setWindowTitle("IA Nutrición")
        self.setWindowIcon(QIcon('app_icon.ico'))  # Cambiar icono
        self.setGeometry(200, 100, 800, 600)
        
        self.init_ui()

    def init_ui(self):
        # Barra de menús
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Ajustes')

        # Agregar opciones de configuración
        mode_action = QAction('Cambiar Modo', self)
        mode_action.triggered.connect(self.change_mode)
        settings_menu.addAction(mode_action)

        delete_data_action = QAction('Eliminar Datos', self)
        delete_data_action.triggered.connect(self.delete_data)
        settings_menu.addAction(delete_data_action)

        # Crear la pestaña principal
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Crear la página principal
        self.main_page = QWidget()
        self.tabs.addTab(self.main_page, "Inicio")
        self.main_layout = QVBoxLayout()
        
        self.main_label = QLabel("Bienvenido a la app de nutrición.")
        self.main_layout.addWidget(self.main_label)
        
        self.food_input_label = QLabel("¿Qué has comido hoy?")
        self.main_layout.addWidget(self.food_input_label)
        
        self.food_input = QLineEdit()
        self.main_layout.addWidget(self.food_input)
        
        self.add_food_button = QPushButton("Agregar Comida")
        self.add_food_button.clicked.connect(self.add_food)
        self.main_layout.addWidget(self.add_food_button)

        self.main_page.setLayout(self.main_layout)

        # Crear la página de gráficos
        self.graph_page = QWidget()
        self.tabs.addTab(self.graph_page, "Gráficas")
        self.graph_layout = QVBoxLayout()

        self.graph_label = QLabel("Aquí aparecerán las gráficas de tu progreso.")
        self.graph_layout.addWidget(self.graph_label)
        self.graph_page.setLayout(self.graph_layout)

        # Configuración del modo oscuro
        self.dark_mode = False
        self.apply_dark_mode()

    def change_mode(self):
        # Cambiar entre modo oscuro y claro
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()

    def apply_dark_mode(self):
        # Aplicar o quitar el modo oscuro
        if self.dark_mode:
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")

    def delete_data(self):
        # Método para eliminar todos los datos
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("Confirmación")
        layout = QFormLayout(confirm_dialog)
        confirm_message = QLabel("¿Estás seguro de que quieres eliminar todos los datos?")
        layout.addRow(confirm_message)
        
        yes_button = QPushButton("Sí")
        yes_button.clicked.connect(self.confirm_delete)
        no_button = QPushButton("No")
        no_button.clicked.connect(confirm_dialog.close)
        
        layout.addRow(yes_button, no_button)
        
        confirm_dialog.exec_()

    def confirm_delete(self):
        # Confirmar la eliminación de datos
        self.food_manager.food_data.clear()
        self.food_manager.save_food_data()
        print("Datos eliminados.")
        self.close()

    def add_food(self):
        # Agregar comida a la base de datos
        food_name = self.food_input.text()
        food_info = self.food_manager.get_food_info(food_name)
        
        if food_info:
            result_text = f"{food_name.capitalize()} ya está registrado: {food_info}"
        else:
            result_text = f"{food_name.capitalize()} no encontrado. ¿Quieres agregarlo?"
            self.prompt_add_food(food_name)

        self.main_label.setText(result_text)

    def prompt_add_food(self, food_name):
        # Dialogo para agregar nuevo alimento
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Agregar {food_name.capitalize()}")
        
        layout = QFormLayout(dialog)

        calories_input = QLineEdit()
        protein_input = QLineEdit()
        carbs_input = QLineEdit()
        fat_input = QLineEdit()
        fiber_input = QLineEdit()

        layout.addRow("Calorías:", calories_input)
        layout.addRow("Proteínas:", protein_input)
        layout.addRow("Carbohidratos:", carbs_input)
        layout.addRow("Grasas:", fat_input)
        layout.addRow("Fibra:", fiber_input)

        submit_button = QPushButton("Agregar")
        submit_button.clicked.connect(lambda: self.add_new_food(food_name, calories_input.text(), protein_input.text(), carbs_input.text(), fat_input.text(), fiber_input.text()))

        layout.addRow(submit_button)

        dialog.exec_()

    def add_new_food(self, food_name, calories, protein, carbs, fat, fiber):
        # Agregar un nuevo alimento a la base de datos
        self.food_manager.add_new_food(food_name, float(calories), float(protein), float(carbs), float(fat), float(fiber))
        self.main_label.setText(f"{food_name.capitalize()} agregado correctamente.")
