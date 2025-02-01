import streamlit as st
import pandas as pd
import paho.mqtt.client as mqtt
import json
import os
import logging
import threading
import time
import random
import re

# Import shared state from the separate module.
from global_config import global_config, active_simulators, simulator_threads

# mqtt setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))

publisher_client = mqtt.Client()

def connect_publisher_mqtt():
    """Connect the publisher MQTT client to the broker."""
    try:
        publisher_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info(f"Publisher connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect publisher to MQTT broker: {e}")
        st.error("Failed to connect publisher to MQTT broker.")

def run_publisher():
    publisher_client.loop_start()

# Start the MQTT loop in a background thread.
publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()



def simulator(room, config_ref, stop_event):
    """
    Simulate sensor data for a given room using the provided configuration (ranges)
    until stop_event is set.
    
    :param room: The room identifier.
    :param config_ref: A reference to the global configuration dictionary.
    :param stop_event: A threading.Event object to signal the simulator to stop.
    """
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
        hum += 5 if hour in range(22, 7) else -3

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


# Run the initialization only once per process.
if not globals().get("global_initialized", False):
    connect_publisher_mqtt()
    config_file_path = os.getenv('SIMULATOR_CONFIG_FILE', 'config.json')
    rooms_config = load_config_from_file(config_file_path)
    initialize_simulators_from_config(rooms_config)
    print(global_config)
    global_initialized = True

# Streamlit UI
st.title("Arduino Simulators Dashboard")
st.sidebar.header("Manage Simulators")


# Adding a new simulator
with st.sidebar.expander("Add Simulator"):
    add_room = st.text_input("Room Identifier", "")
    if st.button("Add Simulator"):
        if add_room:
            if not re.match("^[A-Za-z0-9_-]+$", add_room):
                st.error(
                    "Invalid room identifier. Use only letters, numbers, underscores, or hyphens.")
            elif add_room in active_simulators:
                st.warning(f"Simulator for {add_room} is already active.")
            else:
                # Define default ranges for a new simulator.
                default_ranges = {
                    'temp': [20, 26],
                    'hum': [30, 60],
                    'light': [500, 800],
                    'co2': [350, 500],
                    'air_quality_pm2_5': [10, 25],
                    'air_quality_pm10': [10, 50],
                    'sound': [25, 35],
                    'voc': [50, 400]
                }
                # Add the new room's configuration globally.
                global_config[add_room] = default_ranges.copy()
                simulator_threads[add_room] = {
                    'ranges': default_ranges.copy(),
                    'stop_event': threading.Event()
                }
                stop_event = simulator_threads[add_room]['stop_event']
                thread = threading.Thread(target=simulator, args=(
                    add_room, simulator_threads[add_room], stop_event), daemon=True)
                thread.start()
                simulator_threads[add_room]['thread'] = thread
                active_simulators.add(add_room)
                st.success(f"Added simulator for {add_room}")
        else:
            st.error("Room identifier cannot be empty.")

# Removing a simulator
with st.sidebar.expander("Remove Simulator"):
    if active_simulators:
        remove_room = st.selectbox(
            "Select Room to Remove", sorted(list(active_simulators)))
        if st.button("Remove Simulator"):
            if remove_room in simulator_threads:
                simulator_threads[remove_room]['stop_event'].set()
                simulator_threads[remove_room]['thread'].join(timeout=2)
                del simulator_threads[remove_room]
            active_simulators.discard(remove_room)
            if remove_room in global_config:
                del global_config[remove_room]
            st.success(f"Removed simulator for {remove_room}")
    else:
        st.write("No simulators to remove.")



# Updating ranges of simulator
with st.sidebar.expander("Update Simulator"):
    if active_simulators:
        update_room = st.selectbox(
            "Select Room to Update", sorted(list(active_simulators)))
        if update_room:
            # Get the current configuration from the shared global_config.
            current_ranges = global_config.get(update_room, {})
            st.write(f"Updating parameters for {update_room}:")
            temp_range = current_ranges.get('temp', [20, 30])
            hum_range = current_ranges.get('hum', [30, 60])
            light_range = current_ranges.get('light', [300, 800])
            co2_range = current_ranges.get('co2', [350, 500])
            air_pm2_5_range = current_ranges.get('air_quality_pm2_5', [10, 25])
            air_pm10_range = current_ranges.get('air_quality_pm10', [10, 50])
            sound_range = current_ranges.get('sound', [30, 80])
            voc_range = current_ranges.get('voc', [50, 400])

            temp_min, temp_max = st.slider("Temperature Range (°C):", 0.0, 50.0,
                                           (float(temp_range[0]), float(temp_range[1])), 0.1)
            hum_min, hum_max = st.slider("Humidity Range (%):", 0.0, 100.0,
                                         (float(hum_range[0]), float(hum_range[1])), 0.1)
            light_min, light_max = st.slider("Light Range (lux):", 0.0, 2000.0,
                                             (float(light_range[0]), float(light_range[1])), 1.0)
            co2_min, co2_max = st.slider("CO2 Range (ppm):", 300.0, 2000.0,
                                         (float(co2_range[0]), float(co2_range[1])), 1.0)
            air_pm2_5_min, air_pm2_5_max = st.slider("Air Quality Range, pm2.5 (μg/m³):", 0.0, 200.0,
                                                     (float(air_pm2_5_range[0]), float(air_pm2_5_range[1])), 0.1)
            air_pm10_min, air_pm10_max = st.slider("Air Quality Range, pm10 (μg/m³):", 0.0, 200.0,
                                                   (float(air_pm10_range[0]), float(air_pm10_range[1])), 0.1)
            sound_min, sound_max = st.slider("Sound Range (dB):", 0.0, 120.0,
                                             (float(sound_range[0]), float(sound_range[1])), 1.0)
            voc_min, voc_max = st.slider("VOC Range (μg/m³):", 0.0, 500.0,
                                         (float(voc_range[0]), float(voc_range[1])), 1.0)

            if st.button("Update Simulator"):
                new_ranges = {
                    'temp': [temp_min, temp_max],
                    'hum': [hum_min, hum_max],
                    'light': [light_min, light_max],
                    'co2': [co2_min, co2_max],
                    'air_quality_pm2_5': [air_pm2_5_min, air_pm2_5_max],
                    'air_quality_pm10': [air_pm10_min, air_pm10_max],
                    'sound': [sound_min, sound_max],
                    'voc': [voc_min, voc_max]
                }
                # Update the shared global_config
                global_config[update_room] = new_ranges.copy()
                # Also update the configuration used by the simulator thread
                if update_room in simulator_threads:
                    simulator_threads[update_room]['ranges'] = new_ranges.copy()
                st.success(f"Updated ranges for {update_room}")
    else:
        st.write("No simulators to update.")

# Display ranges of active simulatorsdjj
st.header("Active Simulators")
if active_simulators:
    for room in sorted(active_simulators):
        with st.expander(f"Room: {room}"):
            ranges = global_config.get(room, {})
            if ranges:
                df = pd.DataFrame.from_dict(
                    ranges, orient='index', columns=["Min", "Max"])
                st.write("**Parameter Ranges:**")
                st.table(df.style.format(precision=1))
            else:
                st.write("No range information available.")
else:
    st.write("No active simulators.")
