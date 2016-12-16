/*
 Objet:
 
 Description du croquis:
 
*/
#include <LiquidCrystal.h>
LiquidCrystal lcd (12, 11, 8, 7, 6, 5);

// définition des interfaces
const byte lum_pin = A1;
const byte temp_pin = A0;
const byte pot_pin = A2;
const byte led_pin = 3;
const byte button_pin = 2;

// pour conserver etat LED
volatile byte led_state = LOW;

// pour calibrage photoresistance
int lum_min = 1023;
int lum_max = 0;

// pour debounce bouton sur interruption
#define BOUNCE_DELAY 250
volatile unsigned long last_toogle_time = 0;

// pour gestion delai entre 2 acqusitions
#define SENSE_INTERVAL 3000
unsigned long previous_time = 0;

unsigned long current_time = 0;

// variables utilisées dans setup et/ou loop
 int sensor_value = 0;
 int lum_value = 0;
 int pot_value = 0;
 float temp_value = 0.0;
 float voltage = 0.0;
 char msg [32];
 
void setup() {
  // lancement port série
  Serial.begin (9600);
  while (!Serial) {
    ;
  }
  
  // initialisation LCD
  lcd.begin (16, 2);
  lcd.noAutoscroll ();

  // calibrage photoresistance
  pinMode (LED_BUILTIN, OUTPUT);
  digitalWrite (LED_BUILTIN, HIGH);
  lcd.print (F("Calibrage"));
  while (millis () < 10000) {
    analogRead (lum_pin); // lecture en 2 fois pour pb impedance
    sensor_value = analogRead (lum_pin);
    if (sensor_value > lum_max) {
      lum_max = sensor_value;
    }
    if (sensor_value < lum_min) {
      lum_min = sensor_value;
    }
    delay (10);
  }
  sprintf (msg, "M:%4d - m:%4d", lum_max, lum_min);
  lcd.setCursor (0, 1);
  lcd.print (msg);
  digitalWrite (LED_BUILTIN, LOW);
  delay (5000);
  
  // debut des mesures
  pinMode (led_pin, OUTPUT);
  digitalWrite (led_pin, led_state);
  pinMode (button_pin, INPUT);
  attachInterrupt (digitalPinToInterrupt(button_pin), toogle, RISING);

  // ajustement compteur de délais
  last_toogle_time = millis ();
  previous_time = millis ();
  
  // préparation LCD
  lcd.clear ();
  lcd.noBlink ();
  lcd.noCursor ();
  lcd.print (F("Acquisition"));
  lcd.setCursor (0, 1);
}

void loop() {
  current_time = millis ();
  if (current_time - previous_time >= SENSE_INTERVAL) {
    previous_time = current_time;
    
    // lecture capteur temperature (2 fois pour pb impédance ?)
    analogRead (temp_pin);
    sensor_value = analogRead (temp_pin);
    voltage = (sensor_value / 1024.0) * 5.0;
    temp_value = (voltage - 0.5) * 100;
    
    // lecture capteur lumière (idem)
    analogRead (lum_pin);
    lum_value = analogRead (lum_pin);
    lum_value = map (lum_value, lum_min, lum_max, 0, 255);
    
    // lecture potentiomètre (idem)
    analogRead (pot_pin);
    pot_value = analogRead (pot_pin);
    pot_value = map (pot_value, 0, 1023, 0, 255);
    
    // écriture port série
    Serial.print (temp_value);
    Serial.print ("-");
    Serial.print (lum_value);
    Serial.print ("-");
    Serial.println (pot_value);
    // sprintf (msg, "%2.2f-%3d-%3d", temp_value, lum_value, pot_value);
    // Serial.println (msg);
    
    // affichage temps sur LCD
    lcd.setCursor (0, 1);
    lcd.print (current_time/1000);
  }
}

// routine d'interruption
void toogle () {
  current_time = millis ();
  if (current_time - last_toogle_time > BOUNCE_DELAY) {
    last_toogle_time = current_time;
    led_state = !led_state;
    digitalWrite (led_pin, led_state);
  }
}
