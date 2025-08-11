import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- 1. FUNCIÓN DE GUARDADO (Sin cambios) ---
def guardar_configuracion():
    """
    Guarda los valores de la ventana en un archivo 'config.json'.
    """
    try:
        config_data = {
            "player_detector": {
                "region": {
                    "top": int(player_top_var.get()),
                    "left": int(player_left_var.get()),
                    "width": int(player_width_var.get()),
                    "height": int(player_height_var.get())
                }
            },
            "monster_detector": {
                "region": {
                    "top": int(monster_top_var.get()),
                    "left": int(monster_left_var.get()),
                    "width": int(monster_width_var.get()),
                    "height": int(monster_height_var.get())
                }
            },
            "potions_life": {
                "life": int(potions_life_var.get()) 
            }
        }

        with open('settings/config.json', 'w') as archivo_json:
            json.dump(config_data, archivo_json, indent=4)
        
        messagebox.showinfo("Éxito", "¡La configuración se ha guardado en 'config.json'!")

    except ValueError:
        messagebox.showerror("Error de Entrada", "Por favor, asegúrate de que todos los campos contengan solo números.")
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"No se pudo guardar el archivo: {e}")

# --- 2. FUNCIÓN DE CARGA (Sin cambios) ---
def cargar_configuracion_inicial():
    """
    Carga la configuración desde 'config.json' al iniciar.
    Si no existe, crea el archivo con valores por defecto.
    """
    try:
        with open('settings/config.json', 'r') as archivo:
            config = json.load(archivo)
    except FileNotFoundError:
        print("No se encontró 'config.json'. Creando uno con valores por defecto.")
        config = {
            "player_detector": {"region": {"top": 54, "left": 30, "width": 210, "height": 14}},
            "monster_detector": {"region": {"top": 0, "left": 785, "width": 350, "height": 24}},
            "potions_life": {"life": 50}

        }
        with open('settings/config.json', 'w') as archivo:
            json.dump(config, archivo, indent=4)
    
    player_top_var.set(config["player_detector"]["region"]["top"])
    player_left_var.set(config["player_detector"]["region"]["left"])
    player_width_var.set(config["player_detector"]["region"]["width"])
    player_height_var.set(config["player_detector"]["region"]["height"])

    monster_top_var.set(config["monster_detector"]["region"]["top"])
    monster_left_var.set(config["monster_detector"]["region"]["left"])
    monster_width_var.set(config["monster_detector"]["region"]["width"])
    monster_height_var.set(config["monster_detector"]["region"]["height"])

    potions_life_var.set(config["potions_life"]["life"])



# --- 3. CREACIÓN DE LA VENTANA Y LA ESTRUCTURA DE PESTAÑAS ---
ventana = tk.Tk()
ventana.title("Panel de Configuración del Bot")
ventana.geometry("460x320") # Ajustamos el tamaño

# Creamos el Notebook que contendrá las pestañas
notebook = ttk.Notebook(ventana, padding="10")
notebook.pack(fill=tk.BOTH, expand=True)

# Creamos el Frame para la primera pestaña
tab_regiones = ttk.Frame(notebook)
notebook.add(tab_regiones, text="Regiones de Detección")

# Creamos el Frame para una futura segunda pestaña
tab_general = ttk.Frame(notebook)
notebook.add(tab_general, text="Configuración General")
ttk.Label(tab_general, text="Aquí irán otras configuraciones en el futuro.").pack(pady=50)


# --- 4. DEFINICIÓN DE VARIABLES Y WIDGETS DENTRO DE LA PESTAÑA 'Regiones' ---
# Ahora el padre de los LabelFrame es 'tab_regiones'

# Variables de Tkinter para los campos
player_top_var = tk.StringVar()
player_left_var = tk.StringVar()
player_width_var = tk.StringVar()
player_height_var = tk.StringVar()
monster_top_var = tk.StringVar()
monster_left_var = tk.StringVar()
monster_width_var = tk.StringVar()
monster_height_var = tk.StringVar()

# Sección del Jugador
frame_jugador = ttk.LabelFrame(tab_regiones, text="Vida del jugador", padding="10")
frame_jugador.pack(fill=tk.X, pady=5)

ttk.Label(frame_jugador, text="Top:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_jugador, width=10, textvariable=player_top_var).grid(row=0, column=1)
ttk.Label(frame_jugador, text="Left:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_jugador, width=10, textvariable=player_left_var).grid(row=1, column=1)
ttk.Label(frame_jugador, text="Width:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
ttk.Entry(frame_jugador, width=10, textvariable=player_width_var).grid(row=0, column=3)
ttk.Label(frame_jugador, text="Height:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
ttk.Entry(frame_jugador, width=10, textvariable=player_height_var).grid(row=1, column=3)

# Sección del Monstruo
frame_monstruo = ttk.LabelFrame(tab_regiones, text="Vida del Monstruo", padding="10")
frame_monstruo.pack(fill=tk.X, pady=5)

ttk.Label(frame_monstruo, text="Top:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_monstruo, width=10, textvariable=monster_top_var).grid(row=0, column=1)
ttk.Label(frame_monstruo, text="Left:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_monstruo, width=10, textvariable=monster_left_var).grid(row=1, column=1)
ttk.Label(frame_monstruo, text="Width:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
ttk.Entry(frame_monstruo, width=10, textvariable=monster_width_var).grid(row=0, column=3)
ttk.Label(frame_monstruo, text="Height:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky="w")
ttk.Entry(frame_monstruo, width=10, textvariable=monster_height_var).grid(row=1, column=3)


# Curas

# tab_general = ttk.Frame(notebook)
# notebook.add(tab_general, text="Configuración General")
# ttk.Label(tab_general, text="Aquí irán otras configuraciones en el futuro.").pack(pady=50)
potions_life_var = tk.StringVar()


frame_potions = ttk.LabelFrame(tab_general, text="Activar poción", padding="10")
frame_potions.pack(fill=tk.X, pady=5)

ttk.Label(frame_potions, text="menor que :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ttk.Entry(frame_potions, width=10, textvariable=potions_life_var).grid(row=0, column=1)


# --- 5. Botón de Guardar (fuera del Notebook) ---
# Su padre es 'ventana' para que siempre esté visible
boton_guardar = ttk.Button(
    ventana, 
    text="Guardar Configuración en Archivo", 
    command=guardar_configuracion
)
boton_guardar.pack(pady=10, padx=10, fill=tk.X)


# --- 6. Carga de datos y bucle principal ---
cargar_configuracion_inicial()
ventana.mainloop()