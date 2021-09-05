#! /usr/bin/python3
import time
import yaml
from bluepy.btle import Peripheral, Scanner, DefaultDelegate
import paho.mqtt.client as mqtt

config = yaml.safe_load(open("config.yaml"))

soilService = "2d3fc060-0dcc-11ec-82a8-0242ac130003"
pumpReadWrite = "cbbb4e46-0dcf-11ec-82a8-0242ac130003"
soilRead = "ba8cf798-0de1-11ec-82a8-0242ac130003"
client = mqtt.Client('soil')

global currentPeripheral

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe('pump/set')

def on_disconnect(client, userdata,rc=0):
    print("Disconnected result code "+str(rc))
    client.loop_stop()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if (msg.payload == b'ON'):
        turnOnPump()


client.on_connect = on_connect
# client.on_disconnect = on_disconnect
client.on_message = on_message
client.username_pw_set(config['username'], config['password'])
client.connect(config['client_ip'], config['client_port'], config['client_keep_alive'])

client.loop_start()

def getPeripheralCharacteristicByUUID(peripheral, uuid):
    return peripheral.getCharacteristics(uuid=uuid).pop()

def turnOnPump():
    print('Turning pump on')
    client.publish('pump', "ON", retain=True)
    on = (1).to_bytes(1, byteorder="big")
    pumpReadReadWriteCharacteristic = getPeripheralCharacteristicByUUID(currentPeripheral, pumpReadWrite)
    pumpReadReadWriteCharacteristic.write(on, withResponse=True)

def automateWatering(moisture):
    print('Determining actions...')
    if (moisture < config['moisture_threshold']):
        print('Turning pump on')
        on = (1).to_bytes(1, byteorder="big")
        pumpReadReadWriteCharacteristic = getPeripheralCharacteristicByUUID(peripheral, pumpReadWrite)
        pumpReadReadWriteCharacteristic.write(on, withResponse=True)
    else:
        print('No actions needed.')

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print ("Discovered device", dev.addr0)
        elif isNewData:
            print ("Received new data from"), dev.addr

# scanner = Scanner().withDelegate(ScanDelegate())
# devices = scanner.scan(10.0)
print('Scanning devices...')
devices = Scanner().scan()

for dev in devices:
    name = str(dev.getValueText(9))
    if name.find('Dusty Dirt Sensor') != -1 and dev.connectable:
        print('Device found!')
        print('Reading moisture values...')
        # connect to peripheral and get service
        peripheral = Peripheral(dev)
        currentPeripheral = peripheral
        service = peripheral.getServiceByUUID(soilService)

        # read soil characteristic and publish to mqtt
        soilReadCharacteristic = getPeripheralCharacteristicByUUID(peripheral, soilRead)
        pumpReadWriteCharacteristic = getPeripheralCharacteristicByUUID(peripheral, pumpReadWrite)

        while True:
            valBytes = soilReadCharacteristic.read()
            moisture = int.from_bytes(valBytes, "big")
            client.publish('sensor/soil', moisture, retain=True)

            poopBytes = pumpReadWriteCharacteristic.read()
            pumpState = int.from_bytes(poopBytes, "big")
            client.publish('pump', "ON" if pumpState else "OFF", retain=True)

            print(name + ' = ' + str(moisture))
            if (config['automate_watering']):
                automateWatering(moisture)
            time.sleep(config['read_interval'])

client.loop_stop()