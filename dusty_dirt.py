#! /usr/bin/python3
import yaml
from bluepy.btle import Peripheral, Scanner, DefaultDelegate
import paho.mqtt.client as mqtt

config = yaml.safe_load(open("config.yaml"))

soilService = "2d3fc060-0dcc-11ec-82a8-0242ac130003"
pumpReadWrite = "cbbb4e46-0dcf-11ec-82a8-0242ac130003"
soilRead = "ba8cf798-0de1-11ec-82a8-0242ac130003"
client = mqtt.Client('soil')

global curPeripheral
global curPumpReadWriteCharacteristic
global curSoilReadCharacteristic

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe('pump/set')

def on_disconnect(client, userdata,rc=0):
    print("Disconnected result code "+str(rc))
    client.loop_stop()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("MQTT received for topic '"+msg.topic+"', with payload of "+str(msg.payload))
    if (msg.payload == b'ON'):
        turnOnPump()
    # TODO: have this fn queue the action on the next connection to the appropriate device


client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.username_pw_set(config['username'], config['password'])
client.connect(config['client_ip'], config['client_port'], config['client_keep_alive'])

client.loop_start()

def getPeripheralCharacteristicByUUID(peripheral, uuid):
    return peripheral.getCharacteristics(uuid=uuid).pop()

def turnOnPump():
    print('Turning pump on')
    on = (1).to_bytes(1, byteorder="big")
    client.publish('pump', payload="ON", retain=True)
    client.loop()
    try:
        curPumpReadWriteCharacteristic.write(on, withResponse=True)
    except:
        print("Error turning on pump")
        client.publish('pump', payload="OFF", retain=True)
        client.loop()

def automateWatering(moisture):
    print('Determining actions...')
    if (moisture < config['moisture_threshold']):
        turnOnPump()
    else:
        print('No actions needed.')

def filterDevice(dev):
    name = str(dev.getValueText(9))
    return name.find('Dusty Dirt Sensor') != -1

# scanner = Scanner().withDelegate(ScanDelegate())
# devices = scanner.scan(10.0)
print('Scanning devices...')
devices = Scanner().scan()

found = list(filter(filterDevice, devices))
print(str(len(found))+' Device(s) found!')

for dev in found:
    if dev.connectable:
        name = str(dev.getValueText(9))
        # connect to peripheral and get service and characteristics
        print('==========================================================================================')
        print('Connecting to '+name+'...')
        peripheral = Peripheral(dev)
        curPeripheral = peripheral
        service = peripheral.getServiceByUUID(soilService)
        soilReadCharacteristic = getPeripheralCharacteristicByUUID(peripheral, soilRead)
        curPumpReadWriteCharacteristic = getPeripheralCharacteristicByUUID(peripheral, pumpReadWrite)
        client.message_callback_add('pump/set', on_message)

        print('Reading values...')
        while True:
           # read soil characteristic and publish to mqtt
            moisture = int.from_bytes(soilReadCharacteristic.read(), "big")
            client.publish('sensor/soil', payload=moisture, retain=True)

            pumpState = int.from_bytes(curPumpReadWriteCharacteristic.read(), "big")
            client.publish('pump', payload="ON" if pumpState else "OFF", retain=True)

            print('moisture: ' + str(moisture))
            if (config['automate_watering']):
                automateWatering(moisture)

client.loop_stop()
