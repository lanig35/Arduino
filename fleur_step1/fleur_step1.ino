
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change :
const long interval = 5000;           // interval at which to blink (milliseconds)

// connecteurs
const int pin_temperature = A5;
const int pin_humidite = A0;
const int pin_secheresse = 3;

// variables de calcul
int sensor_value = 0;
float voltage = 0.0;

// valeurs capateurs
float temperature = 0.0;
float humidite = 0.0;
int secheresse = 0;

void setup() {
  //
  Serial.begin (9600);
  // set the digital pin as input:
  pinMode(pin_secheresse, INPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;

    // lecture temperature
    analogRead (pin_temperature);
    sensor_value = analogRead (pin_temperature);
    voltage = (sensor_value / 1024.0) * 5.0;
    temperature = (voltage - 0.5) * 100;

    // lecture humidite
    analogRead (pin_humidite);
    sensor_value = analogRead (pin_humidite);
    sensor_value = constrain (sensor_value, 100, 1000);
    humidite = map (sensor_value, 100, 1000, 100, 0);
    secheresse = digitalRead (pin_secheresse);
    
    Serial.print ("t: "); Serial.println (temperature);
    Serial.print ("h: "); Serial.print (humidite);
    Serial.print (" - s: "); Serial.println (secheresse);
  }
}

