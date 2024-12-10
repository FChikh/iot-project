# dashboard/streamlit_app.py

import streamlit as st
import pandas as pd
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import os
import logging
import threading
from queue import Queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = os.getenv('MQTT_BROKER', 'mosquitto')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
CONTROL_TOPIC = 'control/simulator'

# Initialize session state
if 'active_simulators' not in st.session_state:
    st.session_state.active_simulators = set()

if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = {}

# Initialize a Queue for thread-safe communication
message_queue = Queue()

# Function to publish control messages
def publish_control(action, room, temp_range=None, light_range=None):
    message = {'action': action, 'room': room}
    if temp_range:
        message['temp_range'] = temp_range
    if light_range:
        message['light_range'] = light_range
    payload = json.dumps(message)
    topic = f"{CONTROL_TOPIC}/{action}"
    try:
        publish.single(topic, payload=payload, hostname=MQTT_BROKER, port=MQTT_PORT)
        logger.info(f"Published to {topic}: {payload}")
    except Exception as e:
        logger.error(f"Failed to publish to {topic}: {e}")
        st.error(f"Failed to publish control message: {e}")

# MQTT Client to listen to sensor data
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker.")
        # Subscribe to all temp and light topics
        client.subscribe("+/temp")
        client.subscribe("+/light")
    else:
        logger.error(f"Failed to connect to MQTT broker, return code {rc}")
        st.error("Failed to connect to MQTT broker.")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    logger.debug(f"Received message on {topic}: {payload}")
    try:
        room = topic.split('/')[0]
        sensor_type = topic.split('/')[1]
        value = float(payload) if sensor_type == 'temp' else int(payload)

        # Put the data into the queue
        message_queue.put({'room': room, 'sensor_type': sensor_type, 'value': value})
    except Exception as e:
        logger.error(f"Error processing message on {topic}: {e}")

# Function to run MQTT client in a separate thread
def run_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        logger.error(f"Could not connect to MQTT Broker: {e}")
        st.error("Could not connect to MQTT Broker.")
        return

    client.loop_forever()

# Start MQTT client in a separate thread
mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
mqtt_thread.start()

# Function to process messages from the queue
def process_queue():
    while not message_queue.empty():
        msg = message_queue.get()
        room = msg['room']
        sensor_type = msg['sensor_type']
        value = msg['value']

        # Update active simulators
        st.session_state.active_simulators.add(room)
        
        # Update sensor data
        if room not in st.session_state.sensor_data:
            st.session_state.sensor_data[room] = {'temp': [], 'light': []}
        st.session_state.sensor_data[room][sensor_type].append(value)
        
        # Keep only the latest N data points to prevent memory issues
        N = 100
        if len(st.session_state.sensor_data[room][sensor_type]) > N:
            st.session_state.sensor_data[room][sensor_type] = st.session_state.sensor_data[room][sensor_type][-N:]

# Streamlit UI
st.title("Arduino Simulators Dashboard")

st.sidebar.header("Manage Simulators")

# Add Simulator
with st.sidebar.expander("Add Simulator"):
    add_room = st.text_input("Room Identifier", "")
    if st.button("Add Simulator"):
        if add_room:
            publish_control('add', add_room)
            st.success(f"Added simulator for {add_room}")
        else:
            st.error("Room identifier cannot be empty.")

# Remove Simulator
with st.sidebar.expander("Remove Simulator"):
    if st.session_state.active_simulators:
        remove_room = st.selectbox("Select Room to Remove", sorted(st.session_state.active_simulators))
        if st.button("Remove Simulator"):
            if remove_room:
                publish_control('remove', remove_room)
                st.success(f"Removed simulator for {remove_room}")
                st.session_state.active_simulators.discard(remove_room)
                st.session_state.sensor_data.pop(remove_room, None)
    else:
        st.write("No simulators to remove.")

# Update Simulator
with st.sidebar.expander("Update Simulator"):
    if st.session_state.active_simulators:
        update_room = st.selectbox("Select Room to Update", sorted(st.session_state.active_simulators))
        st.write("Set Temperature Range (°C):")
        temp_min, temp_max = st.slider("Temperature Range", min_value=0.0, max_value=50.0, value=(20.0, 30.0))
        st.write("Set Light Range:")
        light_min, light_max = st.slider("Light Range", min_value=0, max_value=2000, value=(300, 800))
        if st.button("Update Simulator"):
            if update_room:
                publish_control('update', update_room, temp_range=[temp_min, temp_max], light_range=[light_min, light_max])
                st.success(f"Updated simulator for {update_room}")
    else:
        st.write("No simulators to update.")

# Display Active Simulators
st.header("Active Simulators")
if st.session_state.active_simulators:
    st.write(sorted(st.session_state.active_simulators))
else:
    st.write("No active simulators.")

# Visualize Sensor Data
st.header("Sensor Data Visualization")

# Process messages from the queue
process_queue()

# Prepare data for visualization
if st.session_state.sensor_data:
    # Create DataFrames for temperature and light
    temp_data = []
    light_data = []
    for room, sensors in st.session_state.sensor_data.items():
        if 'temp' in sensors and sensors['temp']:
            temp_data.append({'room': room, 'temp': sensors['temp'][-1]})
        if 'light' in sensors and sensors['light']:
            light_data.append({'room': room, 'light': sensors['light'][-1]})
    
    temp_df = pd.DataFrame(temp_data)
    light_df = pd.DataFrame(light_data)
    
    # Set 'room' as index
    if not temp_df.empty:
        temp_df = temp_df.set_index('room')
        st.subheader("Temperature")
        st.bar_chart(temp_df['temp'])  # Removed x parameter
    else:
        st.write("No temperature data available.")
    
    if not light_df.empty:
        light_df = light_df.set_index('room')
        st.subheader("Light")
        st.bar_chart(light_df['light'])  # Removed x parameter
    else:
        st.write("No light data available.")
else:
    st.write("No sensor data available.")
