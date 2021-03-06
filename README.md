# Dusty Dirt
An Arduino based soil sensor with BLE built for integrating with MQTT servers and Home Assistant.

### Intent
The goal of this project is to create a simple, plug-and-play way to monitor and control the watering of a plant.

### Use cases
Travelling and laziness.

### Tech
Initial assumptions are based on using an arduino with BLE capabilities (such as the Nano 33 IOT). This may change over time and WiFi might be included due to ease of use and range issues of Bluetooth. The goal is to keep cost per plant low so smaller chips such as the ESP32 might be incorporated, but battery life is a concern.

Currently the codebase assumes a lot about a Home Assistant setup. `dusty_dirt.py` is to be run on an intermediary device (like a raspi) that then sends mqtt messages to Home Assistant. This limits its flexibility.

### Power Consumption
~5v 
0.08 amps standby
0.18 amps while pump on


### Arduino Nano 33 IOT
board: Arduino NANO 33 IoT
programmer: arduino:sam_ice

### ESP32-S
board: Node32s

### Getting Started
TBD

### Config
config format is `config.yaml` at project root as follows:
```
username: <username_for_mqqt_broker>
password: <password_for_mqqt_broker>
client_ip: <ip_of_mqqt_broker>
client_port: <port_of_mqqt_broker>
client_keep_alive: 60 # adjust to your liking
moisture_threshold: 100 # adjust to your liking
automate_watering: Yes # controls watering based on moisture_threshold
```

### Secrets
`secrets.h` file is used to define secrets for use in `ino` files. 
```
// WiFi
#define SECRET_SSID ""
#define SECRET_PASS ""

// MQQT
#define SECRET_CLIENT_IP ""
#define SECRET_USERNAME ""
#define SECRET_PASSWORD ""
```


