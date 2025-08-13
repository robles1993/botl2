import sys
import os
import time
import serial
import serial.tools.list_ports
import threading
import logging

# --- IMPORTAMOS NUESTROS SCRIPTS COMO MÓDULOS ---
import levelingTarget
import detectLife

# --- CONFIGURACIÓN ---
arduino = None
# Lista para mantener los hilos
threads = []
# Evento para indicar a todos los hilos que deben detenerse
stop_event = threading.Event()

def find_arduino_port():
    # ... (esta función no cambia)
    ports = serial.tools.list_ports.comports()
    for port in ports:
        logging.info(f"Detectado puerto: {port.device} - {port.description}")
        if 'Arduino' in port.description or 'VID:2341' in port.hwid:
            return port.device
    return None

def connect_to_arduino():
    # ... (esta función no cambia)
    global arduino
    puerto_arduino = find_arduino_port()
    if puerto_arduino:
        try:
            arduino = serial.Serial(port=puerto_arduino, baudrate=9600, timeout=1)
            logging.info(f"✅ Launcher conectado a Arduino en {puerto_arduino}")
            time.sleep(2)
        except serial.SerialException as e:
            logging.error(f"❌ Error al conectar con Arduino: {e}")
            arduino = None
    else:
        arduino = None
        logging.warning("❌ No se encontró Arduino conectado. Los comandos serán ignorados.")

# --- FUNCIÓN DE COMUNICACIÓN CENTRALIZADA ---
def send_command_to_arduino(command):
    """Esta función es el 'callback' que los hilos usarán para enviar datos."""
    if arduino:
        try:
            logging.info(f"🚀 Enviando a Arduino: '{command}'")
            arduino.write(command.encode())
        except Exception as e:
            logging.error(f"Error al enviar comando a Arduino: {e}")

# --- FUNCIÓN PRINCIPAL DEL LANZADOR (COMPLETAMENTE NUEVA) ---
def main():
    logging.info("Iniciando la función principal del launcher (modo Hilos).")
    
    connect_to_arduino()
    
    # Limpiar eventos y listas anteriores por si acaso
    stop_event.clear()
    threads.clear()

    # --- CREAR Y LANZAR LOS HILOS ---
    # Creamos un hilo para leveling
    leveling_thread = threading.Thread(
        target=levelingTarget.run, 
        args=(send_command_to_arduino, stop_event), 
        daemon=True
    )
    threads.append(leveling_thread)

    # Creamos un hilo para detectLife (asumiendo que lo has modificado igual)
    detectlife_thread = threading.Thread(
        target=detectLife.run,
        args=(send_command_to_arduino, stop_event),
        daemon=True
    )
    threads.append(detectlife_thread)

    # Iniciar todos los hilos
    for thread in threads:
        thread.start()

    logging.info("Todos los hilos han sido lanzados.")

    # Este hilo (el del launcher) puede simplemente esperar hasta que se le diga que pare
    # Opcional: Podríamos tener un bucle aquí para monitorizar el estado
    stop_event.wait() # Se quedará aquí hasta que el programa principal termine
    shutdown()

def shutdown():
    """Función para apagar todo limpiamente."""
    logging.info("Iniciando secuencia de apagado...")
    stop_event.set() # Señaliza a todos los hilos que deben parar

    if arduino and arduino.is_open:
        arduino.close()
        logging.info("✅ Puerto de Arduino cerrado.")
    
    logging.info("Lanzador finalizado.")