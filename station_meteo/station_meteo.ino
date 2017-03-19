/*

*/

#include <Servo.h>

Servo myServo;
const int pinServo = 9;

const int redLed = 4;
const int greenLed = 3;
const int blueLed = 2;

// pour lecture pluie et température sur port série
bool received = false;
float pluie = 0.0;
float temperature = 0.0;

void setup() {
  // activation liaison série
  Serial.begin (9600);

  // initialisation du moteur servo
  myServo.attach (pinServo);
  myServo.writeMicroseconds (1530);

  // initialisation des PINs de l'alarme RGB
  pinMode (redLed, OUTPUT); digitalWrite (redLed, LOW);
  pinMode (greenLed, OUTPUT); digitalWrite (greenLed, HIGH);
  pinMode (blueLed, OUTPUT); digitalWrite (blueLed, LOW);
}

void loop() {
  // si des données méteo on été reçues via la liaison série
  if (received == true) {
    received = false;
    Serial.print("Temperature: "); Serial.println(temperature);
    Serial.print("Pluie: "); Serial.println(pluie);
    afficheAlarme (temperature);
    afficheMeteo (temperature, pluie);
  }
}

void afficheAlarme (float temperature) {
  if (temperature >= 25) {
    digitalWrite (redLed, HIGH);
    digitalWrite (greenLed, LOW);
    digitalWrite (blueLed, LOW);
  }
  if (temperature > 0 && temperature < 25) {
    digitalWrite (redLed, LOW);
    digitalWrite (greenLed, HIGH);
    digitalWrite (blueLed, LOW);
  }
  if (temperature <= 0) {
    digitalWrite (redLed, LOW);
    digitalWrite (greenLed, LOW);
    digitalWrite (blueLed, HIGH);
  }
}

void serialEvent () {
  while (Serial.available()) {
    temperature = Serial.parseFloat ();
    pluie = Serial.parseFloat ();
  }
  received = true;
}

void afficheMeteo (float temperature, float pluie) {
  if (pluie < 6) {
    if (temperature > 20) {
      Serial.println("lunettes et pieds nus");
      myServo.writeMicroseconds (2000); // 0 degré
    }
    if (temperature > 5 && temperature <= 20) {
      Serial.println("Chaussures de ville");
      myServo.writeMicroseconds (1530); // 45 degré
    }
    if (temperature < 5) {
      Serial.println("Bonnet et moom boots");
      myServo.writeMicroseconds (630); // 135 degré
    }
  } else {
    Serial.println("capuche et bottes");
    myServo.writeMicroseconds(1060); //90 degré
  }
}

