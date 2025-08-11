import cv2
import numpy as np
import mss
import pytesseract
import re
import json
import time
import serial 

print("Iniciando script... Dando 2 segundos para que la placa se estabilice.")
time.sleep(2) # Pausa de 2 segundos
# --- CONFIGURACIÓN DE ARDUINO ---
import serial.tools.list_ports

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Puedes imprimir para ver qué detecta:
        print(port.device, port.description, port.hwid)
        
        # Muchas placas Arduino tienen VID: 2341 o PID: 0043 (depende del modelo)
        # Aquí un ejemplo genérico para Arduino UNO:
        if 'Arduino' in port.description or 'VID:2341' in port.hwid:
            return port.device
    return None

puerto_arduino = find_arduino_port()
if puerto_arduino:
    arduino = serial.Serial(port=puerto_arduino, baudrate=9600, timeout=0.1)
    print(f"Conectado a Arduino en {puerto_arduino}")
else:
    arduino = None
    print("No se encontró Arduino conectado")
    
# Si Tesseract no está en la ruta de tu sistema, descomenta y ajusta la siguiente línea:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def enviar_pulsacion_arduino(tecla):
    """Envía el comando 'H' seguido de la tecla deseada al Arduino."""
    if arduino:
        # Creamos el mensaje de dos bytes: Comando + Tecla
        # Ejemplo: si tecla es '3', esto envía b'P3'
        mensaje = 'H' + tecla
        arduino.write(mensaje.encode()) # .encode() convierte el string a bytes
        print(f"Señal enviada a Arduino para pulsar la tecla: {tecla}")
        
    else:
        print("No se puede enviar señal, Arduino no está conectado.")


# La región de captura que ya tienes

def load_player_config_from_json():
    with open('settings/config.json', 'r') as f:
        config = json.load(f)
    # La única diferencia es la clave que pedimos
    return config['player_detector']['region']

vida_region = load_player_config_from_json() 

def activePotionPercentage():
    with open('settings/config.json', 'r') as f:
        config = json.load(f)
    # La única diferencia es la clave que pedimos
    return config['potions_life']['life']

var_percentage_activated_potions = activePotionPercentage()


def obtener_vida(img):
    """
    Procesa la imagen para aislar el texto y luego usa OCR para leer los valores de vida.
    """
    # 1. Convertir la imagen de BGR (formato de OpenCV) a HSV (Hue, Saturation, Value)
    # El espacio HSV es ideal para filtrar por colores.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. Definir el rango del color del texto (blanco/gris claro) en HSV
    # Estos valores deberían funcionar para aislar casi cualquier texto de color claro.
    lower_white = np.array([0, 0, 150])
    upper_white = np.array([180, 50, 255])

    # 3. Crear una máscara que solo contenga los píxeles dentro del rango definido.
    # El resultado será una imagen en blanco y negro donde el texto es blanco y el fondo negro.
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # 4. (Opcional pero recomendado) Agrandar la imagen.
    # El OCR funciona mucho mejor con imágenes más grandes y claras.
    # Aumentamos el tamaño 3 veces.
    mask_big = cv2.resize(mask, (0, 0), fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # 5. Usar Pytesseract en la máscara procesada para extraer el texto.
    # Usamos la configuración para tratar la imagen como una sola línea de texto (--psm 7)
    # y le decimos que espere encontrar solo dígitos.
    texto = pytesseract.image_to_string(mask_big, config='--psm 7 -c tessedit_char_whitelist=0123456789/')
    
    # 6. Buscar el patrón "actual / total" en el texto extraído.
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
        # Capturar la pantalla en la región definida
        img = np.array(sct.grab(vida_region))
        
        # Obtener los datos de la vida
        actual, total, porcentaje = obtener_vida(img)

        if porcentaje is not None:
            print(f"Vida: {actual}/{total} ({porcentaje:.2f}%)")
            perc = round(porcentaje, 2)
            if perc < var_percentage_activated_potions:
                print(F"¡ATENCIÓN! Vida baja (<{perc}%)")
                enviar_pulsacion_arduino('3')

        else:
            print("No se pudo leer la vida...")

        # Muestra la ventana con la captura original para verificar
        cv2.imshow("Recorte Vida (Original)", img)
        time.sleep(5) 
        # Salir del bucle si se presiona la tecla ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

cv2.destroyAllWindows()