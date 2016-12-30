/*
 Objet: interfacer via le port série afin de fournir la
 température, la valeur de 2 potentiomètres ainsi que
 récupérer des ordres pour l'allumagde de 2 LEDs.
 
 Description du croquis:
   TMP36 sur A3
   potentiomètres sur A1 et A2 associés à une LED en D9
   et D10 en mode PWM
   boutons poussoir en D2 et D3 pour bénéficier des
   interruptions associés à des LED en D4 et D5
   une LED en D6 qui clignote à intervalle régulier
*/

#define NOT_AN_INTERRUPT -1

// interfaces des capteurs
const byte temp_pin = A3;
const byte green_pot = A1;

// interface des leds
const byte red_led = 4;
const byte blue_led = 5;
const byte yellow_led = 6;
const byte white_led = 7;
const byte green_pot_led = 10;

// interface des boutons
const byte red_button = 2;
const byte blue_button = 3;

// interface piezzo
const byte piezzo = 8;

// pour conserver etat LED
byte yellow_state = LOW;
byte white_state = LOW;
volatile byte red_state = LOW;
volatile byte blue_state = LOW;

// pour debounce bouton sur interruption
#define BOUNCE_DELAY 250
volatile unsigned long last_toogle_time = 0;

// pour lecture commande sur port série
char cmd [2];
bool cmd_end = false;
byte index_cmd = 0;

// pour gestion delai entre 2 acqusitions
#define TEMP_INTERVAL 10000
#define POT_INTERVAL  3000
#define YELLOW_INTERVAL 1000

unsigned long prev_temp_time = 0;
unsigned long prev_pot_time = 0;
unsigned long prev_yellow_time = 0;
unsigned long current_time = 0;

// variables utilisées dans setup et/ou loop
int sensor_value = 0;
int green_pot_value = 0;
int blue_pot_value = 0;
float temp_value = 0.0;
float voltage = 0.0;

// tableau des notes
unsigned int notes[5] = {262, 294, 330, 394, 440};

// lecture potentiomètre et scintillement LED
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

// lecture caractère port série
void serialEvent () {
  while (Serial.available ()) {
    char recv = (char)Serial.read ();
    if (recv == '\n') {
      cmd_end = true;
      index_cmd = 0;
    } else {
      if (index_cmd <= 1) {
        cmd[index_cmd] = recv;
        index_cmd++;
      }
    }
  }
}

void setup() {
  // lancement port série
  Serial.begin (9600);
  while (!Serial) {
    ;
  }
  
  // sequence d'accueil
  pinMode (yellow_led, OUTPUT);
  for (int i=0; i<10; i++) {
    tone (piezzo, notes[i%5]);
    digitalWrite (yellow_led, HIGH);
    delay (i * 100);
    digitalWrite (yellow_led, LOW);
    delay (200);
  }
  noTone (piezzo);
  
  // LED en mode PWN avec potentiometre
  pinMode (green_pot_led, OUTPUT);
  
  // LED blanche
  pinMode (white_led, OUTPUT);
  digitalWrite (white_led, white_state);
  
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
  prev_temp_time = millis ();
  prev_pot_time = prev_temp_time;
  prev_yellow_time = prev_temp_time;
}

void loop() {
  current_time = millis ();
  
  if (cmd_end == true) {
    switch (cmd[0]) {
      case 'R':
      {
        if (isDigit (cmd[1])) {
          // inversion LED rouge
          byte state = cmd[1] - '0';
          if ((state == LOW) || (state == HIGH)) {
            red_state = state;
            digitalWrite (red_led, red_state);
          }
        }
        break;
      }
      case 'B':
      {
        if (isDigit (cmd[1])) {
          // inversion LED bleue
          byte state = cmd[1] - '0';
          if ((state == LOW) || (state == HIGH)) {
            blue_state = state;
            digitalWrite (blue_led, blue_state);
          }
        }
        break;
      }
      case 'W':
      {
        if (isDigit (cmd[1])) {
          // inversion LED blanche
          byte state = cmd[1] - '0';
          if ((state == LOW) || (state == HIGH)) {
            white_state = state;
            digitalWrite (white_led, white_state);
          }
        }
        break;
      }
      case 'P':
      {
        if (isDigit (cmd[1])) {
          // action piezzo
          byte note = cmd[1] - '0';
          if (note >= 5) {
            noTone (piezzo);
          } else {
            tone (piezzo, notes[note%5]);
          }
        }
        break;
      }
      default:
        break;
    }
    cmd_end = false;
  }
  
  if (current_time - prev_temp_time >= TEMP_INTERVAL) {
    prev_temp_time = current_time;
    
    // lecture capteur temperature (2 fois pour pb impédance ?)
    analogRead (temp_pin);
    sensor_value = analogRead (temp_pin);
    voltage = (sensor_value / 1024.0) * 5.0;
    temp_value = (voltage - 0.5) * 100;
    
    Serial.print ("t:");
    Serial.println (temp_value);
  }
  
  if (current_time - prev_pot_time >= POT_INTERVAL) {
    prev_pot_time = current_time;
    
    // écriture mesures port série
    Serial.print ("p:");
    Serial.println (green_pot_value);
    // scintillement blanc
    white_state = !white_state;
    digitalWrite (white_led, white_state);
  }
  
  if (current_time - prev_yellow_time >= YELLOW_INTERVAL) {
    prev_yellow_time = current_time;
    // lecture potentiometre
    green_pot_value = analyse_pot (green_pot, green_pot_led);
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
