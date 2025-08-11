# Archivo: main_script.py

import time
# Importamos la función específica desde nuestro módulo en la carpeta 'shared'
from shared.image_finder import find_icon_on_screen

# --- CONFIGURACIÓN ---
# Lista de los iconos que quieres buscar, en orden de prioridad.
# Asegúrate de que las rutas sean correctas desde la raíz de tu proyecto.
ICONS_TO_FIND = [
    '../icons/icono_vida.png',
    '../icons/icono_monstruo.png',
    '../icons/otro_icono.png' 
]

# Umbral de confianza. 0.8 (80%) es un buen punto de partida.
# Súbelo si tienes falsos positivos, bájalo si no detecta el icono.
CONFIDENCE = 0.85 

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("Iniciando búsqueda de iconos en la pantalla...")
    
    # Llamamos a nuestra nueva función
    found_icon_info = find_icon_on_screen(ICONS_TO_FIND, confidence_threshold=CONFIDENCE)

    print("\n--- RESULTADO ---")
    if found_icon_info:
        print(f"¡Icono encontrado!")
        print(f"  -> Ruta del archivo: {found_icon_info['path']}")
        print(f"  -> Coordenadas del centro: {found_icon_info['location']}")
        print(f"  -> Confianza de la coincidencia: {found_icon_info['confidence']:.2f}")
        
        # Aquí podrías añadir la lógica para mover el ratón y hacer clic, etc.
        # import pyautogui
        # pyautogui.moveTo(found_icon_info['location'])
        
    else:
        print("No se encontró ningún icono de la lista con la confianza requerida.")