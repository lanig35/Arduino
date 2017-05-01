#include <SoftwareSerial.h>

SoftwareSerial hc05 (2, 3);
int led = 5;

void setup() {
  // put your setup code here, to run once:
  Serial.begin (9600);
  hc05.begin (9600);
  pinMode (led, OUTPUT);
  digitalWrite (led, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (hc05.available () > 0) {
    char c = hc05.read ();
    Serial.print ("Received: "); Serial.println (c);
    if (c == 'l') {
      digitalWrite (led, HIGH);
    } else {
      digitalWrite (led, LOW);
    }
  }
}
