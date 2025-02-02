# global_config.py
import os
import json
import logging
import threading
import time
import random
import re

from flask import Flask, request, jsonify
from simulator import simulator, connect_publisher_mqtt, run_publisher
from simulator import global_config, active_simulators, simulator_threads

from db import add_equipment_for_room, update_equipment_for_room, remove_equipment_for_room, get_equipment_for_room, get_rooms
from db import add_simulator, update_simulator, remove_simulator


# Import SQLAlchemy session and models.
from db import SessionLocal
# Equipment remains available if needed
from models import Room, Sensor, Equipment

# --------------------------
# Global state and MQTT setup
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


default_equipment = [
    {
        "name": "blackboard",
        "value": True,
        "type": "boolean"
    },
    {
        "name": "capacity",
        "value": 30,
        "type": "integer"
    },
    {
        "name": "computer_class",
        "value": True,
        "type": "boolean"
    },
    {
        "name": "microphone",
        "value": True,
        "type": "boolean"
    },
    {
        "name": "projector",
        "value": True,
        "type": "boolean"
    },
    {
        "name": "smart_board_webex",
        "value": True,
        "type": "boolean"
    },
    {
        "name": "whiteboard",
        "value": True,
        "type": "boolean"
    }
]

default_ranges = {
    "temp": [20, 30],
    "hum": [30, 60],
    "light": [300, 800],
    "co2": [350, 500],
    "air_quality_pm2_5": [10, 25],
    "air_quality_pm10": [10, 50],
    "sound": [30, 80],
    "voc": [50, 400]
}

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


# REST API Endpoints
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
    sensor_ranges = default_ranges
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

@app.route("/rooms", methods=["GET"])
def list_rooms():
    try:
        equipment_data = get_rooms()
        if equipment_data is None:
            return jsonify({"error": f"Rooms not found."}), 404
        return jsonify(equipment_data), 200
    except Exception as e:
        # Log error already done in helper; return error message.
        return jsonify({"error": str(e)}), 500


@app.route("/equipment/<room>", methods=["GET"])
def get_equipment_route(room):
    """
    API endpoint to retrieve the equipment list for a given room.
    Delegates the DB retrieval to `retrieve_equipment_for_room` and builds a JSON response.
    """
    try:
        equipment_data = get_equipment_for_room(room)
        if equipment_data is None:
            # Room not found.
            return jsonify({"error": f"Room '{room}' not found."}), 404
        return jsonify(equipment_data), 200
    except Exception as e:
        # Log error already done in helper; return error message.
        return jsonify({"error": str(e)}), 500


@app.route("/equipment/", methods=["POST"])
def create_equipment_route():
    """
    Create equipment records for the given room.
    Expects a JSON payload of the form:
    
    {
      "equipment": [
          {
             "name": "blackboard",
             "value": true,
             "type": "boolean"
          },
          {
             "name": "capacity",
             "value": 30,
             "type": "integer"
          },
          ...
      ]
    }
    """
    data = request.get_json()
    room = data.get("room")
    eq_list = default_equipment
    if not eq_list or not isinstance(eq_list, list):
        return jsonify({"error": "Missing or invalid 'equipment' list in request."}), 400

    success, message = add_equipment_for_room(room, eq_list)
    status = 200 if success else 400
    return jsonify({"message": message}), status


@app.route("/equipment/<room>", methods=["PUT"])
def update_equipment_route(room):
    """
    Update the equipment records for the given room.
    Expects a JSON payload of the form:
    
    {
      "equipment": [
          {
             "name": "blackboard",
             "value": true,
             "type": "boolean"
          },
          {
             "name": "capacity",
             "value": 30,
             "type": "integer"
          },
          ...
      ]
    }
    For each equipment entry, if a record exists it will be updated;
    if not, a new record will be created.
    """
    data = request.get_json()
    eq_list = data.get("equipment")
    if not eq_list:
        return jsonify({"error": "Missing 'equipment' list in request."}), 400

    success, message = update_equipment_for_room(room, eq_list)
    status = 200 if success else 400
    return jsonify({"message": message}), status


@app.route("/equipment/<room>", methods=["DELETE"])
def delete_equipment_route(room):
    """
    Delete all equipment records for the given room.
    """
    success, message = remove_equipment_for_room(room)
    status = 200 if success else 400
    if status == 200:
        response = {"message": message}
    else:
        response = {"error": message}
    return jsonify(response), status



def run_api():
    # Run the Flask app on port 9999 (adjust host/port as needed)
    app.run(host="0.0.0.0", port=9999)


# Connect to the MQTT broker and start the publisher thread
connect_publisher_mqtt()
publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()

# Load configuration from the database and initialize simulators.
rooms_config = load_config_from_db()
initialize_simulators_from_config(rooms_config)

if __name__ == "__main__":
    # Start the Flask API server (blocking call)
    run_api()
