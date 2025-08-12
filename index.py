import tkinter as tk
from tkinter import messagebox
import threading
import launcher
import logging
import multiprocessing  # <--- 1. IMPORTA EL MÓDULO

# ... (El resto de tus funciones y la configuración de logging se quedan igual) ...

def levear_random():
    # ... (El código de esta función ya está bien) ...
    btn.config(state=tk.DISABLED, text="BOT EN EJECUCIÓN...")
    
    def run_launcher():
        try:
            logging.info("Iniciando el launcher...")
            launcher.main()
        except Exception as e:
            logging.error(f"Error crítico al ejecutar launcher.main(): {e}", exc_info=True)
            messagebox.showerror("Error Crítico", f"No se pudo iniciar el launcher. Revisa bot_errors.log.\nError: {e}")
            if btn.winfo_exists():
                btn.config(state=tk.NORMAL, text="LEVEARRANDOM")

    threading.Thread(target=run_launcher, daemon=True).start()
    messagebox.showinfo("Bot Iniciado", "El bot se ha iniciado en segundo plano.\nCierra esta ventana para detenerlo.")


# Este bloque ahora es a prueba de PyInstaller
if __name__ == '__main__':
    # --- 2. AÑADE ESTA LÍNEA AQUÍ, JUSTO AL PRINCIPIO ---
    multiprocessing.freeze_support()
    # ----------------------------------------------------

    root = tk.Tk()
    root.title("Mi Bot - Pantalla Principal")
    root.geometry("400x200")

    btn = tk.Button(root, text="LEVEARRANDOM", command=levear_random, font=("Arial", 14), width=20, relief=tk.RAISED, borderwidth=3)
    btn.pack(pady=50)

    root.mainloop()