# dashboard/streamlit_app.py

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))

# Initialize session state
if 'active_simulators' not in st.session_state:
    st.session_state.active_simulators = set()

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = {}

if 'simulator_threads' not in st.session_state:
    st.session_state.simulator_threads = {}
    
    
# MQTT Publisher Client
publisher_client = mqtt.Client()


def connect_publisher_mqtt():
    """Connect the publisher MQTT client to the broker."""
    try:
        publisher_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info(f"Publisher connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect publisher to MQTT broker: {e}")
        st.error("Failed to connect publisher to MQTT broker.")


connect_publisher_mqtt()

def run_publisher():
    publisher_client.loop_start()

publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()


# Simulator function
def simulator(room, ranges_ref, stop_event):
    """Simulate sensor data for a given room with user-adjustable ranges and realistic distribution."""
    while not stop_event.is_set():
        current_time = time.localtime()
        hour = current_time.tm_hour
        ranges = ranges_ref['ranges']

        # Gaussian distribution with time-dependent shifts
        temp = round(random.gauss((ranges['temp'][0] + ranges['temp'][1]) / 2, 2), 2)
        temp += 2 if 7 <= hour <= 19 else -1  # Warmer during the day, cooler at night

        hum = round(random.gauss((ranges['hum'][0] + ranges['hum'][1]) / 2, 5), 2)
        # Higher at night, lower during the day
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
        sound += 10 if hour in range(7, 22) else -10

        voc = round(random.gauss(
            (ranges['voc'][0] + ranges['voc'][1]) / 2, 5), 2)

        # Generate ISO 8601 timestamp
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Publish to MQTT topics with timestamp
        try:
            publisher_client.publish(
                f"{room}/temp", json.dumps({"value": temp, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/humidity", json.dumps({"value": hum, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/light", json.dumps({"value": light, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/co2", json.dumps({"value": co2, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/air_quality_pm2_5", json.dumps({"value": air_quality_pm2_5, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/air_quality_pm10", json.dumps({"value": air_quality_pm10, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sound", json.dumps({"value": sound, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/voc", json.dumps({"value": voc, "timestamp": timestamp}))

            logger.info(f"Simulated data for {room}: Temp={temp}°C, Light={light} lux, CO2={co2} ppm, "
                        f"Air Quality PM2_5={air_quality_pm2_5} μg/m³, Air Quality PM10={air_quality_pm10} μg/m³, "
                        f"Sound={sound} dB, VOC={voc} μg/m³ at {timestamp}")
        except Exception as e:
            logger.error(f"Failed to publish simulated data for {room}: {e}")

        time.sleep(1)


# Load configuration from file
def load_config_from_file(config_file="config.json"):
    """Load room configurations from a JSON file."""
    try:
        with open(config_file, "r") as file:
            config_data = json.load(file)
            logger.info("Configuration loaded successfully.")
            return config_data.get("rooms", [])
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        st.error(f"Failed to load configuration: {e}")
        return []


# Initialize simulators from configuration
def initialize_simulators_from_config(rooms):
    """Initialize simulators based on room configuration data."""
    for room_config in rooms:
        room_name = room_config["name"]

        # Extract sensor ranges
        sensor_ranges = {}
        for sensor in room_config["sensors"]:
            sensor_ranges[sensor["name"]] = sensor["range"]

        # Initialize simulator thread for this room
        if room_name not in st.session_state.simulator_threads:
            st.session_state.simulator_threads[room_name] = {
                'ranges': sensor_ranges,
                'stop_event': threading.Event()
            }

            # Start the simulator thread
            thread_data_ref = st.session_state.simulator_threads[room_name]
            stop_event = thread_data_ref['stop_event']
            thread = threading.Thread(target=simulator, args=(
                room_name, thread_data_ref, stop_event), daemon=True)
            thread.start()
            thread_data_ref['thread'] = thread

            st.session_state.active_simulators.add(room_name)
            logger.info(f"Simulator for {room_name} initialized.")


# Load and initialize simulators from config
config_file_path = os.getenv('SIMULATOR_CONFIG_FILE', 'config.json')
rooms_config = load_config_from_file(config_file_path)
initialize_simulators_from_config(rooms_config)


# Streamlit UI
st.title("Arduino Simulators Dashboard")

st.sidebar.header("Manage Simulators")
# Add Simulator
with st.sidebar.expander("Add Simulator"):
    add_room = st.text_input("Room Identifier", "")
    if st.button("Add Simulator"):
        if add_room:
            if not re.match("^[A-Za-z0-9_-]+$", add_room):
                st.error(
                    "Invalid room identifier. Use only letters, numbers, underscores, or hyphens.")
            elif add_room in st.session_state.active_simulators:
                st.warning(f"Simulator for {add_room} is already active.")
            else:
                # Define default ranges for all parameters
                default_ranges = {
                    'temp': [20, 30],
                    'hum': [30, 60],
                    'light': [300, 800],
                    'co2': [350, 500],
                    'air_quality_pm2_5': [10, 100],
                    'air_quality_pm10': [10, 100],
                    'sound': [30, 80],
                    'voc': [50, 150]
                }

                # Store the simulator ranges and other details in session_state
                st.session_state.simulator_threads[add_room] = {
                    'ranges': default_ranges,  # Store the ranges here
                    'stop_event': threading.Event()
                }

                # Pass a reference to the thread
                thread_data_ref = st.session_state.simulator_threads[add_room]
                stop_event = thread_data_ref['stop_event']

                # Start the simulator thread
                thread = threading.Thread(target=simulator, args=(
                    add_room, thread_data_ref, stop_event), daemon=True)
                thread.start()

                # Add thread to session_state
                thread_data_ref['thread'] = thread

                # Update active simulators
                st.session_state.active_simulators.add(add_room)

                st.success(f"Added simulator for {add_room}")
        else:
            st.error("Room identifier cannot be empty.")


# Remove Simulator
with st.sidebar.expander("Remove Simulator"):
    if st.session_state.active_simulators:
        remove_room = st.selectbox("Select Room to Remove", sorted(
            st.session_state.active_simulators))
        if st.button("Remove Simulator"):
            if remove_room:
                # Retrieve and stop the simulator thread
                simulator_info = st.session_state.simulator_threads.get(
                    remove_room)
                if simulator_info:
                    simulator_info['stop_event'].set()
                    simulator_info['thread'].join(timeout=2)
                    logger.info(f"Simulator for {remove_room} stopped.")
                    del st.session_state.simulator_threads[remove_room]

                # Update active simulators and sensor data
                st.session_state.active_simulators.discard(remove_room)
                st.session_state.sensor_data.pop(remove_room, None)

                st.success(f"Removed simulator for {remove_room}")
    else:
        st.write("No simulators to remove.")

# Update Simulator
with st.sidebar.expander("Update Simulator"):
    if st.session_state.active_simulators:
        update_room = st.selectbox("Select Room to Update", sorted(
            st.session_state.active_simulators))
        if update_room:
            current_ranges = st.session_state.simulator_threads[update_room]['ranges']
            logger.error(f"Updating parameters for {update_room}:")
            logger.error(type(current_ranges['temp'][0]))
            st.write(f"Updating parameters for {update_room}:")
            
            # Convert values to float to avoid type mismatch errors
            temp_min, temp_max = st.slider("Temperature Range (°C):", min_value=0.0, max_value=50.0,
                                           value=(float(current_ranges['temp'][0]), float(current_ranges['temp'][1])), step=0.1)
            hum_min, hum_max = st.slider("Humidity Range (%):", min_value=0.0, max_value=100.0,
                                         value=(float(current_ranges['hum'][0]), float(current_ranges['hum'][1])), step=0.1)
            light_min, light_max = st.slider("Light Range (lux):", min_value=0.0, max_value=2000.0,
                                             value=(float(current_ranges['light'][0]), float(current_ranges['light'][1])), step=1.0)
            co2_min, co2_max = st.slider("CO2 Range (ppm):", min_value=300.0, max_value=2000.0,
                                         value=(float(current_ranges['co2'][0]), float(current_ranges['co2'][1])), step=1.0)
            air_pm2_5_min, air_pm2_5_max = st.slider("Air Quality Range, pm2.5 (μg/m³):", min_value=0.0, max_value=200.0,
                                                     value=(float(current_ranges['air_quality_pm2_5'][0]), float(current_ranges['air_quality_pm2_5'][1])), step=0.1)
            air_pm10_min, air_pm10_max = st.slider("Air Quality Range, pm10 (μg/m³):", min_value=0.0, max_value=200.0,
                                                   value=(float(current_ranges['air_quality_pm10'][0]), float(current_ranges['air_quality_pm10'][1])), step=0.1)
            sound_min, sound_max = st.slider("Sound Range (dB):", min_value=0.0, max_value=120.0,
                                             value=(float(current_ranges['sound'][0]), float(current_ranges['sound'][1])), step=1.0)
            voc_min, voc_max = st.slider("VOC Range (μg/m³):", min_value=0.0, max_value=500.0,
                                         value=(float(current_ranges['voc'][0]), float(current_ranges['voc'][1])), step=1.0)


            if st.button("Update Simulator"):
                st.session_state.simulator_threads[update_room]['ranges'] = {
                    'temp': [temp_min, temp_max],
                    'hum': [hum_min, hum_max],
                    'light': [light_min, light_max],
                    'co2': [co2_min, co2_max],
                    'air_quality_pm2_5': [air_pm2_5_min, air_pm2_5_max],
                    'air_quality_pm10': [air_pm10_min, air_pm10_max],
                    'sound': [sound_min, sound_max],
                    'voc': [voc_min, voc_max]
                }

                st.success(f"Updated ranges for {update_room}")
    else:
        st.write("No simulators to update.")



# Display Active Simulators
st.header("Active Simulators")
if st.session_state.active_simulators:
    for room in sorted(st.session_state.active_simulators):
        # Create an expander for each room
        with st.expander(f"Room: {room}"):
            # Retrieve the ranges for the room
            ranges = st.session_state.simulator_threads[room]['ranges']

            # Display the ranges in a table format
            st.write("**Parameter Ranges:**")
            st.table(pd.DataFrame(ranges).T.rename(
                columns={0: 'Min', 1: 'Max'}))
else:
    st.write("No active simulators.")
