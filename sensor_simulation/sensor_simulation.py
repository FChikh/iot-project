import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import random
import time

# Get configuration from environment variables
url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
token = os.getenv('INFLUXDB_TOKEN')
org = os.getenv('INFLUXDB_ORG', 'myorg')
bucket = os.getenv('INFLUXDB_BUCKET', 'room_sensors')

# Create the client
client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Room IDs
rooms = ["MSA1000", "MSA2000", "MSA3500", "MSA3110"]



def generate_sensor_data(room, current_time):
    """Generate realistic sensor data based on time of day and room usage."""
    hour = current_time.hour

    # Light levels based on time of day
    if 8 <= hour <= 18:  # Daytime
        light = round(random.uniform(300.0, 500.0), 2)
    elif 6 <= hour < 8 or 18 < hour <= 22:  # Early morning or evening
        light = round(random.uniform(150.0, 300.0), 2)
    else:  # Night
        light = round(random.uniform(0.0, 50.0), 2)

    # Temperature variations (cooler in morning, warmer in afternoon)
    if 6 <= hour <= 9:  # Morning
        temperature = round(random.uniform(18.0, 21.0), 2)
    elif 10 <= hour <= 15:  # Afternoon
        temperature = round(random.uniform(22.0, 25.0), 2)
    else:  # Evening and night
        temperature = round(random.uniform(19.0, 22.0), 2)

    # CO2 levels (higher during occupied hours)
    if 8 <= hour <= 18:  # Occupied
        co2 = round(random.uniform(400.0, 800.0), 2)
    else:  # Unoccupied
        co2 = round(random.uniform(300.0, 400.0), 2)

    # Humidity (slight variation throughout the day)
    humidity = round(random.uniform(30.0, 60.0), 2)

    # Return generated values
    return {
        "light": light,
        "temperature": temperature,
        "co2": co2,
        "humidity": humidity
    }

# Continuously send data
while True:
    current_time = datetime.now()
    for room in rooms:
        # Generate sensor values for the room
        sensor_data = generate_sensor_data(room, current_time)

        # Create a point
        point = (
            Point("room_data")
            .tag("room_id", room)
            .field("light", sensor_data["light"])
            .field("temperature", sensor_data["temperature"])
            .field("co2", sensor_data["co2"])
            .field("humidity", sensor_data["humidity"])
            .time(int(current_time.timestamp() * 1e9))
        )

        # Write data to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)

    print(f"Data written to InfluxDB at {current_time}")
    time.sleep(10)

# Close the client (although this will never be reached in this infinite loop)
client.close()
