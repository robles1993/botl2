# settings/settings.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- 1. FUNCIÓN DE GUARDADO (Sin cambios en su lógica interna) ---
def guardar_configuracion():
    # ... (tu código de guardado es correcto y no necesita cambios)
    try:
        monsters_list = [var.get() for var in monster_vars if var.get()]
        config_data = {
            "player_detector": {"region": {"top": int(player_top_var.get()),"left": int(player_left_var.get()),"width": int(player_width_var.get()),"height": int(player_height_var.get())}},
            "monster_detector": {"region": {"top": int(monster_top_var.get()),"left": int(monster_left_var.get()),"width": int(monster_width_var.get()),"height": int(monster_height_var.get())}},
            "potions_life": {"life": int(potions_life_var.get())},"monsters": monsters_list
        }
        if not os.path.exists('settings'):
            os.makedirs('settings')
        with open('settings/config.json', 'w') as archivo_json:
            json.dump(config_data, archivo_json, indent=4)
        messagebox.showinfo("Éxito", "¡La configuración se ha guardado en 'settings/config.json'!")
    except ValueError:
        messagebox.showerror("Error de Entrada", "Por favor, asegúrate de que todos los campos de región y pociones contengan solo números.")
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"No se pudo guardar el archivo: {e}")

# --- 2. FUNCIÓN DE CARGA (Sin cambios en su lógica interna) ---
def cargar_configuracion_inicial():
    # ... (tu código de carga es correcto y no necesita cambios)
    try:
        with open('settings/config.json', 'r') as archivo:
            config = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {
            "player_detector": {"region": {"top": 54, "left": 30, "width": 210, "height": 14}},
            "monster_detector": {"region": {"top": 0, "left": 785, "width": 350, "height": 24}},
            "potions_life": {"life": 50},"monsters": ["Toad Lord", "Marsh Stakato Soldier"] 
        }
        if not os.path.exists('settings'):
            os.makedirs('settings')
        with open('settings/config.json', 'w') as archivo:
            json.dump(config, archivo, indent=4)
    
    player_top_var.set(config.get("player_detector", {}).get("region", {}).get("top", 54))
    player_left_var.set(config.get("player_detector", {}).get("region", {}).get("left", 30))
    player_width_var.set(config.get("player_detector", {}).get("region", {}).get("width", 210))
    player_height_var.set(config.get("player_detector", {}).get("region", {}).get("height", 14))
    monster_top_var.set(config.get("monster_detector", {}).get("region", {}).get("top", 0))
    monster_left_var.set(config.get("monster_detector", {}).get("region", {}).get("left", 785))
    monster_width_var.set(config.get("monster_detector", {}).get("region", {}).get("width", 350))
    monster_height_var.set(config.get("monster_detector", {}).get("region", {}).get("height", 24))
    potions_life_var.set(config.get("potions_life", {}).get("life", 50))
    
    monsters_from_file = config.get("monsters", [])
    for i in range(8):
        if i < len(monsters_from_file):
            monster_vars[i].set(monsters_from_file[i])
        else:
            monster_vars[i].set("")

# --- NUEVO: FUNCIÓN QUE CONSTRUYE LA INTERFAZ ---
def create_settings_ui(parent_window):
    """
    Crea todos los widgets del panel de configuración dentro de una ventana padre.
    Esta es la función que será llamada desde index.py.
    """
    # MODIFICADO: Hacemos las variables globales para que las funciones de guardar/cargar las vean
    global player_top_var, player_left_var, player_width_var, player_height_var
    global monster_top_var, monster_left_var, monster_width_var, monster_height_var
    global potions_life_var, monster_vars

    # MODIFICADO: Todo el código de la UI ahora está DENTRO de esta función
    # y usa 'parent_window' en lugar de crear una nueva.
    
    notebook = ttk.Notebook(parent_window, padding="10")
    notebook.pack(fill=tk.BOTH, expand=True)

    tab_regiones = ttk.Frame(notebook)
    notebook.add(tab_regiones, text="Regiones de Detección")

    tab_general = ttk.Frame(notebook)
    notebook.add(tab_general, text="Configuración General")

    # -- Variables de Tkinter --
    player_top_var = tk.StringVar()
    player_left_var = tk.StringVar()
    player_width_var = tk.StringVar()
    player_height_var = tk.StringVar()
    monster_top_var = tk.StringVar()
    monster_left_var = tk.StringVar()
    monster_width_var = tk.StringVar()
    monster_height_var = tk.StringVar()
    potions_life_var = tk.StringVar()
    monster_vars = [tk.StringVar() for _ in range(8)]

    # -- Widgets en la pestaña 'Regiones' --
    frame_jugador = ttk.LabelFrame(tab_regiones, text="Vida del jugador", padding="10")
    frame_jugador.pack(fill=tk.X, pady=5, padx=5)
    ttk.Label(frame_jugador, text="Top:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Entry(frame_jugador, width=10, textvariable=player_top_var).grid(row=0, column=1)
    ttk.Label(frame_jugador, text="Left:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ttk.Entry(frame_jugador, width=10, textvariable=player_left_var).grid(row=1, column=1)
    ttk.Label(frame_jugador, text="Width:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
    ttk.Entry(frame_jugador, width=10, textvariable=player_width_var).grid(row=0, column=3)
    ttk.Label(frame_jugador, text="Height:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
    ttk.Entry(frame_jugador, width=10, textvariable=player_height_var).grid(row=1, column=3)

    frame_monstruo = ttk.LabelFrame(tab_regiones, text="Vida del Monstruo", padding="10")
    frame_monstruo.pack(fill=tk.X, pady=5, padx=5)
    ttk.Label(frame_monstruo, text="Top:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Entry(frame_monstruo, width=10, textvariable=monster_top_var).grid(row=0, column=1)
    ttk.Label(frame_monstruo, text="Left:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    ttk.Entry(frame_monstruo, width=10, textvariable=monster_left_var).grid(row=1, column=1)
    ttk.Label(frame_monstruo, text="Width:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
    ttk.Entry(frame_monstruo, width=10, textvariable=monster_width_var).grid(row=0, column=3)
    ttk.Label(frame_monstruo, text="Height:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
    ttk.Entry(frame_monstruo, width=10, textvariable=monster_height_var).grid(row=1, column=3)

    # -- Widgets en la pestaña 'Configuración General' --
    frame_potions = ttk.LabelFrame(tab_general, text="Activar poción", padding="10")
    frame_potions.pack(fill=tk.X, pady=5, padx=5)
    ttk.Label(frame_potions, text="Usar poción si la vida es menor que (%):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Entry(frame_potions, width=10, textvariable=potions_life_var).grid(row=0, column=1)

    frame_monsters_list = ttk.LabelFrame(tab_general, text="Lista de Monstruos a Atacar", padding="10")
    frame_monsters_list.pack(fill=tk.X, pady=5, padx=5)
    for i in range(8):
        ttk.Label(frame_monsters_list, text=f"Monstruo {i+1}:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(frame_monsters_list, width=40, textvariable=monster_vars[i]).grid(row=i, column=1, padx=5, pady=2, sticky="ew")
    frame_monsters_list.columnconfigure(1, weight=1)

    # -- Botón de Guardar --
    boton_guardar = ttk.Button(
        parent_window, 
        text="Guardar Configuración en Archivo", 
        command=guardar_configuracion
    )
    boton_guardar.pack(pady=10, padx=10, fill=tk.X)

    # -- Carga de datos inicial --
    cargar_configuracion_inicial()

# --- NUEVO: BLOQUE PARA EJECUCIÓN DIRECTA ---
if __name__ == '__main__':
    # Este código solo se ejecuta si corres "python settings/settings.py" directamente.
    # Es útil para probar la ventana de configuración de forma aislada.
    ventana_de_prueba = tk.Tk()
    ventana_de_prueba.title("Panel de Configuración (Modo de Prueba)")
    ventana_de_prueba.geometry("480x480")
    
    create_settings_ui(ventana_de_prueba) # Llama a la función para construir la UI
    
    ventana_de_prueba.mainloop()