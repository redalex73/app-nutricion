import csv
import os
import sys

class Utils:
    @staticmethod
    def read_csv(file_path):
        """Lee un archivo CSV y devuelve una lista de diccionarios."""
        data = []
        if os.path.exists(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
        return data

    @staticmethod
    def write_to_csv(file_path, fieldnames, rows):
        """Escribe datos en un archivo CSV."""
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def remove_invalid_entries(data, valid_keys):
        """Elimina las entradas no válidas que no tienen las claves necesarias."""
        return [entry for entry in data if all(key in entry for key in valid_keys)]

    @staticmethod
    def get_data_path(filename):
        """Obtiene la ruta completa del archivo dentro de la carpeta 'data', compatible con PyInstaller."""
        if getattr(sys, 'frozen', False):  # Si está empaquetado como .exe
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, 'data', filename)

