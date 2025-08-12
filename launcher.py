# =================================================================
# SCRIPT LANZADOR Y SERVIDOR DE ARDUINO
# =================================================================

import subprocess
import sys
import os
import time
import serial
import serial.tools.list_ports
import threading

# --- CONFIGURACIÓN ---
scripts_a_lanzar = ["detectLife.py", "leveling.py"] # Puedes añadir más aquí
procesos = []
arduino = None

# --- LÓGICA DE ARDUINO (AHORA CENTRALIZADA AQUÍ) ---

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Detectado puerto: {port.device} - {port.description}")
        if 'Arduino' in port.description or 'VID:2341' in port.hwid:
            return port.device
    return None

def connect_to_arduino():
    global arduino
    puerto_arduino = find_arduino_port()
    if puerto_arduino:
        try:
            arduino = serial.Serial(port=puerto_arduino, baudrate=9600, timeout=1)
            print(f"✅ Launcher conectado a Arduino en {puerto_arduino}")
            time.sleep(2) # Dar tiempo a que la conexión se estabilice
        except serial.SerialException as e:
            print(f"❌ Error al conectar con Arduino: {e}")
            arduino = None
    else:
        arduino = None
        print("❌ No se encontró Arduino conectado. Los comandos serán ignorados.")

# --- FUNCIÓN PARA ESCUCHAR A LOS PROCESOS HIJOS ---

def listen_to_process(proceso, nombre_script):
    # Lee la salida del script hijo línea por línea
    for line in iter(proceso.stdout.readline, b''):
        comando = line.decode('utf-8').strip()
        print(f"📬 Recibido de '{nombre_script}': '{comando}'")
        
        # Si tenemos una conexión de Arduino, enviamos el comando
        if arduino and ':' in comando:
            # El comando que enviará el hijo será del tipo "TIPO:DATOS"
            # por ejemplo "PULSE:A1" o "SIMPLE:M"
            try:
                # Partimos el comando para obtener solo los datos a enviar
                tipo, datos = comando.split(':', 1)
                arduino.write(datos.encode())
                print(f"🚀 Enviando a Arduino: '{datos}'")
            except Exception as e:
                print(f"Error procesando o enviando comando: {e}")

# --- LÓGICA PRINCIPAL DEL LANZADOR ---

connect_to_arduino() # Primero, nos conectamos al Arduino

print("\nLanzando scripts en paralelo...")
print("======================================================")
print("PRESIONA Ctrl+C EN ESTA VENTANA PARA DETENER TODO.")
print("======================================================")

# Bucle para lanzar cada script
for script in scripts_a_lanzar:
    if not os.path.exists(script):
        print(f"AVISO: El script '{script}' no se encuentra y será omitido.")
        continue
    
    # MUY IMPORTANTE: stdout=subprocess.PIPE le dice a Popen que capturemos la salida del hijo
    proceso = subprocess.Popen([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    procesos.append(proceso)
    
    # Creamos un "hilo" demonio que escuchará a este proceso en segundo plano
    thread = threading.Thread(target=listen_to_process, args=(proceso, script))
    thread.daemon = True # Permite que el programa principal termine aunque los hilos sigan corriendo
    thread.start()
    
    print(f"-> Script '{script}' lanzado con éxito (ID: {proceso.pid})")

# Bucle principal del lanzador
try:
    while True:
        # Revisa si algún proceso ha terminado
        for p in procesos:
            if p.poll() is not None:
                print(f"El proceso {p.pid} ha terminado.")
                # Aquí podrías añadir lógica para relanzarlo si quisieras
                procesos.remove(p)
        if not procesos:
            print("Todos los scripts han terminado de ejecutarse.")
            break
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nSeñal de interrupción (Ctrl+C) recibida. Apagando...")

finally:
    for proceso in procesos:
        if proceso.poll() is None:
            print(f"-> Terminando proceso {proceso.pid}...")
            proceso.terminate()
            
    if arduino:
        arduino.close()
        print("✅ Puerto de Arduino cerrado.")
        
    print("Lanzador finalizado.")