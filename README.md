# dusty_dirt
An Arduino based soil sensor with BLE built for integrating with MQTT servers and Home Assistant.

### Intent
The goal of this project is to create a simple, plug-and-play way to monitor and control the watering of a plant.

### Use cases
Travelling and laziness.

### Tech
Initial assumptions are based on using an arduino with BLE capabilities (such as the Nano 33 IOT). This may change over time and WiFi might be included due to ease of use and range issues of Bluetooth. The goal is to keep cost per plant low so smaller chips such as the ESP32 might be incorporated, but battery life is a concern.

Currently the codebase assumes a lot about a Home Assistant setup. `dusyt_dirt.py` is to be run on an intermediary device (like a raspi) that then sends mqtt messages to Home Assistant. This limits its flexibility.

### Getting Started
TBD
