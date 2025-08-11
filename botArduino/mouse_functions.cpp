#include <Arduino.h>      // Necesario para funciones básicas de Arduino como delay()
#include "mouse_functions.h" // Incluye las declaraciones de este mismo fichero
#include "Mouse.h"           // Necesario para las funciones de Mouse

// Esta es la implementación (el código real) de la función.
void moverRaton() {
  int moveAmount = 20;  // Píxeles a mover
  int moveDelay = 50;   // Pausa entre movimientos
  int repetitions = 5;  // Cuántas veces hacer el ciclo izquierda-derecha

  for (int i = 0; i < repetitions; i++) {
    Mouse.move(-moveAmount, 0, 0); // Mueve a la izquierda
    delay(moveDelay);
    Mouse.move(moveAmount, 0, 0);  // Mueve a la derecha
    delay(moveDelay);
  }
}