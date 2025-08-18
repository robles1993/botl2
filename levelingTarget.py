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


# leveling.py

# ... (tus funciones load_config_from_json y get_health_percentage no cambian) ...

def run(send_command_callback, stop_event):
    """
    Hilo principal de leveling:
    - CORRECCIÓN: Envía la lista de monstruos UNA SOLA VEZ al inicio con el prefijo 'LT:'.
    - El bucle principal solo usa comandos de acción cortos.
    """
    logging.info("-> Hilo 'leveling.py' iniciado.")
    
    config = load_config_from_json()
    if not config:
        return

    TARGET_REGION = config['monster_detector']['region']

    # --- CORRECCIÓN: Enviar la lista de monstruos al iniciar ---
    monsters = config.get("monsters", [])
    if monsters:
        monsters_str = ";".join(monsters)
        command = f"LT:{monsters_str}\n"  # Usamos el prefijo LT como pediste
        send_command_callback(command)
        logging.info(f"Lista de monstruos enviada a Arduino: {command.strip()}")
        # Damos 1 segundo a Arduino para procesar la lista antes de continuar
        time.sleep(1)
    else:
        logging.warning("No hay monstruos en config.json para enviar.")

    # --- El resto de la lógica ---
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

                    # Target manual cada 2s. SIEMPRE envía un comando corto 'T\n'.
                    if ahora - ultimo_target_manual > 2:
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

                    img_bgr = np.array(sct.grab(TARGET_REGION))
                    health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])

                    if health_perc > 1.0:
                        muerte_confirmada_contador = 0
                        send_command_callback('A1\n')
                        time.sleep(0.3)
                        
                        if health_perc > 80.0:
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
                    
                    time.sleep(0.1)

    except Exception as e:
        logging.error(f"Error crítico en el hilo de leveling: {e}", exc_info=True)
    finally:
        logging.info("-> Hilo 'leveling.py' finalizado.")