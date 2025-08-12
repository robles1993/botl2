# utils.py
import sys
import os

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En desarrollo, _MEIPASS no existe, así que usamos la ruta del archivo principal
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)