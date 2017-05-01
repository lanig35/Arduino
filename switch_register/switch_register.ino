
int data = 2;
int clk = 3;
int latch = 4;

void setup() {
  // put your setup code here, to run once:
  pinMode (data, OUTPUT);
  pinMode (clk, OUTPUT);
  pinMode (latch, OUTPUT);
}

void updateLEDs(int value) {
  digitalWrite(latch, LOW);     //Pulls the chips latch low
  shiftOut(data, clk, LSBFIRST, value); //Shifts out the 8 bits to the shift register
  digitalWrite(latch, HIGH);   //Pulls the latch high displaying the data
}

void loop() {
  // put your main code here, to run repeatedly:
  byte leds = 0;
  int delayTime = 500; //the number of milliseconds to delay between LED updates
  for (int i = 0; i < 8; i++) {
    leds = 0;
    bitSet (leds, i);
    updateLEDs(leds);
    delay(delayTime);
  }
}
