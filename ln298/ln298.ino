#include <ArduinoBLE.h>

#define dirA 7
#define dirB 8
#define soil A7

const int ledPin = LED_BUILTIN; // pin to use for the LED

// Soil service and characteristics
BLEService soilService("2d3fc060-0dcc-11ec-82a8-0242ac130003");
BLEByteCharacteristic switchPumpCharacteristic("cbbb4e46-0dcf-11ec-82a8-0242ac130003", BLERead | BLEWrite);
BLEByteCharacteristic soilCharacteristic("ba8cf798-0de1-11ec-82a8-0242ac130003", BLERead);

void setup() {
  Serial.begin(9600);
  // while (!Serial); // Debug only!

  Serial.println("Initializing logic...");
  pinMode(dirA, OUTPUT);
  pinMode(dirB, OUTPUT);
  pinMode(soil, INPUT);
  pinMode(ledPin, OUTPUT);

  initializeBLE();
}

void initializeBLE() {
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // set advertised local name and service UUID:
  Serial.println("Setting up services...");
  BLE.setDeviceName("Dusty Dirt Sensor");
  BLE.setLocalName("Dusty Dirt Sensor");
  BLE.setAdvertisedService(soilService);

  // add the characteristic to the service
  soilService.addCharacteristic(switchPumpCharacteristic);
  soilService.addCharacteristic(soilCharacteristic);

  // add service
  BLE.addService(soilService);

  // set the initial value for the characeristic:
  switchPumpCharacteristic.writeValue(0);
  switchPumpCharacteristic.setEventHandler(BLEWritten, switchPumpCharacteristicHandler);

  // start advertising
  BLE.advertise();

  Serial.println("Advertising BLE from local address " + BLE.address() + "...");
}

void turnLEDOn() {
  digitalWrite(ledPin, HIGH);
}

void turnLEDOff() {
  digitalWrite(ledPin, LOW); 
}

void switchPumpCharacteristicHandler(BLEDevice central, BLECharacteristic characteristic) {
  if (switchPumpCharacteristic.value()) { 
    turnOnPump();
   } else {
    turnOffPump();
   }
}

void turnOnPump() {
  Serial.println("turning on pump");
  switchPumpCharacteristic.writeValue(1);

  turnLEDOn();
  digitalWrite(dirA, LOW);
  digitalWrite(dirB, HIGH);

  delay(5000);

  turnOffPump(); // always turn off for safety
}

void turnOffPump() {
  Serial.println("turning off pump");
  digitalWrite(dirA,LOW);
  digitalWrite(dirB,LOW); 
  turnLEDOff();
  switchPumpCharacteristic.writeValue(0);
}

void checkSoil() {
   int moisture;
   moisture = analogRead(soil);
   soilCharacteristic.writeValue(moisture);
   Serial.print("Moisture Level: ");
   Serial.println(moisture);
}

void loop() {
  // listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {
      checkSoil();
    }

    // when the central disconnects, print it out:
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}
