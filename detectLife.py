import cv2
import numpy as np
import mss
import pytesseract
import re
import json
import time
import logging
import sys
from utils import resource_path

# --- FUNCIONES DE UTILIDAD (No cambian) ---
def load_config_from_json():
    try:
        config_path = resource_path('settings/config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"FATAL en detectLife: No se pudo cargar config.json: {e}")
        return None

def obtener_vida(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 150])
    upper_white = np.array([180, 50, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    mask_big = cv2.resize(mask, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    texto = pytesseract.image_to_string(mask_big, config='--psm 7 -c tessedit_char_whitelist=0123456789/')
    match = re.search(r'(\d+)\s*/\s*(\d+)', texto)
    if match:
        actual = int(match.group(1))
        total = int(match.group(2))
        porcentaje = (actual / total) * 100 if total > 0 else 0
        return actual, total, porcentaje
    return None, None, None

# --- NUEVA FUNCIÓN PRINCIPAL ---
def run(send_command_callback, stop_event):
    """
    Función principal que se ejecutará como un hilo.
    Recibe una función 'callback' para enviar comandos y un evento para detenerse.
    """
    logging.info("-> Hilo 'detectLife.py' iniciado.")
    
    config = load_config_from_json()
    if not config:
        return # Salir del hilo si la configuración falló

    vida_region = config['player_detector']['region']
    var_percentage_activated_potions = config['potions_life']['life']

    try:
        with mss.mss() as sct:
            while not stop_event.is_set(): # El bucle se ejecuta hasta que se le ordene parar
                # Capturamos la imagen de la región de la vida
                img = np.array(sct.grab(vida_region))
                
                # Obtenemos los datos de la vida
                actual, total, porcentaje = obtener_vida(img)
                
                if porcentaje is not None:
                    if porcentaje < var_percentage_activated_potions:
                        # Usamos logging para registrar la acción
                        logging.info(f"DetectLife: Vida baja detectada ({porcentaje:.1f}%), usando poción.")
                        # --- CAMBIO IMPORTANTE: Usamos el callback ---
                        # En lugar de enviar "PULSE:H3", el launcher solo necesita el comando final
                        send_command_callback('H3') 
                
                # Pausamos durante un segundo para no sobrecargar la CPU.
                # stop_event.wait() es una forma más reactiva de hacer un sleep,
                # ya que se interrumpirá inmediatamente si el evento se activa.
                stop_event.wait(1)

    except Exception as e:
        logging.error(f"Error crítico en el hilo de detectLife: {e}", exc_info=True)
    finally:
        logging.info("-> Hilo 'detectLife.py' finalizado.")