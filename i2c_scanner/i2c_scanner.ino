#include <Wire.h>
 
 
void setup()
{
  Wire.begin();
 
  Serial.begin(9600);
  while (!Serial);             // Leonardo: wait for serial monitor
  Serial.println("\nI2C Scanner");
}
 
 
void loop()
{
  byte error, address;
  int nDevices;
 
  Serial.println("Scanning...");
 
  nDevices = 0;
  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
 
    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.print(address,HEX);
      Serial.println("  !");
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknown error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }    
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else {
    Wire.beginTransmission (0x68);
    Wire.write (0x03);
    Wire.endTransmission ();
    Wire.requestFrom (0x68, 2);
    byte num = Wire.read ();
    byte jour = Wire.read ();
    Serial.print (num); Serial.print (" : ");
    Serial.println (jour);
    Wire.beginTransmission (0x68);
    Wire.write (0x08);
    Wire.write (11);
    Wire.endTransmission ();
    Wire.beginTransmission (0x68);
    Wire.write (0x08);
    Wire.endTransmission ();    
    Wire.requestFrom (0x68, 6);    
    for (int i=0; i<6; i++) {
      Serial.println (Wire.read ());
    }
  }
    Serial.println("done\n");
 
  delay(5000);           // wait 5 seconds for next scan
}
