import cv2
import numpy as np
import mss
import time
import json
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
def enviar_pulsacion_arduino(tecla):
    """Envía el comando 'P' seguido de la tecla deseada al Arduino."""
    if arduino:
        # Creamos el mensaje de dos bytes: Comando + Tecla
        # Ejemplo: si tecla es '3', esto envía b'P3'
        mensaje = 'P' + tecla
        arduino.write(mensaje.encode()) # .encode() convierte el string a bytes
        print(f"Señal enviada a Arduino para pulsar la tecla: {tecla}")
        
    else:
        print("No se puede enviar señal, Arduino no está conectado.")

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
            enviar_pulsacion_arduino('4')


        # Visualización (opcional pero útil para depurar) OCULTAR EN PRODUCCIÓN
        cv2.imshow("Captura de Vida del Objetivo", img_bgr)
        time.sleep(1) 
        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        time.sleep(0.1) # Pequeña pausa para no sobrecargar la CPU

cv2.destroyAllWindows()
print("Programa terminado.")