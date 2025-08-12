import cv2
import numpy as np
import mss
import time
import json
import logging
import sys
from utils import resource_path

# ... (Las funciones load_config_from_json, get_health_percentage no cambian) ...
def load_config_from_json():
    try:
        config_path = resource_path('settings/config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"FATAL en leveling: No se pudo cargar config.json: {e}")
        return None

def get_health_percentage(img, total_width):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70]); upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70]); upper_red2 = np.array([180, 255, 255])
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    red_pixels = cv2.countNonZero(mask)
    if total_width == 0 or img.shape[0] == 0: return 0.0
    return (red_pixels / (total_width * img.shape[0])) * 100

# --- NUEVA FUNCIÓN PRINCIPAL ---
def run(send_command_callback, stop_event):
    """
    Función principal que se ejecutará como un hilo.
    Recibe una función 'callback' para enviar comandos y un evento para detenerse.
    """
    logging.info("-> Hilo 'leveling.py' iniciado.")
    
    config = load_config_from_json()
    if not config:
        return # Salir si la configuración falló

    TARGET_REGION = config['monster_detector']['region']
    
    estado = 'BUSCANDO'
    LADOS_DEL_CIRCULO_EN_PYTHON = 8
    TIEMPO_ESPERA_POR_PASO = 1.3 
    pasos_de_busqueda_dados = 0
    muerte_confirmada_contador = 0
    CONFIRMACIONES_NECESARIAS = 3

    try:
        with mss.mss() as sct:
            while not stop_event.is_set(): # El bucle se ejecuta hasta que se le ordene parar
                # --- ESTADO: BUSCANDO ---
                if estado == 'BUSCANDO':
                    if pasos_de_busqueda_dados >= LADOS_DEL_CIRCULO_EN_PYTHON:
                        pasos_de_busqueda_dados = 0
                    send_command_callback('M') # <--- Llama al callback
                    time.sleep(TIEMPO_ESPERA_POR_PASO)
                    img_bgr = np.array(sct.grab(TARGET_REGION))
                    health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
                    if health_perc > 1.0:
                        logging.info("Leveling: Enemigo encontrado.")
                        send_command_callback('R') # <--- Llama al callback
                        estado = 'ATACANDO'
                        pasos_de_busqueda_dados = 0
                        muerte_confirmada_contador = 0
                    else:
                        pasos_de_busqueda_dados += 1
                # --- ESTADO: ATACANDO ---
                elif estado == 'ATACANDO':
                    img_bgr = np.array(sct.grab(TARGET_REGION))
                    health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
                    if health_perc > 1.0:
                        muerte_confirmada_contador = 0
                        send_command_callback('A1') # <--- Llama al callback
                        time.sleep(0.8)
                    else:
                        muerte_confirmada_contador += 1
                        if muerte_confirmada_contador >= CONFIRMACIONES_NECESARIAS:
                            logging.info("Leveling: Enemigo derrotado.")
                            send_command_callback('P4') # <--- Llama al callback
                            time.sleep(1.5)
                            estado = 'BUSCANDO'
                            pasos_de_busqueda_dados = 0
                        else:
                            time.sleep(0.3)
    except Exception as e:
        logging.error(f"Error crítico en el hilo de leveling: {e}", exc_info=True)
    finally:
        logging.info("-> Hilo 'leveling.py' finalizado.")