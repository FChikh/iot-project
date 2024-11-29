import serial
import paho.mqtt.client as mqtt
import json
import os

import socket

# Serial port settings
serial_port = os.environ.get(
    'SERIAL_PORT', '/dev/cu.usbmodem2101')  # Update as needed
baud_rate = 9600

# MQTT broker settings
mqtt_broker = os.environ.get(
    'MQTT_BROKER', '127.0.0.1')  # Update as needed
mqtt_port = 1883
temp_topic = "room/temp"
light_topic = "room/light"
print(f"Connecting to MQTT broker: {mqtt_broker}")

# Connect to the serial port
ser = serial.Serial(serial_port, baud_rate)

# Connect to the MQTT broker
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)

try:
    while True:
        # Read data from serial
        line = ser.readline().decode('utf-8').strip()
        print(f"Received: {line}")

        # Parse the JSON data
        try:
            data = json.loads(line)
            temp = data['temp']
            light = data['light']

            # Publish to MQTT topics
            client.publish(temp_topic, temp)
            client.publish(light_topic, light)
            print(f"Published: Temp={temp}, Light={light}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except KeyError as e:
            print(f"Missing key in data: {e}")

except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
    client.disconnect()
