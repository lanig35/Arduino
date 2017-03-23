#include <SPI.h>
#include <Ethernet2.h>

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0x90, 0xA2, 0xDA, 0x10, 0xF7, 0x05
};
IPAddress ip(192, 168, 1, 177);

// Initialize the Ethernet server library
// with the IP address and port you want to use
// (port 80 is default for HTTP):
EthernetServer server(80);

 // will store last time sensors were read
unsigned long previousMillis = 0;
       
 // interval at which to read sensors (milliseconds
const long interval = 10000;          

// connecteurs
const int pin_temperature = A5;
const int pin_humidite = A0;
const int pin_secheresse = 3;
const int pin_led = 2;

// variables de calcul
int sensor_value = 0;
float voltage = 0.0;

// valeurs capteurs
float temperature = 0.0;
float humidite = 0.0;
int secheresse = 0;

void setup() {
  pinMode(pin_secheresse, INPUT);
  pinMode(pin_led, OUTPUT);
    
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }

  // start the Ethernet connection and the server:
  //Ethernet.begin(mac, ip);
  Ethernet.begin(mac);
  server.begin();
  Serial.print("server is at ");
  Serial.println(Ethernet.localIP());
}


void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time we read the sensors
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

    digitalWrite (pin_led, secheresse);
  }
  
  // listen for incoming clients
  EthernetClient client = server.available();
  if (client) {
    Serial.println("new client");
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println("Refresh: 10");  // refresh the page automatically every 10 sec
          client.println();
          
          client.println ("<!DOCTYPE HTML>");
          client.println ("<html lang=fr>");
          client.println ("<head>");
          client.println ("<meta charset=\"utf-8\"/>");
          client.println ("<title>Plante Connectée</title>");
          client.println ("</head>");
          client.println ("<body>");
          client.println ("<h1 style=\"color:blue;\">Relevé Capteurs</h1>");
          
          // output the value of sensors
          client.print ("<h2>Temperature: ");
          client.print (temperature); client.println(" °</h2>");
          client.print ("<h2>Humidite: ");
          client.print (humidite); client.println(" %</h2>");

          client.println ("</body>");
          client.println("</html>");
          break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        }
        else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    Serial.println("client disconnected");
  }
}

