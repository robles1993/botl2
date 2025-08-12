import cv2
import numpy as np
import mss
import time
import json
import serial
import serial.tools.list_ports
import random

# (El resto de la configuración inicial y funciones find_arduino_port, load_config_from_json son iguales)
# ...
print("Iniciando script... Dando 2 segundos para que la placa se estabilice.")
time.sleep(2)

# --- CONFIGURACIÓN DE ARDUINO ---
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Detectado puerto: {port.device} - {port.description}")
        if 'Arduino' in port.description or 'VID:2341' in port.hwid:
            return port.device
    return None

puerto_arduino = find_arduino_port()
if puerto_arduino:
    try:
        arduino = serial.Serial(port=puerto_arduino, baudrate=9600, timeout=0.1)
        print(f"Conectado a Arduino en {puerto_arduino}")
    except serial.SerialException as e:
        print(f"Error al conectar con Arduino: {e}")
        arduino = None
else:
    arduino = None
    print("No se encontró Arduino conectado. El script funcionará sin enviar señales.")

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

# --- FUNCIONES DE COMUNICACIÓN Y PROCESAMIENTO ---

def enviar_comando_simple(comando):
    """Envía un único comando de un caracter al Arduino (ej: para mover)."""
    if arduino:
        arduino.write(comando.encode())
        print(f"Señal de movimiento '{comando}' enviada a Arduino.")
    else:
        print(f"SIMULACIÓN: Se enviaría el comando '{comando}' al Arduino.")

def enviar_pulsacion(comando, tecla):
    """Envía un comando de pulsación de tecla al Arduino (ej: A1, P4)."""
    if arduino:
        mensaje = comando + str(tecla)
        arduino.write(mensaje.encode())
    else:
        if comando == 'A': print(f"SIMULACIÓN: Pulsar 'Ataque' ({tecla})")
        elif comando == 'P': print(f"SIMULACIÓN: Pulsar 'Recoger' ({tecla})")
        elif comando == 'N': print(f"SIMULACIÓN: Pulsar 'Siguiente Objetivo' ({tecla})")

def get_health_percentage(img, total_width):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70]); upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70]); upper_red2 = np.array([180, 255, 255])
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
    red_pixels = cv2.countNonZero(mask)
    if total_width == 0 or img.shape[0] == 0: return 0.0
    return (red_pixels / (total_width * img.shape[0])) * 100

# --- BUCLE PRINCIPAL CON MÁQUINA DE ESTADOS REACTIVA ---
estado = 'BUSCANDO'

# NUEVOS PARÁMETROS DE BÚSQUEDA
LADOS_DEL_CIRCULO_EN_PYTHON = 8  # Debe coincidir con el valor en Arduino
# Tiempo que tarda Arduino en hacer UN paso (700+50+100+100+100+150 = 1200ms)
# Le damos un margen.
TIEMPO_ESPERA_POR_PASO = 1.3 
pasos_de_busqueda_dados = 0

# Añadimos el contador de confirmación de muerte para más robustez
muerte_confirmada_contador = 0
CONFIRMACIONES_NECESARIAS = 3

with mss.mss() as sct:
    print("Iniciando bot. Presiona 'q' en la ventana de visualización para salir.")
    
    while True:
        # --- ESTADO: BUSCANDO UN ENEMIGO (LÓGICA MEJORADA) ---
        if estado == 'BUSCANDO':
            # Si hemos completado un círculo y no hay bicho, empezamos de nuevo.
            if pasos_de_busqueda_dados >= LADOS_DEL_CIRCULO_EN_PYTHON:
                print("Círculo de búsqueda completo. Reiniciando secuencia.")
                pasos_de_busqueda_dados = 0
            
            print(f"Estado: BUSCANDO (Paso {pasos_de_busqueda_dados + 1}/{LADOS_DEL_CIRCULO_EN_PYTHON})")
            
            # 1. Ordena a Arduino dar UN solo paso
            enviar_comando_simple('M')
            
            # 2. Espera solo el tiempo que tarda ese paso
            time.sleep(TIEMPO_ESPERA_POR_PASO)

            # 3. Comprueba INMEDIATAMENTE si se encontró un objetivo
            img_bgr = np.array(sct.grab(TARGET_REGION))
            health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
            
            if health_perc > 1.0:
                print(f"¡Bicho encontrado con {health_perc:.2f}% de vida! INTERRUMPIENDO BÚSQUEDA.")
                # Le decimos a Arduino que resetee su propio contador
                enviar_comando_simple('R') 
                estado = 'ATACANDO'
                pasos_de_busqueda_dados = 0 # Resetea el contador de Python
                muerte_confirmada_contador = 0
            else:
                # Si no se encontró nada, contamos el paso y seguimos buscando
                pasos_de_busqueda_dados += 1

        # --- ESTADO: ATACANDO A UN ENEMIGO (LÓGICA CON CONFIRMACIÓN) ---
        elif estado == 'ATACANDO':
            img_bgr = np.array(sct.grab(TARGET_REGION))
            health_perc = get_health_percentage(img_bgr, TARGET_REGION['width'])
            
            print(f"Estado: ATACANDO - Vida: {health_perc:.2f}% (Confirmaciones de muerte: {muerte_confirmada_contador})")

            if health_perc > 1.0:
                muerte_confirmada_contador = 0
                enviar_pulsacion('A', '1')
                time.sleep(0.8)
            else:
                muerte_confirmada_contador += 1
                if muerte_confirmada_contador >= CONFIRMACIONES_NECESARIAS:
                    print("¡Muerte confirmada! Recogiendo botín...")
                    time.sleep(0.5)
                    enviar_pulsacion('P', '4')
                    time.sleep(1.5)
                    
                    print("CAMBIANDO A MODO BÚSQUEDA.")
                    estado = 'BUSCANDO'
                    pasos_de_busqueda_dados = 0 # Aseguramos empezar de 0
                else:
                    print("Posible muerte. Re-confirmando...")
                    time.sleep(0.3)

        # Visualización y control de salida
        img_display = cv2.cvtColor(np.array(sct.grab(TARGET_REGION)), cv2.COLOR_BGRA2BGR)
        cv2.putText(img_display, f"ESTADO: {estado}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Detector", img_display)
        
        # Eliminé los time.sleep(1) extra que tenías al final del bucle para mayor reactividad
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
print("Programa terminado.")