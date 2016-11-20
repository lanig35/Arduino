/*
  Arduino Starter Kit example
 Project 14  - Tweak the Arduino Logo
 
 This sketch is written to accompany Project 14 in the
 Arduino Starter Kit
 
 Parts required:
 10 kilohm potentiometer
 
 Software required : 
 Processing http://processing.org
 Active internet connection
 
 Created 18 September 2012
 by Scott Fitzgerald
 
 http://arduino.cc/starterKit
 
 This example code is part of the public domain 
 */

int pot;
byte angle;
int i;

void setup() {
  // initialize serial communication
  Serial.begin(9600);
  i = 0;
}

void loop() {
  // read the value of A0, divide by 4 and 
  // send it as a byte over the serial connection
  pot = analogRead(A0);
  angle = map (pot, 0, 1023, 0, 255);
  if (i < 50) {
  //  Serial.println (angle);
    Serial.write (angle);
  //  i++;
  }
  delay(10000);
}


