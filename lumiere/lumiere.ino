/*
 Objet:
 
 Description du croquis:
 
*/

#define NOT_AN_INTERRUPT -1

// interfaces des capteurs
const byte lum_pin = A2;
const byte temp_pin = A3;
const byte pot_pin = A1;

// interface des leds
const byte red_led = 4;
const byte blue_led = 5;
const byte yellow_led = 6;
const byte pot_led = 9;

// interface des boutons
const byte red_button = 2;
const byte blue_button = 3;

// pour conserver etat LED
byte yellow_state = LOW;
volatile byte red_state = LOW;
volatile byte blue_state = LOW;

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
 
void setup() {
  // lancement port série
  Serial.begin (9600);
  while (!Serial) {
    ;
  }

  // calibrage photoresistance
  pinMode (yellow_led, OUTPUT);
  digitalWrite (yellow_led, HIGH);
  while (millis () < 10000) {
    analogRead (lum_pin); // lecture en 2 fois pour pb impedance
    sensor_value = analogRead (lum_pin);
    if (sensor_value > lum_max) {
      lum_max = sensor_value;
    }
    if (sensor_value < lum_min) {
      lum_min = sensor_value;
    }
  }
  digitalWrite (yellow_led, LOW);
  
  // LED en mode PWN avec potentiometre
  pinMode (pot_led, OUTPUT);
  
  // mise en place interruption boutons
  pinMode (red_led, OUTPUT);
  digitalWrite (red_led, red_state);
  pinMode (red_button, INPUT);
  attachInterrupt (digitalPinToInterrupt(red_button), toogle_red, RISING);

  pinMode (blue_led, OUTPUT);
  digitalWrite (blue_led, blue_state);
  pinMode (blue_button, INPUT);
  attachInterrupt (digitalPinToInterrupt(blue_button), toogle_blue, RISING);

  // ajustement compteur de délais
  last_toogle_time = millis ();
  previous_time = millis ();
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
    lum_value = constrain (lum_value, 0, 255);
    
    // lecture potentiomètre (idem)
    analogRead (pot_pin);
    pot_value = analogRead (pot_pin);
    pot_value = map (pot_value, 0, 1023, 0, 255);
    // lumiere LED
    analogWrite (pot_led, pot_value);
    
    // écriture mesures port série
    Serial.print (temp_value);
    Serial.print ("-");
    Serial.print (lum_value);
    Serial.print ("-");
    Serial.println (pot_value);
    
    // scintillement jaune
    yellow_state = !yellow_state;
    digitalWrite (yellow_led, yellow_state);
  }
}

// routine d'interruption
void toogle_red () {
  current_time = millis ();
  if (current_time - last_toogle_time > BOUNCE_DELAY) {
    last_toogle_time = current_time;
    red_state = !red_state;
    digitalWrite (red_led, red_state);
  }
}

void toogle_blue () {
  current_time = millis ();
  if (current_time - last_toogle_time > BOUNCE_DELAY) {
    last_toogle_time = current_time;
    blue_state = !blue_state;
    digitalWrite (blue_led, blue_state);
  }
}
