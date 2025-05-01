from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class GraphsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Aquí se mostrarán las gráficas del progreso"))
        self.setLayout(layout)
