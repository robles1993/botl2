import cv2
import numpy as np
import mss
import time
import json
# Se han eliminado las importaciones de serial

print("-> Script 'leveling.py' iniciado.")

# --- SE HA ELIMINADO TODA LA CONFIGURACIÓN DE ARDUINO ---

# --- CONFIGURACIÓN ---
def load_config_from_json():
    try:
        with open('settings/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'settings/config.json'.")
        exit()

config = load_config_from_json()
TARGET_REGION = config['monster_detector']['region']

# --- FUNCIONES DE COMUNICACIÓN MODIFICADAS ---

def enviar_comando_simple(comando):
    """En lugar de escribir en Arduino, imprime el comando para el launcher."""
    # El formato es "TIPO:DATOS". flush=True es VITAL para que se envíe inmediatamente.
    print(f"SIMPLE:{comando}", flush=True)

def enviar_pulsacion(comando, tecla):
    """Imprime el comando combinado para que el launcher lo envíe."""
    mensaje = comando + str(tecla)
    print(f"PULSE:{mensaje}", flush=True)

def get_health_percentage(img, total_width):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70]); upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70]); upper_red2 = np.array([180, 255, 255])
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    red_pixels = cv2.countNonZero(mask)
    if total_width == 0 or img.shape[0] == 0: return 0.0
    return (red_pixels / (total_width * img.shape[0])) * 100

# --- BUCLE PRINCIPAL (SIN CAMBIOS EN SU LÓGICA) ---
# El resto de tu script se mantiene exactamente igual, ya que la lógica no cambia.
estado = 'BUSCANDO'
LADOS_DEL_CIRCULO_EN_PYTHON = 8
TIEMPO_ESPERA_POR_PASO = 1.3 
pasos_de_busqueda_dados = 0
muerte_confirmada_contador = 0
CONFIRMACIONES_NECESARIAS = 3

with mss.mss() as sct:
    while True:
        try:
            # --- ESTADO: BUSCANDO UN ENEMIGO ---
            if estado == 'BUSCANDO':
                if pasos_de_busqueda_dados >= LADOS_DEL_CIRCULO_EN_PYTHON:
                    pasos_de_busqueda_dados = 0
                enviar_comando_simple('M')
                time.sleep(TIEMPO_ESPERA_POR_PASO)
                img_bgr = np.array(sct.grab(TARGET_REGION))
                health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
                if health_perc > 1.0:
                    enviar_comando_simple('R') 
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
                    enviar_pulsacion('A', '1')
                    time.sleep(0.8)
                else:
                    muerte_confirmada_contador += 1
                    if muerte_confirmada_contador >= CONFIRMACIONES_NECESARIAS:
                        enviar_pulsacion('P', '4')
                        time.sleep(1.5)
                        estado = 'BUSCANDO'
                        pasos_de_busqueda_dados = 0
                    else:
                        time.sleep(0.3)
            # --- Visualización ---
            # La visualización con cv2.imshow puede ser problemática en scripts hijos.
            # Podrías comentarla si da problemas.
            # img_display = cv2.cvtColor(np.array(sct.grab(TARGET_REGION)), cv2.COLOR_BGRA2BGR)
            # cv2.putText(img_display, f"ESTADO: {estado}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # cv2.imshow("Detector Leveling", img_display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            # Es buena idea capturar errores para que el script no muera silenciosamente
            print(f"Error en leveling.py: {e}")
            break
cv2.destroyAllWindows()