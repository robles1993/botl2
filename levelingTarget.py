import cv2
import numpy as np
import mss
import time
import json
import logging
from utils import resource_path


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
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.bitwise_or(
        cv2.inRange(hsv, lower_red1, upper_red1),
        cv2.inRange(hsv, lower_red2, upper_red2)
    )
    red_pixels = cv2.countNonZero(mask)
    if total_width == 0 or img.shape[0] == 0:
        return 0.0
    return (red_pixels / (total_width * img.shape[0])) * 100


def run(send_command_callback, stop_event):
    """
    Hilo principal de leveling:
    - Envia la lista de monstruos AL PRIMER T (T:...) y luego solo envía T.
    - BUSCANDO / ATACANDO igual que antes.
    """
    logging.info("-> Hilo 'leveling.py' iniciado.")
    
    config = load_config_from_json()
    if not config:
        return

    TARGET_REGION = config['monster_detector']['region']

    # Lista de monstruos (string preparado)
    monsters = config.get("monsters", [])
    monsters_str = ";".join(monsters) if monsters else ""
    monsters_loaded_on_arduino = False  # bandera: todavía no hemos enviado T:...

    estado = 'BUSCANDO'
    muerte_confirmada_contador = 0
    CONFIRMACIONES_NECESARIAS = 3

    try:
        with mss.mss() as sct:
            ultimo_target_manual = 0
            ultimo_next_target = 0

            while not stop_event.is_set():
                # --- ESTADO BUSCANDO ---
                if estado == 'BUSCANDO':
                    ahora = time.time()

                    # Target manual cada 2s
                    if ahora - ultimo_target_manual > 2:
                        # Si no hemos cargado la lista en Arduino, enviamos T:lista en lugar de T
                        if not monsters_loaded_on_arduino and monsters_str:
                            send_command_callback(f"T:{monsters_str}\n")
                            monsters_loaded_on_arduino = True
                            logging.info("Enviado T:lista_de_monstruos (primer load).")
                        else:
                            send_command_callback('T\n')
                        ultimo_target_manual = ahora

                    # NextTarget cada 1s
                    if ahora - ultimo_next_target > 1:
                        send_command_callback('N\n')
                        ultimo_next_target = ahora

                    # Chequear vida del objetivo
                    img_bgr = np.array(sct.grab(TARGET_REGION))
                    health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
                    if health_perc > 1.0:
                        logging.info("Leveling: Enemigo encontrado.")
                        estado = 'ATACANDO'
                        muerte_confirmada_contador = 0
                        continue

                    time.sleep(0.1)

                # --- ESTADO ATACANDO ---
                elif estado == 'ATACANDO':
                    ahora = time.time()

                    # Chequear vida
                    img_bgr = np.array(sct.grab(TARGET_REGION))
                    health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])

                    if health_perc > 1.0:
                        muerte_confirmada_contador = 0
                        send_command_callback('A1\n')
                        time.sleep(0.3)
                        
                    if health_perc > 80.0:
                        # NextTarget cada 1s para buscar más mobs cercanos
                        if ahora - ultimo_next_target > 1:
                            send_command_callback('N\n')
                            ultimo_next_target = ahora

                    else:
                        muerte_confirmada_contador += 1
                        if muerte_confirmada_contador >= CONFIRMACIONES_NECESARIAS:
                            logging.info("Leveling: Enemigo derrotado.")
                            send_command_callback('P4\n')
                            time.sleep(0.5)
                            estado = 'BUSCANDO'
                            ultimo_target_manual = 0
                            ultimo_next_target = 0
                        else:
                            time.sleep(0.1)

    except Exception as e:
        logging.error(f"Error crítico en el hilo de leveling: {e}", exc_info=True)
    finally:
        logging.info("-> Hilo 'leveling.py' finalizado.")
