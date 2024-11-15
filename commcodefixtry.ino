#include <WiFiNINA.h>
#include <WiFiUdp.h>

// Wi-Fi credentials
const char* ssid = "DESKTOP-770LUMN 7689";
const char* password = "71Z&622h";

// UDP settings
WiFiUDP udp;
const char* remoteIP = "192.168.137.163";  // Replace with Raspberry Pi's IP address
const int remotePort = 8888;

// Sensor pins
const int sensorPinA = A0;
const int sensorPinB = A1;

void setup() {
  Serial.begin(9600);
  
  // Connect to Wi-Fi
  if (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println("Connected to WiFi!");
  }

  // Start UDP
  udp.begin(8889);  // Local port to listen for responses
}

void loop() {
  // Read moisture sensors
  int moistureA = analogRead(sensorPinA);
  int moistureB = analogRead(sensorPinB);

  // Prepare message to send
  String message = String(moistureA) + "," + String(moistureB);

  // Send data to Raspberry Pi
  udp.beginPacket(remoteIP, remotePort);
  udp.write(message.c_str());
  udp.endPacket();

  Serial.println("Data sent: " + message);

  delay(2500); // Send every 5 seconds
}