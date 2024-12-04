import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
import os
import json

# Environment configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_BUCKET = "mybucket"
INFLUXDB_ORG = "myorg"
INFLUXDB_TOKEN = "admin123"

# Set up InfluxDB client
client = InfluxDBClient(url=f"http://{INFLUXDB_HOST}:8086", token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=WritePrecision.NS)

# Function to handle writing static room facilities data to InfluxDB
def write_static_room_data(room_data):
    for room in room_data.get('rooms', []):
        point = Point("room_facilities") \
            .tag("room_name", room.get("name")) \
            .field("videoprojector", room["facilities"].get("videoprojector", False)) \
            .field("seating_capacity", room["facilities"].get("seating_capacity", 0))

        # Add optional facilities if they are present
        if "computers" in room["facilities"]:
            point.field("computers", room["facilities"]["computers"])
        if "robots_for_training" in room["facilities"]:
            point.field("robots_for_training", room["facilities"]["robots_for_training"])

        # Write point to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Load and write static data to InfluxDB
if __name__ == "__main__":
    try:
        # Load static room facilities data from JSON
        with open("room_facilities_data.json", "r") as f:
            room_facilities_data = json.load(f)
            write_static_room_data(room_facilities_data)
    except Exception as e:
        print(f"Error writing static room data: {e}")

# Functions to handle writing sensor data to InfluxDB for each type
def write_air_quality_data(data):
    for value in data.get('air_quality_values', []):
        point = Point("air_quality") \
            .field("PM2.5", value.get("PM2.5")) \
            .field("PM10", value.get("PM10")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_co2_data(data):
    for value in data.get('co2_values', []):
        point = Point("co2") \
            .field("co2_level", value.get("co2_level")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_humidity_data(data):
    for value in data.get('humidity_values', []):
        point = Point("humidity") \
            .field("humidity", value.get("humidity")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_light_intensity_data(data):
    for value in data.get('light_intensity_values', []):
        point = Point("light_intensity") \
            .field("light_intensity", value.get("light_intensity")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_sound_data(data):
    for value in data.get('sound_values', []):
        point = Point("sound") \
            .field("sound_level", value.get("sound_level")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_temperature_data(data):
    for value in data.get('temperature_values', []):
        point = Point("temperature") \
            .field("temperature", value.get("temperature")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

def write_voc_data(data):
    for value in data.get('voc_values', []):
        point = Point("voc") \
            .field("VOC_level", value.get("VOC_level")) \
            .time(value.get("timestamp"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# Callback when MQTT receives a message
def on_message(client, userdata, message):
    try:
        # Decode message payload
        payload = message.payload.decode()
        data = json.loads(payload)

        # Parse the topic and write data accordingly
        topic = message.topic
        if topic == "sensor/air_quality":
            write_air_quality_data(data)
        elif topic == "sensor/co2":
            write_co2_data(data)
        elif topic == "sensor/humidity":
            write_humidity_data(data)
        elif topic == "sensor/light_intensity":
            write_light_intensity_data(data)
        elif topic == "sensor/sound":
            write_sound_data(data)
        elif topic == "sensor/temperature":
            write_temperature_data(data)
        elif topic == "sensor/voc":
            write_voc_data(data)

    except Exception as e:
        print(f"Error processing message: {e}")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER)

# Subscribe to relevant topics
topics = [
    ("sensor/air_quality", 0),
    ("sensor/co2", 0),
    ("sensor/humidity", 0),
    ("sensor/light_intensity", 0),
    ("sensor/sound", 0),
    ("sensor/temperature", 0),
    ("sensor/voc", 0)
]
mqtt_client.subscribe(topics)

mqtt_client.on_message = on_message

# Start loop to keep listening for MQTT messages
mqtt_client.loop_forever()
