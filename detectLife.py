import cv2
import numpy as np
import mss
import pytesseract
import re
import json
import time
# Se ha eliminado la importación de serial

print("-> Script 'detectLife.py' iniciado.")

# --- SE HA ELIMINADO TODA LA CONFIGURACIÓN DE ARDUINO ---

# --- FUNCIÓN DE COMUNICACIÓN MODIFICADA ---
def enviar_pulsacion_arduino(tecla):
    """Imprime el comando para que el launcher lo envíe."""
    mensaje = 'H' + tecla
    # El launcher enviará el payload "H3" al Arduino.
    print(f"PULSE:{mensaje}", flush=True)

# El resto de tu código de detección de vida (load_config, obtener_vida, etc.)
# se mantiene exactamente igual.
def load_player_config_from_json():
    with open('settings/config.json', 'r') as f:
        config = json.load(f)
    return config['player_detector']['region']
vida_region = load_player_config_from_json() 

def activePotionPercentage():
    with open('settings/config.json', 'r') as f:
        config = json.load(f)
    return config['potions_life']['life']
var_percentage_activated_potions = activePotionPercentage()

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

# Bucle principal para capturar y procesar
with mss.mss() as sct:
    while True:
        try:
            img = np.array(sct.grab(vida_region))
            actual, total, porcentaje = obtener_vida(img)
            if porcentaje is not None:
                if porcentaje < var_percentage_activated_potions:
                    enviar_pulsacion_arduino('3')
            # Es mejor usar un sleep más corto para mayor reactividad
            time.sleep(1) 
            # La ventana de OpenCV también podría dar problemas.
            # cv2.imshow("Recorte Vida (Original)", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        except Exception as e:
            print(f"Error en detectLife.py: {e}")
            break
cv2.destroyAllWindows()