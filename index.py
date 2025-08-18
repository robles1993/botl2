import tkinter as tk
from tkinter import messagebox
import threading
import logging
import multiprocessing

# --- IMPORTAMOS LOS MÓDULOS NECESARIOS ---
try:
    import launcher
    import launcherTarget
    from settings import settings as settings_panel
except ImportError as e:
    # NUEVO: Mensaje de error más genérico para cubrir todos los casos
    messagebox.showerror(
        "Error de Importación",
        f"No se pudo importar un módulo necesario: {e}\n"
        "Asegúrate de que 'launcher.py', 'launcherTarget.py' y "
        "'settings_panel.py' estén en la misma carpeta."
    )
    exit()

# Configuración del logging (sin cambios)
logging.basicConfig(
    filename='bot_errors.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# NUEVO: Variable global para evitar abrir múltiples ventanas de configuración
settings_window_open = False

# --- FUNCIONES DE CONTROL DE BOTONES (sin cambios) ---
def enable_buttons():
    if root.winfo_exists():
        btn_random.config(state=tk.NORMAL)
        btn_target.config(state=tk.NORMAL)
        btn_settings.config(state=tk.NORMAL) # NUEVO: Reactivar también el botón de config

def start_levear_random():
    btn_random.config(state=tk.DISABLED)
    btn_target.config(state=tk.DISABLED)
    btn_settings.config(state=tk.DISABLED) # NUEVO: Desactivar mientras el bot corre
    
    def run_launcher():
        try:
            logging.info("Iniciando launcher (modo Random)...")
            launcher.main()
            logging.info("El proceso de launcher (Random) ha finalizado.")
        except Exception as e:
            logging.error(f"Error crítico al ejecutar launcher.main(): {e}", exc_info=True)
            messagebox.showerror("Error Crítico", f"No se pudo ejecutar el launcher. Revisa bot_errors.log.\nError: {e}")
        finally:
            enable_buttons()

    threading.Thread(target=run_launcher, daemon=True).start()
    messagebox.showinfo("Bot Iniciado", "El bot de Leveo Random se ha iniciado en segundo plano.")

def start_levear_target():
    btn_random.config(state=tk.DISABLED)
    btn_target.config(state=tk.DISABLED)
    btn_settings.config(state=tk.DISABLED) # NUEVO: Desactivar mientras el bot corre

    def run_launcher_target():
        try:
            logging.info("Iniciando launcher (modo Target)...")
            launcherTarget.main()
            logging.info("El proceso de launcher (Target) ha finalizado.")
        except Exception as e:
            logging.error(f"Error crítico al ejecutar launcherTarget.main(): {e}", exc_info=True)
            messagebox.showerror("Error Crítico", f"No se pudo ejecutar el launcher. Revisa bot_errors.log.\nError: {e}")
        finally:
            enable_buttons()

    threading.Thread(target=run_launcher_target, daemon=True).start()
    messagebox.showinfo("Bot Iniciado", "El bot de Farm por Target se ha iniciado en segundo plano.")

# --- NUEVO: FUNCIÓN PARA ABRIR LA VENTANA DE CONFIGURACIÓN ---
def open_settings_window():
    """
    Abre la ventana de configuración del bot en una nueva ventana (Toplevel).
    Evita que se abran múltiples ventanas a la vez.
    """
    global settings_window_open
    if settings_window_open:
        return  # Si ya está abierta, no hacemos nada

    settings_window_open = True
    settings_win = tk.Toplevel(root)
    settings_win.title("Panel de Configuración")
    settings_win.geometry("480x480")

    # Llamamos a la función del otro script para que construya la UI dentro de la nueva ventana
    settings_panel.create_settings_ui(settings_win)

    # Función que se ejecuta al cerrar la ventana de configuración
    def on_settings_close():
        global settings_window_open
        settings_window_open = False
        settings_win.destroy()

    settings_win.protocol("WM_DELETE_WINDOW", on_settings_close)


# --- BLOQUE PRINCIPAL DE LA GUI (MODIFICADO) ---
if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    root = tk.Tk()
    root.title("Mi Bot - Pantalla Principal")
    root.geometry("400x250")

    # NUEVO: Frame superior para el botón de configuración
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))

    btn_settings = tk.Button(
        top_frame,
        text="⚙️ Configuración",
        command=open_settings_window,
        font=("Arial", 10)
    )
    btn_settings.pack(side=tk.RIGHT) # Lo alineamos a la derecha

    # Frame para centrar los botones principales
    center_frame = tk.Frame(root)
    center_frame.pack(expand=True)

    # --- BOTÓN 1: LEVEAR RANDOM ---
    btn_random = tk.Button(
        center_frame, 
        text="LEVEAR RANDOM",
        command=start_levear_random,
        font=("Arial", 12, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED, 
        borderwidth=3
    )
    btn_random.pack(pady=10)

    # --- BOTÓN 2: FARM POR TARGET ---
    btn_target = tk.Button(
        center_frame, 
        text="FARM POR TARGET",
        command=start_levear_target,
        font=("Arial", 12, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED, 
        borderwidth=3
    )
    btn_target.pack(pady=10)

    root.mainloop()