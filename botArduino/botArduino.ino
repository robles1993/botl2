#include "Mouse.h"
#include "mouse_functions.h" 
// Esta es la función que mueve el ratón. La separamos para poder llamarla
// solo cuando la necesitemos.


void setup() {
  // Inicializa la comunicación por puerto serie a 9600 baudios.
  // Es crucial que sea la misma velocidad que usará Python.
  Serial.begin(9600);

  // Inicializa la funcionalidad del ratón.
  Mouse.begin();
}

void loop() {
  // Comprueba si hay datos disponibles para leer en el puerto serie.
  if (Serial.available() > 0) {
    // Lee el carácter entrante.
    char comando = Serial.read(); // Lee primer byte --> 'H'
    if (comando == 'H') {
        // Antes de leer tecla, espera que haya datos disponibles
        while (Serial.available() == 0) {}
        char tecla = Serial.read();  // Lee segundo byte --> '3'
        restoreLife(tecla);
    }
  }
}