#include "mouse_functions.h"
#include "Keyboard.h"

// La implementación ahora usa el parámetro 'keyToPress'.
void attack() {
  Keyboard.press(KEY_F1);  // Presiona F1
  delay(100);               // Mantiene la tecla presionada 50 ms
  Keyboard.release(KEY_F1); // Suelta F1
}