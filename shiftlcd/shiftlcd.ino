
/*
   3-pin Arduino interface for HD44780 LCDs via 74HC595 Shift Register
*/
#include <Wire.h>
#include <ShiftLCD.h>
#include <RTClib.h>

ShiftLCD lcd(3, 6, 5);

const int pin_temperature = A0;
const int buzzer = 15;

const int ctrlEcran = 7;
const int ctrlAlarm = 8;
const int ctrlHorloge = 9;

const int swqe = 2;
volatile unsigned int count = 0;

unsigned long previousMillis = 0;

RTC_DS1307 rtc;
char daysOfTheWeek[7][12] = {"Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"};
bool rtc_ok = true;

/** Mesure la référence interne à 1.1 volts */
unsigned int analogReadReference(void) {
  /* Elimine toutes charges résiduelles */
  ADMUX = 0x4F;
  delayMicroseconds(5);

  /* Sélectionne la référence interne à 1.1 volts comme point de mesure, avec comme limite haute VCC */
  ADMUX = 0x4E;
  delayMicroseconds(200);

  /* Active le convertisseur analogique -> numérique */
  ADCSRA |= (1 << ADEN);

  /* Lance une conversion analogique -> numérique */
  ADCSRA |= (1 << ADSC);

  /* Attend la fin de la conversion */
  while (ADCSRA & (1 << ADSC));

  /* Récupère le résultat de la conversion */
  return ADCL | (ADCH << 8);
}

void clock () {
  count ++;
}

void setup() {
  Serial.begin (9600);

  lcd.begin(16, 2);
  lcd.print("Début");

  if (! rtc.begin ()) {
    Serial.println ("RTC absent");
    rtc_ok = false;
  } else {
    if (! rtc.isrunning()) {
      Serial.println ("Ajustement RTC");
      rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }
  }

  pinMode (buzzer, OUTPUT);
  pinMode (ctrlEcran, INPUT_PULLUP);
  pinMode (ctrlAlarm, INPUT_PULLUP);
  pinMode (ctrlHorloge, INPUT_PULLUP);

  pinMode (swqe, INPUT_PULLUP);
  attachInterrupt (digitalPinToInterrupt (swqe), clock, CHANGE);
  rtc.writeSqwPinMode (0x10);
}

void loop() {
  noInterrupts();
  if (count >= 10) {
    Serial.println ("Compteur = 10");
    count = 0;
  }
  interrupts ();

  unsigned long currentMillis = millis();
  if ((currentMillis - previousMillis) >= 1000) {
    previousMillis = currentMillis;
    analogRead (pin_temperature);
    int sensor_value = analogRead (pin_temperature);
    float voltage = (sensor_value / 1024.0) * 5.0;
    float temperature = (voltage - 0.5) * 100;
    Serial.println (temperature);

    DateTime current = rtc.now ();
    lcd.setCursor (0, 0);
    String msg1 (daysOfTheWeek[current.dayOfTheWeek()]);
    msg1 = msg1 + " " + current.day() + " " + current.month();
    // lcd.print(daysOfTheWeek[current.dayOfTheWeek()]);
    lcd.print (msg1);
    lcd.setCursor(0, 1);
    //  lcd.print(millis() / 1000);
    String msg (current.hour());
    msg = msg + "/" + current.minute() + "/" + current.second();
    lcd.print (msg);
  }
  //  float tension_alim = (1023 * 1.1) / analogReadReference();
  //  Serial.println(tension_alim, 3);

}
