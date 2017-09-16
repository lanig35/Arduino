/*
 Fade

 This example shows how to fade an LED on pin 9
 using the analogWrite() function ou le TIMER 2 
 configuré en Phase Correct PWM
 */

const byte led = 11;

const byte color [] = {0,6,15,30,66,102,144,255};
byte index = 0;

void fadeLed (const byte pin, const byte duty) {
  /*
   * TODO: vérifier pin PB3 - 11 arduino - ou PD3 - 3 arduino
   * pour sélectionner le port registre COM2
   * PB3: COM2Ax et PD3: COM2Bx
   * verifier fréquence f = 16Mhz / (N * 2 * 255)
   * ici N = 8 avec CS22/1/0 = 010
   * WGM21 = 0 et WGM20 = 1 ==> phase correct PWM
   * WGM22 = 0 pour TOP = 0xFF - 255
   */
  TCCR2A |= (1<<COM2A1) | (1<<WGM20);
  // TCCR2A = 0b10000001;
  // prescaler à 8 - lance le timer  (CS22/1/0 = 0 timer stoppé)
  TCCR2B |= (1<<CS21);
  // TCCR2B = 0b00000010;
  OCR2A = duty;
}

void setup() {
  // desactivation Analog Comparator
  ACSR |= (1<<ACD);
  // desactivation ADC module
  ADCSRA &= ~(1<<ADEN); // mise à zéro flag ADEN
  // désactivation Digital Input sur port analogique
  DIDR1 |= 0b00000011;
  DIDR0 |= 0b00011111;
  // pinMode(led, OUTPUT);
  DDRB |= (1<<PB3);
}

void loop() {
  // set the brightness of led:
  //analogWrite(led, color[index]);
  fadeLed (PB3, color[index]);
  
  // change the brightness for next time through the loop:
  index++;
  if (index >= 7) {
    index = 0;
  }
  // wait for 30 milliseconds to see the dimming effect
  delay(200);
}
