/*
 Objet:
 
 Description du croquis:
 
*/

#define NOT_AN_INTERRUPT -1

// interfaces des capteurs
const byte blue_pot = A2;
const byte temp_pin = A3;
const byte green_pot = A1;

// interface des leds
const byte red_led = 4;
const byte blue_led = 5;
const byte yellow_led = 6;
const byte blue_pot_led = 9;
const byte green_pot_led = 10;

// interface des boutons
const byte red_button = 2;
const byte blue_button = 3;

// pour conserver etat LED
byte yellow_state = LOW;
volatile byte red_state = LOW;
volatile byte blue_state = LOW;

// pour debounce bouton sur interruption
#define BOUNCE_DELAY 250
volatile unsigned long last_toogle_time = 0;

// pour gestion delai entre 2 acqusitions
#define SENSE_INTERVAL 10000
unsigned long previous_time = 0;
unsigned long current_time = 0;

// variables utilisées dans setup et/ou loop
int sensor_value = 0;
int green_pot_value = 0;
int blue_pot_value = 0;
float temp_value = 0.0;
float voltage = 0.0;
 
int analyse_pot (byte pot, byte led) {
  int pot_value = 0;
  
  // lecture potentiomètre (idem)
  analogRead (pot);
  pot_value = analogRead (pot);
  pot_value = map (pot_value, 0, 1023, 0, 255);
  // lumiere LED
  analogWrite (led, pot_value);
  return (pot_value);
}

void setup() {
  // lancement port série
  Serial.begin (9600);
  while (!Serial) {
    ;
  }

  // sequence d'accueil
  pinMode (yellow_led, OUTPUT);
  for (int i=1; i<10; i++) {
    digitalWrite (yellow_led, HIGH);
    delay (i * 100);
    digitalWrite (yellow_led, LOW);
    delay (200);
  }
  
  // LEDs en mode PWN avec potentiometres
  pinMode (blue_pot_led, OUTPUT);
  pinMode (green_pot_led, OUTPUT);
  
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
    
    blue_pot_value = analyse_pot (blue_pot, blue_pot_led);
    green_pot_value = analyse_pot (green_pot, green_pot_led);
    
    // écriture mesures port série
    Serial.print (temp_value);
    Serial.print ("-");
    Serial.print (green_pot_value);
    Serial.print ("-");
    Serial.println (blue_pot_value);
    
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
