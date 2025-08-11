#include "mouse_functions.h"
#include "Keyboard.h"

// La implementación ahora usa el parámetro 'keyToPress'.
void pickUp(char keyToPress) {
  Keyboard.press(KEY_F4);  // Presiona F1
  delay(100);               // Mantiene la tecla presionada 50 ms
  Keyboard.release(KEY_F4); // Suelta F1

  delay(1000);               // Hay que hace este tiempo que sea random entre 1 y 3 segundos

  Keyboard.press(KEY_F4);  // Presiona F1
  delay(100);               // Mantiene la tecla presionada 50 ms
  Keyboard.release(KEY_F4); // Suelta F1

  delay(1000);               // Hay que hace este tiempo que sea random entre 1 y 3 segundos

  Keyboard.press(KEY_F4);  // Presiona F1
  delay(100);               // Mantiene la tecla presionada 50 ms
  Keyboard.release(KEY_F4); // Suelta F1
}