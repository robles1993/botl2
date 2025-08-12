#include "mouse_functions.h"
#include "Keyboard.h"

// La implementación ahora usa el parámetro 'keyToPress'.
void pickUp() {
  int moveDelay = 500;  // Pausa entre movimientos
  int repetitions = 5;  // Cuántas veces repetir
  for (int i = 0; i < repetitions; i++) {
    Keyboard.press(KEY_F4);    // Presiona F1
    delay(100);                // Mantiene la tecla presionada 50 ms
    Keyboard.release(KEY_F4);  // Suelta F1
  }
}
