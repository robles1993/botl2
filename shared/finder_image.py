import cv2
import numpy as np
import mss

def find_icon_on_screen(icon_paths, confidence_threshold=0.8):
    """
    Toma una captura de pantalla y busca una lista de iconos en ella.

    Args:
        icon_paths (list): Una lista de rutas de archivo para los iconos a buscar.
        confidence_threshold (float): El nivel de confianza (0.0 a 1.0) necesario 
                                     para considerar que se encontró una coincidencia.

    Returns:
        dict: Un diccionario con la información del icono encontrado 
              ({'path': ruta, 'location': (x, y), 'confidence': valor})
              o None si no se encuentra ningún icono.
    """
    # 1. Tomar una captura de la pantalla completa
    with mss.mss() as sct:
        # Usar sct.monitors[1] para el monitor principal
        screenshot = np.array(sct.grab(sct.monitors[1]))
        # Convertir a un formato que OpenCV pueda usar (BGR)
        screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    # 2. Iterar sobre cada ruta de icono proporcionada
    for icon_path in icon_paths:
        try:
            # Cargar la imagen del icono que queremos encontrar
            icon = cv2.imread(icon_path, cv2.IMREAD_COLOR)
            if icon is None:
                print(f"Advertencia: No se pudo cargar el icono en '{icon_path}'. Saltando...")
                continue

            # Obtener las dimensiones del icono para más tarde
            icon_h, icon_w, _ = icon.shape

            # 3. Realizar el Template Matching
            # TM_CCOEFF_NORMED es el método más fiable, da un valor entre -1 y 1
            result = cv2.matchTemplate(screenshot_bgr, icon, cv2.TM_CCOEFF_NORMED)
            
            # Encontrar la ubicación con la mayor coincidencia
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            print(f"Probando '{icon_path}'... Confianza máxima: {max_val:.2f}")

            # 4. Comprobar si la confianza supera nuestro umbral
            if max_val >= confidence_threshold:
                # Calcular el centro del icono encontrado
                center_x = max_loc[0] + icon_w // 2
                center_y = max_loc[1] + icon_h // 2

                print(f"¡Éxito! Icono '{icon_path}' encontrado en ({center_x}, {center_y}) con confianza {max_val:.2f}")
                
                # Devolver toda la información útil
                return {
                    'path': icon_path,
                    'location': (center_x, center_y),
                    'confidence': max_val
                }

        except Exception as e:
            print(f"Error procesando el icono {icon_path}: {e}")
            continue

    # 5. Si el bucle termina sin encontrar nada, devolver None
    return None