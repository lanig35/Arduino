const int trig = 10;
const int echo = 9;
const int buzzer = 2;

void setup() {
  // put your setup code here, to run once:
  pinMode (trig, OUTPUT);
  pinMode (echo, INPUT);
  pinMode (buzzer, OUTPUT);

  Serial.begin (9600);
}

void loop() {
  int duration, distance;
  
  // put your main code here, to run repeatedly:
  digitalWrite (trig, HIGH);
  delay (10);
  digitalWrite (trig, LOW);

  duration = pulseIn (echo, HIGH);
  distance = (duration/2) / 29.1;

  Serial.print ("duration: "); Serial.println (duration);
  Serial.print ("distance: "); Serial.println(distance);
  
  if (distance <= 50 && distance >= 0) {
    tone (2, 1000, 20);
  }
}
