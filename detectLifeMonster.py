import cv2
import numpy as np
import mss
import time
import json

# --- CONFIGURACIÓN ---
# Si Tesseract no está en la ruta de tu sistema, puedes comentar o eliminar esta línea
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Ajusta esta región para que capture únicamente LA BARRA ROJA, sin el borde negro si es posible.
# Es importante que el 'width' sea el ancho total de la barra cuando la vida está al 100%.
def load_monster_config_from_json():
    with open('settings/config.json', 'r') as f:
        config = json.load(f)
    # La única diferencia es la clave que pedimos
    return config['monster_detector']['region']

TARGET_REGION = load_monster_config_from_json() 

# --- FUNCIÓN DE PROCESAMIENTO ---

def get_health_percentage(img, total_width):
    """
    Calcula el porcentaje de vida restante basándose en la cantidad de píxeles rojos.
    """
    # 1. Convertir la imagen a espacio de color HSV.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. Definir el rango para el color rojo de la barra de vida.
    # El rojo tiene dos rangos en HSV porque cruza el valor 0/180.
    # Rango inferior (tonos más oscuros/rojos)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    # Rango superior (tonos más rosados/brillantes)
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # 3. Crear máscaras para ambos rangos y combinarlas.
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2) # Une las dos máscaras

    # 4. Calcular el número de píxeles rojos (píxeles blancos en la máscara).
    red_pixels = cv2.countNonZero(mask)

    # 5. Calcular el porcentaje de vida.
    # El área total es el ancho de la captura por su altura.
    total_pixels_in_bar_area = total_width * img.shape[0]
    
    if total_pixels_in_bar_area == 0:
        return 0.0

    percentage = (red_pixels / total_pixels_in_bar_area) * 100
    
    return percentage

# --- BUCLE PRINCIPAL ---

with mss.mss() as sct:
    print("Iniciando detector de vida. Presiona 'q' en la ventana de visualización para salir.")
    
    while True:
        # Capturar la pantalla en la región definida
        img = np.array(sct.grab(TARGET_REGION))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # Convertir de BGRA a BGR

        # Obtener el porcentaje de vida
        health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
        print(f"Vida del objetivo: {health_perc:.2f}%")

        perc = round(health_perc, 2)
        if perc == 0   :
            print(f"BICHO MUERTO")

        # Visualización (opcional pero útil para depurar) OCULTAR EN PRODUCCIÓN
        cv2.imshow("Captura de Vida del Objetivo", img_bgr)
        time.sleep(1) 
        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        time.sleep(0.1) # Pequeña pausa para no sobrecargar la CPU

cv2.destroyAllWindows()
print("Programa terminado.")