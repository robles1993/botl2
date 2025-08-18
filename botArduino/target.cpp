#include <Keyboard.h>
#include "Mouse.h"
#include "mouse_functions.h"

#define MAX_MONSTERS 20   // tamaño máximo del array dinámico
String monsterList[MAX_MONSTERS];
int numberOfMonsters = 0;
int currentMonsterIndex = 0;

void escribirLento(String texto, int retraso) {
  for (int j = 0; j < texto.length(); j++) {
    Keyboard.print(texto[j]);
    delay(retraso);
  }
}

// 🔹 llamada desde el .ino cuando llega "M:..."
void updateMonsterList(const String &semicolonList) {
  numberOfMonsters = 0;
  currentMonsterIndex = 0;

  int start = 0;
  int idx;
  while ((idx = semicolonList.indexOf(';', start)) != -1 && numberOfMonsters < MAX_MONSTERS) {
    monsterList[numberOfMonsters++] = semicolonList.substring(start, idx);
    start = idx + 1;
  }
  if (start < semicolonList.length() && numberOfMonsters < MAX_MONSTERS) {
    monsterList[numberOfMonsters++] = semicolonList.substring(start);
  }
}

void target() {
  if (numberOfMonsters == 0) return; // no hay lista cargada

  if (currentMonsterIndex >= numberOfMonsters) {
    currentMonsterIndex = 0;
  }

  const int distanciaGiro = 300; 

  Mouse.press(MOUSE_RIGHT);
  delay(100);
  Mouse.move(distanciaGiro, 0, 0);
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

  currentMonsterIndex++;
}