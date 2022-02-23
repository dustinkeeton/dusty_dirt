/*
 *  This sketch sends a message to a TCP server
 *
 */

#include <WiFi.h>
#include <WiFiMulti.h>
#include <ArduinoMqttClient.h>

#include "secrets.h"

WiFiClient client;
WiFiMulti WiFiMultiSomething;
MqttClient mqttClient(client);

// HA
char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;
char clientIP[] = SECRET_CLIENT_IP;

// MQTT
uint16_t port = 1883;
char username[] = SECRET_USERNAME;
char mqttPassword[] = SECRET_PASSWORD;
// char broker[] = "soil";
char topic[] = "sensor/soil";

// other nonsense
const long interval = 1000;
unsigned long previousMillis = 0;
int count = 0;

void setup()
{
  Serial.begin(9600);
  // while (!Serial); // Debug only!
  Serial.println("starting");
  // We start by connecting to a WiFi network
  WiFiMultiSomething.addAP(SECRET_SSID, SECRET_PASS);
  Serial.println();
  Serial.println();
  Serial.print("Waiting for WiFi... ");
  while(WiFiMultiSomething.run() != WL_CONNECTED) {
      Serial.print(".");
      delay(500);
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  delay(500);

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(SECRET_CLIENT_IP);

  mqttClient.setUsernamePassword(SECRET_USERNAME, SECRET_PASSWORD);
  if (!mqttClient.connect(SECRET_CLIENT_IP, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1);
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}


void loop()
{
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  mqttClient.poll();

  // to avoid having delays in loop, we'll use the strategy from BlinkWithoutDelay
  // see: File -> Examples -> 02.Digital -> BlinkWithoutDelay for more info
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousMillis >= interval) {
    // save the last time a message was sent
    previousMillis = currentMillis;
    int val = 42;
    Serial.print("Sending message to topic: ");
    Serial.println(topic);
    Serial.println(val);

    // send message, the Print interface can be used to set the message contents
    mqttClient.beginMessage(topic);
    mqttClient.print(val);
    mqttClient.endMessage();

    Serial.println();

    count++;
  }
}
