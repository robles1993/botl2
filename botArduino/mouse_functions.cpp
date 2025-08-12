#include <Arduino.h>
#include "mouse_functions.h" // Asegúrate que coincida con tu .h
#include "Mouse.h"

// Prototipo de la función de otro fichero.
void nextTarget();

// Variable global estática para recordar el progreso del círculo.
// Su valor se conserva entre llamadas a moverRaton().
static int pasoActualDelCirculo = 0;

/**
 * @brief Realiza un clic izquierdo y luego busca el siguiente objetivo.
 * Se mantiene tu función.
 */
void leftClickMouse() {
  Serial.println("-> Clic izquierdo + Next Target.");
  Mouse.press(MOUSE_LEFT);
  delay(50);
  Mouse.release(MOUSE_LEFT);
  delay(100);
  nextTarget();  
}

/**
 * @brief REALIZA UN ÚNICO PASO de la rutina de búsqueda circular.
 * 
 * Esta función ya no contiene un bucle. Es llamada repetidamente por Python.
 * Si se llama 8 veces, completará un círculo.
 */
void moverRaton() {
  // --- PARÁMETROS DEL CÍRCULO (se mantienen) ---
  const int ladosDelCirculo = 8; 
  const int distanciaGiro = 300; 
  const int tiempoCaminandoPorLado = 700; 

  Serial.print("-> Ejecutando paso de búsqueda ");
  Serial.println(pasoActualDelCirculo + 1);

  // --- PASO 1: Caminar y targetear ---
  leftClickMouse();
  delay(tiempoCaminandoPorLado);

  // --- PASO 2: Girar la cámara para el siguiente paso ---
  Mouse.press(MOUSE_RIGHT);
  delay(100);
  Mouse.move(distanciaGiro, 0, 0); // Giro horizontal
  delay(100);
  Mouse.release(MOUSE_RIGHT);
  delay(150);

  // Avanzamos al siguiente paso.
  pasoActualDelCirculo++;

  // Si hemos completado el círculo, lo reiniciamos para la próxima vez.
  if (pasoActualDelCirculo >= ladosDelCirculo) {
    pasoActualDelCirculo = 0;
  }
}

/**
 * @brief NUEVA FUNCIÓN: Resetea el contador de búsqueda.
 * Se llama desde Python cuando se encuentra un enemigo para interrumpir el ciclo.
 */
void resetearBusqueda() {
  pasoActualDelCirculo = 0;
  Serial.println("-> Búsqueda interrumpida por Python. Contador de pasos reseteado.");
}