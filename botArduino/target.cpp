#include <Keyboard.h>
#include "Mouse.h"

const int numberOfMonsters = 4;
String monsterList[numberOfMonsters] = {
  "Toad Lord",
  "Marsh Stakato Soldier",
  "Marsh Stakato Worker",
  "Giant Crimson And"
};

int currentMonsterIndex = 0;

void escribirLento(String texto, int retraso) {
  for (int j = 0; j < texto.length(); j++) {
    Keyboard.print(texto[j]);
    delay(retraso);
  }
}

void target() {
  const int distanciaGiro = 300; 
  if (currentMonsterIndex >= numberOfMonsters) {
    currentMonsterIndex = 0;
  }

  Mouse.press(MOUSE_RIGHT);
  delay(100);
  Mouse.move(distanciaGiro, 0, 0); // Giro horizontal
  delay(100);
  Mouse.release(MOUSE_RIGHT);
  delay(150);

  Mouse.press(MOUSE_LEFT);
  delay(50);
  Mouse.release(MOUSE_LEFT);
  delay(100);

  Keyboard.press(KEY_RETURN);
  Keyboard.releaseAll();
  delay(50);

  Keyboard.press(KEY_LEFT_SHIFT);
  Keyboard.press('7'); // "/"
  delay(100);
  Keyboard.releaseAll();
  delay(50);

  escribirLento("target ", 50);
  escribirLento(monsterList[currentMonsterIndex], 50);

  Keyboard.press(KEY_RETURN);
  Keyboard.releaseAll();
  delay(50);

  Keyboard.press(KEY_ESC);
  Keyboard.releaseAll();

  currentMonsterIndex++; // siguiente mob en el próximo intento
}
