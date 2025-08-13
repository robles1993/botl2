import tkinter as tk
from tkinter import messagebox
import threading
import logging
import multiprocessing

# --- IMPORTAMOS LOS DOS LAUNCHERS SEPARADOS ---
# Asegúrate de que estos archivos (launcher.py y launcherTarget.py) existen en el mismo directorio.
try:
    import launcher
    import launcherTarget # Tu segundo launcher
except ImportError as e:
    messagebox.showerror("Error de Importación", f"No se pudo importar un módulo necesario: {e}\nAsegúrate de que 'launcher.py' y 'launcherTarget.py' estén en la misma carpeta.")
    exit()


# Configuración del logging
logging.basicConfig(
    filename='bot_errors.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- FUNCIÓN PARA HABILITAR LOS BOTONES ---
def enable_buttons():
    """Función para reactivar los botones de la GUI."""
    if root.winfo_exists():
        btn_random.config(state=tk.NORMAL)
        btn_target.config(state=tk.NORMAL)

# --- FUNCIÓN PARA EL PRIMER BOTÓN ---
def start_levear_random():
    # Deshabilitamos ambos botones para evitar conflictos
    btn_random.config(state=tk.DISABLED)
    btn_target.config(state=tk.DISABLED)
    
    def run_launcher():
        try:
            logging.info("Iniciando launcher (modo Random)...")
            launcher.main() # Llama a la función main del primer launcher
            logging.info("El proceso de launcher (Random) ha finalizado.")
        except Exception as e:
            logging.error(f"Error crítico al ejecutar launcher.main(): {e}", exc_info=True)
            messagebox.showerror("Error Crítico", f"No se pudo ejecutar el launcher. Revisa bot_errors.log.\nError: {e}")
        finally:
            # Volvemos a habilitar los botones cuando el proceso termina o falla
            enable_buttons()

    threading.Thread(target=run_launcher, daemon=True).start()
    messagebox.showinfo("Bot Iniciado", "El bot de Leveo Random se ha iniciado en segundo plano.")

# --- FUNCIÓN PARA EL SEGUNDO BOTÓN ---
def start_levear_target():
    # Deshabilitamos ambos botones
    btn_random.config(state=tk.DISABLED)
    btn_target.config(state=tk.DISABLED)
    
    def run_launcher_target():
        try:
            logging.info("Iniciando launcher (modo Target)...")
            launcherTarget.main() # Llama a la función main del SEGUNDO launcher
            logging.info("El proceso de launcher (Target) ha finalizado.")
        except Exception as e:
            logging.error(f"Error crítico al ejecutar launcherTarget.main(): {e}", exc_info=True)
            messagebox.showerror("Error Crítico", f"No se pudo ejecutar el launcher. Revisa bot_errors.log.\nError: {e}")
        finally:
            # Volvemos a habilitar los botones cuando el proceso termina o falla
            enable_buttons()

    threading.Thread(target=run_launcher_target, daemon=True).start()
    messagebox.showinfo("Bot Iniciado", "El bot de Farm por Target se ha iniciado en segundo plano.")

# --- BLOQUE PRINCIPAL DE LA GUI ---
if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    root = tk.Tk()
    root.title("Mi Bot - Pantalla Principal")
    # Aumentamos la altura de la ventana
    root.geometry("400x250") 

    # Frame para centrar los botones
    frame = tk.Frame(root)
    frame.pack(expand=True)

    # --- BOTÓN 1: LEVEAR RANDOM ---
    btn_random = tk.Button(
        frame, 
        text="LEVEAR RANDOM",
        command=start_levear_random, # Faltaba el comando
        font=("Arial", 12, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED, 
        borderwidth=3
    )
    btn_random.pack(pady=10) # pady añade espacio vertical

    # --- BOTÓN 2: FARM POR TARGET ---
    btn_target = tk.Button(
        frame, 
        text="FARM POR TARGET",
        command=start_levear_target, # Faltaba el comando
        font=("Arial", 12, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED, 
        borderwidth=3
    )
    btn_target.pack(pady=10) # pady añade espacio vertical

    root.mainloop()