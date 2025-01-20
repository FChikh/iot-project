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
    
# Initialize rolling data for visualization
if 'rolling_data' not in st.session_state:
    st.session_state.rolling_data = {}

# Update rolling data with new values


def update_rolling_data(room, parameter, value, window_size=100):
    if room not in st.session_state.rolling_data:
        st.session_state.rolling_data[room] = {}
    if parameter not in st.session_state.rolling_data[room]:
        st.session_state.rolling_data[room][parameter] = []
    # Append new value
    st.session_state.rolling_data[room][parameter].append(value)
    # Trim to the rolling window size
    if len(st.session_state.rolling_data[room][parameter]) > window_size:
        st.session_state.rolling_data[room][parameter] = st.session_state.rolling_data[room][parameter][-window_size:]

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

# Start MQTT client loop in a separate thread


def run_publisher():
    publisher_client.loop_start()


publisher_thread = threading.Thread(target=run_publisher, daemon=True)
publisher_thread.start()

# Simulator function


def simulator(room, ranges_ref, stop_event):
    """Simulate sensor data for a given room with user-adjustable ranges and realistic distribution."""
    while not stop_event.is_set():
        current_time = time.localtime()
        logger.info(f"Simulating data for {room} at {time.strftime('%H:%M:%S', current_time)}")
        hour = current_time.tm_hour
        ranges = ranges_ref['ranges']
        logger.info("Ranges are: " + str(ranges))

        # Generate data based on time of day and user-defined ranges
        temp = round(random.gauss(
            (ranges['temp'][0] + ranges['temp'][1]) / 2, 2), 2)
        light = max(ranges['light'][0], min(ranges['light'][1], int(
            800 * (1 if 7 <= hour <= 19 else 0.2) + random.gauss(0, 50))))
        co2 = max(ranges['co2'][0], min(ranges['co2'][1], int(
            random.gauss(400, 50) + (50 if 8 <= hour <= 20 else -30))))
        air_quality = max(ranges['air_quality'][0], min(
            ranges['air_quality'][1], int(random.gauss(50, 10))))
        sound = max(ranges['sound'][0], min(ranges['sound'][1], int(
            random.gauss(40 if hour in range(22, 7) else 60, 5))))
        voc = max(ranges['voc'][0], min(
            ranges['voc'][1], int(random.gauss(100, 20))))

        # Generate ISO 8601 timestamp
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Publish to MQTT topics with timestamp
        try:
            publisher_client.publish(
                f"{room}/temp", json.dumps({"value": temp, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/light", json.dumps({"value": light, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/co2", json.dumps({"value": co2, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/air_quality", json.dumps({"value": air_quality, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/sound", json.dumps({"value": sound, "timestamp": timestamp}))
            publisher_client.publish(
                f"{room}/voc", json.dumps({"value": voc, "timestamp": timestamp}))

            logger.info(f"Simulated data for {room}: Temp={temp}°C, Light={light} lux, CO2={co2} ppm, "
                        f"Air Quality={air_quality} μg/m³, Sound={sound} dB, VOC={voc} μg/m³ at {timestamp}")
        except Exception as e:
            logger.error(f"Failed to publish simulated data for {room}: {e}")

        time.sleep(1)  # Publish every second


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
                    'temp': [20.0, 30.0],
                    'light': [300, 800],
                    'co2': [350, 500],
                    'air_quality': [10, 100],
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
            st.write(f"Updating parameters for {update_room}:")
            temp_min, temp_max = st.slider("Temperature Range (°C):", min_value=0.0, max_value=50.0,
                                           value=(current_ranges['temp'][0], current_ranges['temp'][1]))
            light_min, light_max = st.slider("Light Range (lux):", min_value=0, max_value=2000,
                                             value=(current_ranges['light'][0], current_ranges['light'][1]))
            co2_min, co2_max = st.slider("CO2 Range (ppm):", min_value=300, max_value=2000,
                                         value=(current_ranges['co2'][0], current_ranges['co2'][1]))
            air_min, air_max = st.slider("Air Quality Range (μg/m³):", min_value=0, max_value=200,
                                         value=(current_ranges['air_quality'][0], current_ranges['air_quality'][1]))
            sound_min, sound_max = st.slider("Sound Range (dB):", min_value=0, max_value=120,
                                             value=(current_ranges['sound'][0], current_ranges['sound'][1]))
            voc_min, voc_max = st.slider("VOC Range (μg/m³):", min_value=0, max_value=500,
                                         value=(current_ranges['voc'][0], current_ranges['voc'][1]))

            if st.button("Update Simulator"):
                st.session_state.simulator_threads[update_room]['ranges'] = {
                    'temp': [temp_min, temp_max],
                    'light': [light_min, light_max],
                    'co2': [co2_min, co2_max],
                    'air_quality': [air_min, air_max],
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
