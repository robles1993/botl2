# =================================================================
# SCRIPT LANZADOR CONTROLABLE
# =================================================================

# 1. IMPORTACIONES: Todas las librerías necesarias van aquí arriba.
import subprocess
import sys
import os
import time

# 2. CONFIGURACIÓN: Aquí defines qué scripts quieres lanzar.
scripts_a_lanzar = ["detectLife.py", "detectLifeMonster.py", "leveling.py"]

# 3. LÓGICA PRINCIPAL
# -----------------------------------------------------------------

# Almacenará los procesos que iniciemos para poder controlarlos después
procesos = []

print("Lanzando scripts en paralelo...")
print("======================================================")
print("PRESIONA Ctrl+C EN ESTA VENTANA PARA DETENER TODO.")
print("======================================================")

# Bucle para lanzar cada script
for script in scripts_a_lanzar:
    if not os.path.exists(script):
        print(f"AVISO: El script '{script}' no se encuentra. Será omitido.")
        continue
        
    # Usamos sys.executable para garantizar que se usa el mismo intérprete de Python
    comando = [sys.executable, script]
    
    # Lanzamos el proceso sin bloquear el script principal
    proceso = subprocess.Popen(comando)
    procesos.append(proceso)
    print(f"-> Script '{script}' lanzado con éxito (ID de Proceso: {proceso.pid})")

# Bucle principal del lanzador
try:
    # Este bucle mantiene el script principal vivo, esperando a que
    # el usuario presione Ctrl+C.
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Este bloque se ejecuta ÚNICAMENTE cuando presionas Ctrl+C en esta ventana.
    print("\n\nSeñal de interrupción (Ctrl+C) recibida.")
    print("Iniciando secuencia de apagado para todos los scripts...")
    
    for proceso in procesos:
        print(f"-> Enviando señal de terminación al proceso {proceso.pid}...")
        proceso.terminate() # Pide amablemente al proceso que se cierre
    
    # Esperamos un momento para dar tiempo a que los procesos se cierren
    time.sleep(2) 
    print("Secuencia de apagado completada.")

finally:
    # Este bloque se ejecuta siempre al final, para asegurar que no queden procesos huérfanos.
    print("Verificación final de procesos...")
    for proceso in procesos:
        if proceso.poll() is None: # Si el proceso aún existe...
            print(f"-> Forzando cierre del proceso {proceso.pid} que no respondió.")
            proceso.kill() # ...lo cerramos por la fuerza.
    print("Lanzador finalizado.")