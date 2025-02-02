import random
import time
import json
import logging
import paho.mqtt.client as mqtt
import os
from numpy import cos, pi

logger = logging.getLogger(__name__)


# MQTT publisher setup
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
publisher_client = mqtt.Client()

# Shared state (in‑memory configuration for simulators)
# holds configuration for each room: { room_name: { sensor_name: [min, max], ... } }
global_config = {}
active_simulators = set()    # set of room names that have an active simulator
simulator_threads = {}       # mapping of room name to thread info


def connect_publisher_mqtt():
    try:
        publisher_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info(f"Publisher connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect publisher to MQTT broker: {e}")
        exit(1)


def run_publisher():
    publisher_client.loop_start()
    

def sigma_3(range):
    """
    Calculate the standard deviation for a range.
    """
    return (range[1] - range[0]) / 6

def mean(range):
    """
    Calculate the mean value of a range.
    """
    return (range[0] + range[1]) / 2

def simulator(room, config_ref, stop_event):
    """
    Simulate sensor values for a given room using configuration from config_ref.
    """
    while not stop_event.is_set():
        current_time = time.localtime()
        hour = current_time.tm_hour
        minutes = current_time.tm_min
        time_float = hour + minutes / 60
        ranges = config_ref['ranges']

        # Example simulation for several sensor names.
        if 'temp' in ranges:
            temp = round(random.gauss(
                mean(ranges['temp']), sigma_3(ranges['temp'])), 2)
            temp += -1.5 * cos((time_float - 1) / 12 * pi)
            
        if 'hum' in ranges:
            hum = round(random.gauss(
                mean(ranges['hum']), sigma_3(ranges['hum'])), 2)
            hum += 3 * cos((time_float - 4) / 12 * pi)

        if 'light' in ranges:
            light = round(random.gauss(
                mean(ranges['light']), sigma_3(ranges['light'])), 2)
            light += -150 * cos((time_float - 1) / 12 * pi)

        if 'co2' in ranges:
            co2 = round(random.gauss(
                mean(ranges['co2']), sigma_3(ranges['co2'])), 2)
            co2 += -50 * cos((time_float - 1) / 12 * pi)

        if 'air_quality_pm2_5' in ranges:
            air_quality_pm2_5 = round(random.gauss(
                mean(ranges['air_quality_pm2_5']), sigma_3(ranges['air_quality_pm2_5'])), 2)
            
        if 'air_quality_pm10' in ranges:
            air_quality_pm10 = round(random.gauss(
                mean(ranges['air_quality_pm10']), sigma_3(ranges['air_quality_pm10'])), 2)
            
        if 'sound' in ranges:
            sound = round(random.gauss(
                mean(ranges['sound']), sigma_3(ranges['sound'])), 2)
            sound += -10 * cos((time_float - 1) / 12 * pi)

        if 'voc' in ranges:
            voc = round(random.gauss(
                (ranges['voc'][0] + ranges['voc'][1]) / 2, 5), 2)

        # Generate timestamp (ISO 8601)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Publish sensor data to MQTT topics.
        try:
            if 'temp' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/temp", json.dumps({"value": temp, "timestamp": timestamp}))
            if 'hum' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/humidity", json.dumps({"value": hum, "timestamp": timestamp}))
            if 'light' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/light", json.dumps({"value": light, "timestamp": timestamp}))
            if 'co2' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/co2", json.dumps({"value": co2, "timestamp": timestamp}))
            if 'air_quality_pm2_5' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/air_quality_pm2_5", json.dumps({"value": air_quality_pm2_5, "timestamp": timestamp}))
            if 'air_quality_pm10' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/air_quality_pm10", json.dumps({"value": air_quality_pm10, "timestamp": timestamp}))
            if 'sound' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/sound", json.dumps({"value": sound, "timestamp": timestamp}))
            if 'voc' in ranges:
                publisher_client.publish(
                    f"{room}/sensors/voc", json.dumps({"value": voc, "timestamp": timestamp}))

            logger.info(f"Simulated data for {room} at {timestamp}")
        except Exception as e:
            logger.error(f"Failed to publish simulated data for {room}: {e}")

        time.sleep(10)
