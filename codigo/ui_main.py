from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel,
    QPushButton, QTextEdit, QLineEdit, QHBoxLayout, QFileDialog,
    QCheckBox, QFormLayout, QSpinBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys

from data_manager import (
    ensure_data_dirs, load_config, save_config, export_data, import_data
)
from ui_graphs import GraphsTab
from chatbot import ChatbotWidget

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        ensure_data_dirs()
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NutriTrack AI")
        self.setGeometry(200, 100, 960, 640)

        if self.config.get("dark_mode", True):
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
        else:
            self.setStyleSheet("")

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(ChatbotWidget(), "Chatbot")
        self.tabs.addTab(GraphsTab(), "Gráficas")

        settings_button = QPushButton()
        settings_button.setIcon(QIcon.fromTheme("preferences-system"))
        settings_button.clicked.connect(self.open_settings)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("NutriTrack IA"))
        top_bar.addStretch()
        top_bar.addWidget(settings_button)

        layout.addLayout(top_bar)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def open_settings(self):
        dialog = QWidget()
        dialog.setWindowTitle("Ajustes")
        dialog.setFixedSize(300, 300)

        layout = QVBoxLayout()
        form = QFormLayout()

        dark_checkbox = QCheckBox("Modo oscuro")
        dark_checkbox.setChecked(self.config.get("dark_mode", True))
        form.addRow("Tema:", dark_checkbox)

        age_spin = QSpinBox()
        age_spin.setRange(10, 120)
        age_spin.setValue(self.config.get("edad", 30))
        form.addRow("Edad:", age_spin)

        height_spin = QSpinBox()
        height_spin.setRange(100, 250)
        height_spin.setValue(self.config.get("altura", 170))
        form.addRow("Altura (cm):", height_spin)

        birthday_input = QLineEdit()
        birthday_input.setPlaceholderText("dd-mm")
        birthday_input.setText(self.config.get("cumpleaños", ""))
        form.addRow("Cumpleaños:", birthday_input)

        export_button = QPushButton("Exportar datos")
        export_button.clicked.connect(lambda: QMessageBox.information(dialog, "Exportado", f"Exportado a:\n{export_data()}"))

        import_button = QPushButton("Importar datos")
        import_button.clicked.connect(lambda: self.import_file(dialog))

        save_button = QPushButton("Guardar")
        save_button.clicked.connect(lambda: self.save_settings(dialog, dark_checkbox.isChecked(), age_spin.value(), height_spin.value(), birthday_input.text()))

        layout.addLayout(form)
        layout.addWidget(export_button)
        layout.addWidget(import_button)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.show()

    def save_settings(self, dialog, dark, edad, altura, cumple):
        self.config["dark_mode"] = dark
        self.config["edad"] = edad
        self.config["altura"] = altura
        self.config["cumpleaños"] = cumple
        save_config(self.config)
        QMessageBox.information(dialog, "Guardado", "Configuraciones guardadas.\nReinicia la app para aplicar los cambios.")
        dialog.close()

    def import_file(self, dialog):
        fname, _ = QFileDialog.getOpenFileName(self, "Importar archivo", "", "JSON (*.json)")
        if fname:
            import_data(fname)
            QMessageBox.information(dialog, "Importado", "Datos importados correctamente.\nReinicia la app para aplicar cambios.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
