import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import json

# Environment configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot_data")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot_project")
INFLUXDB_USERNAME = os.getenv("INFLUXDB_USERNAME", "admin")
INFLUXDB_PASSWORD = os.getenv("INFLUXDB_PASSWORD", "admin123")

# Set up InfluxDB client
client = InfluxDBClient(
    url=f"http://{INFLUXDB_HOST}:8086", username=INFLUXDB_USERNAME, password=INFLUXDB_PASSWORD, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_sensor_data(sensor_type, room, value, timestamp):
    """
    Write sensor data to InfluxDB.
    :param sensor_type: The type of sensor (e.g., temp, light, etc.)
    :param room: The room where the sensor is located
    :param value: The sensor value
    :param timestamp: The timestamp for the reading
    """
    try:
        point = Point("room_data") \
            .tag("room_id", room) \
            .field(sensor_type, value) \
            .time(timestamp, WritePrecision.NS)
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Written {sensor_type} data for room {room}: {value} at {timestamp}")
    except Exception as e:
        print(f"Error writing {sensor_type} data to InfluxDB: {e}")

def on_message(client, userdata, message):
    """
    Handle incoming MQTT messages and route them to the appropriate InfluxDB function.
    """
    try:
        # Decode the message payload
        payload = message.payload.decode()
        data = json.loads(payload)

        # Extract room, sensor type, value, and timestamp
        print(f"Received message: {data}")
        print(f"Topic: {message.topic}")
        print(f"time: {message.timestamp}")
        topic = message.topic
        room, sensors, sensor_type = topic.split("/")
        value = data.get("value")
        timestamp = data.get("timestamp")

        if value is not None and timestamp is not None:
            write_sensor_data(sensor_type, room, value, timestamp)
        else:
            print(f"Incomplete data received: {data}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")


# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER)


# Subscribe to topics for each sensor type
mqtt_client.subscribe("+/sensors/#")

mqtt_client.on_message = on_message

# Start loop to keep listening for MQTT messages
print("Listening for MQTT messages...")
mqtt_client.loop_forever()
