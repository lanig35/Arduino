#include <IRremote.h>

/*
  Arduino Starter Kit example
 Project 9  - Motorized Pinwheel

 This sketch is written to accompany Project 9 in the
 Arduino Starter Kit

 Parts required:
 10 kilohm resistor
 pushbutton
 motor
 9V battery
 IRF520 MOSFET
 1N4007 diode

 Created 13 September 2012
 by Scott Fitzgerald

 http://www.arduino.cc/starterKit

 This example code is part of the public domain
 */

// named constants for the switch and motor pins
const int switchPin = 4; // the number of the switch pin
const int motorPin =  9; // the number of the motor pin

int switchState = 0;  // variable for reading the switch's status

int receiver = 11;
IRrecv irrecv (receiver);
decode_results results;

void setup() {
  // initialize the motor pin as an output:
  pinMode(motorPin, OUTPUT);
  // initialize the switch pin as an input:
  pinMode(switchPin, INPUT);
  
  Serial.begin (9600);
  Serial.println ("debut");
  irrecv.enableIRIn ();
}

void loop() {
  bool motorOn = false;
  if (irrecv.decode (&results)) {
    Serial.print (results.value, HEX);
    switch (results.value) {
      case 0xFF6897: 
        Serial.println (" : Key 1");
        motorOn = true;
        break;
      default:
        Serial.println (" : Inconnu");
        break;
    }
    irrecv.resume();
  }
  
  // read the state of the switch value:
  switchState = digitalRead(switchPin);

  // check if the switch is pressed.
  if (switchState == HIGH || motorOn == true) {
    // turn motor on:
    digitalWrite(motorPin, HIGH);
  } else {
    // turn motor off:
    digitalWrite(motorPin, LOW);
  }

  delay (100);
}
