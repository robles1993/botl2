#ifndef MOUSE_FUNCTIONS_H
#define MOUSE_FUNCTIONS_H
#include <Arduino.h>
// Declaración o "prototipo" de la función.
// Solo le dice al compilador que esta función existe.
void moverRaton();
void restoreLife();
void pickUp();
void attack();
void nextTarget();
void leftClickMouse();
void resetearBusqueda();
void target();

void updateMonsterList(const String &semicolonList);

#endif