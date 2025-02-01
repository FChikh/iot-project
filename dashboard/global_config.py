import os
import json
import logging
import threading
import time
import random
import re

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

# --------------------------
# Global state and MQTT setup
# --------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared state
global_config = {}           # holds configuration for each room
active_simulators = set()    # names of active simulators
simulator_threads = {}       # info for each simulator thread

# MQTT publisher setup
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
publisher_client = mqtt.Client()


def connect_publisher_mqtt():
    try:
        publisher_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info(f"Publisher connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect publisher to MQTT broker: {e}")
        exit(1)


def run_publisher():
    publisher_client.loop_start()
    

def simulator(room, config_ref, stop_event):
    while not stop_event.is_set():
        current_time = time.localtime()
        hour = current_time.tm_hour
        ranges = config_ref['ranges']

        # Simulate sensor values using Gaussian distributions and time-dependent shifts.
        temp = round(random.gauss(
            (ranges['temp'][0] + ranges['temp'][1]) / 2, 2), 2)
        temp += 2 if 7 <= hour <= 19 else -1

        hum = round(random.gauss(
            (ranges['hum'][0] + ranges['hum'][1]) / 2, 5), 2)
        hum += 5 if 0 <= hour < 7 or 22 <= hour <= 23 else -3

        light = round(random.gauss(
            (ranges['light'][0] + ranges['light'][1]) / 2, 100), 2)
        light += 400 if 7 <= hour <= 19 else -300

        co2 = round(random.gauss(
            (ranges['co2'][0] + ranges['co2'][1]) / 2, 20), 2)
        co2 += 50 if 8 <= hour <= 20 else -30

        air_quality_pm2_5 = round(random.gauss(
            (ranges['air_quality_pm2_5'][0] + ranges['air_quality_pm2_5'][1]) / 2, 5), 2)
        air_quality_pm10 = round(random.gauss(
            (ranges['air_quality_pm10'][0] + ranges['air_quality_pm10'][1]) / 2, 5), 2)

        sound = round(random.gauss(
            (ranges['sound'][0] + ranges['sound'][1]) / 2, 5), 2)
        sound += 10 if 7 <= hour <= 22 else -10

        voc = round(random.gauss(
            (ranges['voc'][0] + ranges['voc'][1]) / 2, 5), 2)

        # Generate timestamp (ISO 8601)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Publish sensor data to MQTT topics.
        try:
            publisher_client.publish(
                f"{room}/sensors/temp", json.dumps({"value": temp, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sensors/humidity", json.dumps({"value": hum, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sensors/light", json.dumps({"value": light, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sensors/co2", json.dumps({"value": co2, "timestamp": timestamp}))
            publisher_client.publish(f"{room}/sensors/air_quality_pm2_5", json.dumps(
                {"value": air_quality_pm2_5, "timestamp": timestamp}))
            publisher_client.publish(f"{room}/sensors/air_quality_pm10", json.dumps(
                {"value": air_quality_pm10, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sensors/sound", json.dumps({"value": sound, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sensors/voc", json.dumps({"value": voc, "timestamp": timestamp}))
            logger.info(f"Simulated data for {room} at {timestamp}")
        except Exception as e:
            logger.error(f"Failed to publish simulated data for {room}: {e}")

        time.sleep(10)
    

def load_config_from_file(config_file="config.json"):
    """
    Load room configurations from a JSON file.
    
    :param config_file: The path to the JSON configuration file.
    """
    try:
        with open(config_file, "r") as file:
            config_data = json.load(file)
            logger.info("Configuration loaded successfully.")
            return config_data.get("rooms", [])
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        st.error(f"Failed to load configuration: {e}")
        return []


def initialize_simulators_from_config(rooms):
    """
    For each room in the config, store its sensor ranges in the global configuration and
    initialize a simulator thread if not already running.
    
    :param rooms: A list of room configurations.
    """
    for room_config in rooms:
        room_name = room_config["name"]
        sensor_ranges = {}
        for sensor in room_config["sensors"]:
            sensor_ranges[sensor["name"]] = sensor["range"]

        # Store the configuration in the shared global_config dictionary.
        if room_name not in global_config:
            global_config[room_name] = sensor_ranges.copy()

        if room_name not in simulator_threads:
            simulator_threads[room_name] = {
                'ranges': sensor_ranges.copy(),
                'stop_event': threading.Event()
            }
            stop_event = simulator_threads[room_name]['stop_event']
            thread = threading.Thread(target=simulator, args=(
                room_name, simulator_threads[room_name], stop_event), daemon=True)
            thread.start()
            simulator_threads[room_name]['thread'] = thread
            active_simulators.add(room_name)
            logger.info(f"Simulator for {room_name} initialized.")


connect_publisher_mqtt()
publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()
config_file_path = os.getenv('SIMULATOR_CONFIG_FILE', 'config.json')
rooms_config = load_config_from_file(config_file_path)
initialize_simulators_from_config(rooms_config)

# --------------------------
# Simulator function
# --------------------------




# --------------------------
# Helper functions for simulators
# --------------------------


def add_simulator(room, sensor_ranges):
    if room in active_simulators:
        return False, "Simulator already active."
    # Save configuration
    global_config[room] = sensor_ranges.copy()
    # Create a thread info record
    stop_event = threading.Event()
    simulator_threads[room] = {
        'ranges': sensor_ranges.copy(),
        'stop_event': stop_event
    }
    thread = threading.Thread(target=simulator, args=(
        room, simulator_threads[room], stop_event), daemon=True)
    thread.start()
    simulator_threads[room]['thread'] = thread
    active_simulators.add(room)
    logger.info(f"Simulator for {room} added.")
    return True, f"Simulator for {room} added."


def remove_simulator(room):
    if room not in active_simulators:
        return False, "Simulator not active."
    if room in simulator_threads:
        simulator_threads[room]['stop_event'].set()
        simulator_threads[room]['thread'].join(timeout=2)
        del simulator_threads[room]
    active_simulators.discard(room)
    if room in global_config:
        del global_config[room]
    logger.info(f"Simulator for {room} removed.")
    return True, f"Simulator for {room} removed."


def update_simulator(room, new_ranges):
    if room not in active_simulators:
        return False, "Simulator not active."
    global_config[room] = new_ranges.copy()
    if room in simulator_threads:
        simulator_threads[room]['ranges'] = new_ranges.copy()
    logger.info(f"Simulator for {room} updated.")
    return True, f"Simulator for {room} updated."

# --------------------------
# REST API using Flask
# --------------------------


app = Flask(__name__)


@app.route("/simulators", methods=["GET"])
def list_simulators():
    # Returns list of active simulators and their configurations.
    response = {
        "active_simulators": list(active_simulators),
        "configurations": global_config
    }
    return jsonify(response), 200


@app.route("/simulators", methods=["POST"])
def create_simulator():
    data = request.get_json()
    room = data.get("room")
    sensor_ranges = data.get("ranges")
    if not room or not sensor_ranges:
        return jsonify({"error": "Missing 'room' or 'ranges' in request."}), 400
    success, message = add_simulator(room, sensor_ranges)
    status = 200 if success else 400
    return jsonify({"message": message}), status


@app.route("/simulators/<room>", methods=["PUT"])
def update_simulator_route(room):
    data = request.get_json()
    new_ranges = data.get("ranges")
    if not new_ranges:
        return jsonify({"error": "Missing 'ranges' in request."}), 400
    success, message = update_simulator(room, new_ranges)
    status = 200 if success else 400
    if status == 200:
        response = {
            "active_simulators": list(active_simulators),
            "configurations": global_config
        }
        return jsonify(response), status
    return jsonify({"message": message}), status


@app.route("/simulators/<room>", methods=["DELETE"])
def delete_simulator(room):
    success, message = remove_simulator(room)
    status = 200 if success else 400
    if status == 200:
        response = {
            "active_simulators": list(active_simulators),
            "configurations": global_config
        }
        return jsonify(response), status
    return jsonify({"message": message}), status


def run_api():
    # Run the Flask app on port 5000 (adjust host/port as needed)
    app.run(host="0.0.0.0", port=9999)


if __name__ == "__main__":
    # Start the Flask API server (blocking call)
    run_api()
