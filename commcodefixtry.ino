#include <WiFiNINA.h> // Include the WiFiNINA library for Wi-Fi functionality
#include <WiFiUdp.h>  // Include the WiFiUdp library for UDP communication

// WiFi Credentials
const char* ssid = "DESKTOP-770LUMN 7689";
const char* password = "71Z&622h";

// UDP settings
WiFiUDP udp;
const char* remoteIP = "192.168.137.163";  
const int remotePort = 8888;

// Sensor pins
const int sensorPinA = A0;        // Analog pin connected to Plant A's moisture sensor
const int sensorPinB = A1;        // Analog pin connected to Plant B's moisture sensor

// Function to connect to Wi-Fi network
void connectToWiFi() {
  Serial.print("Connecting to Wi-Fi...");
  
  // Keep trying to connect until successful
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);   // Attempt to connect
    delay(1000);                 // Wait 1 second between attempts
    Serial.print(".");           // Print progress indicator
  }
  
  // Connection successful
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(9600); // Initialize Serial Monitor for debugging

  // Initial attempt to connect to Wi-Fi
  connectToWiFi();

  // Start the UDP service, specifying a local port for responses (optional)
  udp.begin(8889); // Local port to listen for responses
}

void loop() {
  // Reconnect to Wi-Fi if the connection is lost
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi lost. Attempting to reconnect...");
    connectToWiFi(); // Call the function to re-establish the connection
  }

  // Read soil moisture levels
  int moistureA = analogRead(sensorPinA); // Read moisture value for Plant A
  int moistureB = analogRead(sensorPinB); // Read moisture value for Plant B

  // Create a string with both moisture readings, separated by a comma
  String message = String(moistureA) + "," + String(moistureB);

  // Send the message to the Raspberry Pi via UDP
  udp.beginPacket(remoteIP, remotePort); // Begin a UDP packet to the specified IP and port
  udp.write(message.c_str());           // Write the message to the UDP packet
  udp.endPacket();                      // Send the UDP packet

  // Print the sent message to the Serial Monitor for debugging
  Serial.println("Data sent: " + message);

  // Wait 2.5 seconds before sending the next reading 
  delay(2500);
}
