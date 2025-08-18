#include "Mouse.h"
#include <Keyboard.h>
#include "mouse_functions.h"
// Esta es la función que mueve el ratón. La separamos para poder llamarla
// solo cuando la necesitemos.


void setup() {
  // Inicializa la comunicación por puerto serie a 9600 baudios.
  // Es crucial que sea la misma velocidad que usará Python.
  Serial.begin(9600);
  Keyboard.begin();
  // Inicializa la funcionalidad del ratón.
  Mouse.begin();
}

void loop() {
  // Comprueba si hay datos disponibles para leer en el puerto serie.
  if (Serial.available() > 0) {

    String comando = Serial.readStringUntil('\n');  // leemos línea completa
    comando.trim();
    if (comando.startsWith("H")) {
      // Antes de leer tecla, espera que haya datos disponibles
      restoreLife();
    }

    if (comando.startsWith("P")) {
      // Antes de leer tecla, espera que haya datos disponibles
      pickUp();
    }

    if (comando.startsWith("A")) {
      attack();
    }

    if (comando.startsWith("N")) {
      nextTarget();
    }
    
    if (comando.startsWith("LT:")) {
      String monsters = comando.substring(3);  // Extrae todo después de "LT:"
      updateMonsterList(monsters);
    }
    // CAMBIO CLAVE: Lógica para la ACCIÓN de hacer target
    else if (comando.startsWith("T")) {
      target();  // Llama a tu función de target
    }

    if (comando == 'M') {
      moverRaton();
    } else if (comando == 'R') {
      resetearBusqueda();
    }
  }
}