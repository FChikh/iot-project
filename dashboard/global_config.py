# global_config.py
import os
import json
import logging
import threading
import time
import random
import re

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

# Import SQLAlchemy session and models.
from db import SessionLocal
# Equipment remains available if needed
from models import Room, Sensor, Equipment

# --------------------------
# Global state and MQTT setup
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared state (in‑memory configuration for simulators)
# holds configuration for each room: { room_name: { sensor_name: [min, max], ... } }
global_config = {}
active_simulators = set()    # set of room names that have an active simulator
simulator_threads = {}       # mapping of room name to thread info

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

# --------------------------
# Simulator function
# --------------------------


def simulator(room, config_ref, stop_event):
    """
    Simulate sensor values for a given room using configuration from config_ref.
    """
    while not stop_event.is_set():
        current_time = time.localtime()
        hour = current_time.tm_hour
        ranges = config_ref['ranges']

        # Example simulation for several sensor names.
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

# --------------------------
# Database-backed configuration functions
# --------------------------


def load_config_from_db():
    """
    Query the database for rooms and their sensor configurations.
    Returns a list of dictionaries with keys: "name" and "sensors".
    The "sensors" value is a dict mapping sensor name to [min, max].
    """
    db_session = SessionLocal()
    config_list = []
    try:
        rooms = db_session.query(Room).all()
        for room in rooms:
            sensor_ranges = {}
            sensors = db_session.query(Sensor).filter(
                Sensor.room_id == room.id).all()
            for sensor in sensors:
                sensor_ranges[sensor.name] = [
                    sensor.min_value, sensor.max_value]
            config_list.append({"name": room.name, "sensors": sensor_ranges})
        logger.info("Loaded configuration from database.")
        return config_list
    except Exception as e:
        logger.error(f"Failed to load configuration from DB: {e}")
        return []
    finally:
        db_session.close()


def initialize_simulators_from_config(rooms):
    """
    For each room configuration from the DB, update the global config and
    initialize a simulator thread if not already running.
    """
    for room_config in rooms:
        room_name = room_config["name"]
        # Already a dict: { sensor_name: [min, max], ... }
        sensor_ranges = room_config["sensors"]
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

# --------------------------
# Helper functions for simulator management (with DB updates)
# --------------------------


def add_simulator(room, sensor_ranges):
    """
    Add a simulator for the given room by:
      1. Inserting a new Room and corresponding Sensor rows into the DB.
      2. Updating the in-memory global_config and starting a simulator thread.
    """
    if room in active_simulators:
        return False, "Simulator already active."

    # Update in-memory configuration.
    global_config[room] = sensor_ranges.copy()

    # Insert into the DB.
    db_session = SessionLocal()
    try:
        # Check if the room already exists.
        existing_room = db_session.query(
            Room).filter(Room.name == room).first()
        if existing_room:
            return False, f"Room {room} already exists in DB."
        new_room = Room(name=room)
        db_session.add(new_room)
        db_session.flush()  # Get new_room.id

        # Add sensor configuration rows.
        for sensor_name, range_vals in sensor_ranges.items():
            new_sensor = Sensor(room_id=new_room.id, name=sensor_name,
                                min_value=range_vals[0], max_value=range_vals[1])
            db_session.add(new_sensor)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error adding simulator for {room}: {e}")
        return False, f"DB error adding simulator: {e}"
    finally:
        db_session.close()

    # Start simulator thread.
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


def update_simulator(room, new_ranges):
    """
    Update the simulator configuration both in memory and in the DB.
    """
    if room not in active_simulators:
        return False, "Simulator not active."

    global_config[room] = new_ranges.copy()
    if room in simulator_threads:
        simulator_threads[room]['ranges'] = new_ranges.copy()

    # Update the DB.
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if not room_record:
            return False, f"Room {room} not found in DB."
        # For each sensor in new_ranges, update if exists; otherwise, add it.
        for sensor_name, range_vals in new_ranges.items():
            sensor_record = db_session.query(Sensor).filter(
                Sensor.room_id == room_record.id,
                Sensor.name == sensor_name
            ).first()
            if sensor_record:
                sensor_record.min_value = range_vals[0]
                sensor_record.max_value = range_vals[1]
            else:
                new_sensor = Sensor(room_id=room_record.id, name=sensor_name,
                                    min_value=range_vals[0], max_value=range_vals[1])
                db_session.add(new_sensor)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error updating simulator for {room}: {e}")
        return False, f"DB error updating simulator: {e}"
    finally:
        db_session.close()

    logger.info(f"Simulator for {room} updated.")
    return True, f"Simulator for {room} updated."


def remove_simulator(room):
    """
    Remove the simulator from memory and delete the corresponding Room (and cascade delete Sensors) from the DB.
    """
    if room not in active_simulators:
        return False, "Simulator not active."

    if room in simulator_threads:
        simulator_threads[room]['stop_event'].set()
        simulator_threads[room]['thread'].join(timeout=2)
        del simulator_threads[room]
    active_simulators.discard(room)
    if room in global_config:
        del global_config[room]

    # Remove from the DB.
    db_session = SessionLocal()
    try:
        room_record = db_session.query(Room).filter(Room.name == room).first()
        if room_record:
            db_session.delete(room_record)
            db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"DB error removing simulator for {room}: {e}")
        return False, f"DB error removing simulator: {e}"
    finally:
        db_session.close()

    logger.info(f"Simulator for {room} removed.")
    return True, f"Simulator for {room} removed."


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
    # Run the Flask app on port 9999 (adjust host/port as needed)
    app.run(host="0.0.0.0", port=9999)


# --------------------------
# Main execution
# --------------------------
connect_publisher_mqtt()
publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()

# Load configuration from the database and initialize simulators.
rooms_config = load_config_from_db()
initialize_simulators_from_config(rooms_config)

if __name__ == "__main__":
    # Start the Flask API server (blocking call)
    run_api()
