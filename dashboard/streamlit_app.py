import streamlit as st
import pandas as pd
import requests
import re

API_BASE = "http://localhost:9999"  # Adjust if your API is hosted elsewhere

st.title("Arduino Simulators Dashboard")

# --------------------------
# Display current simulators
# --------------------------
st.header("Active Simulators")
try:
    resp = requests.get(f"{API_BASE}/simulators")
    if resp.ok:
        data = resp.json()
        simulators = data.get("active_simulators", [])
        configurations = data.get("configurations", {})
        if simulators:
            for room in sorted(simulators):
                with st.expander(f"Room: {room}"):
                    config = configurations.get(room, {})
                    if config:
                        df = pd.DataFrame.from_dict(
                            config, orient="index", columns=["Min", "Max"])
                        st.table(df)
                    else:
                        st.write("No configuration available.")
        else:
            st.write("No active simulators.")
    else:
        st.error("Failed to fetch simulators data from API.")
except Exception as e:
    st.error(f"Error connecting to API: {e}")

# --------------------------
# Add a new simulator
# --------------------------
with st.sidebar.expander("Add Simulator"):
    add_room = st.text_input("Room Identifier", "")
    if st.button("Add Simulator"):
        if add_room:
            # Validate room identifier
            if not re.match("^[A-Za-z0-9_-]+$", add_room):
                st.error(
                    "Invalid room identifier. Use only letters, numbers, underscores, or hyphens.")
            else:
                # Define default ranges for a new simulator.
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
                payload = {"room": add_room, "ranges": default_ranges}
                try:
                    resp = requests.post(
                        f"{API_BASE}/simulators", json=payload)
                    if resp.ok:
                        st.success(f"Added simulator for {add_room}")
                    else:
                        st.error(f"Failed to add simulator: {resp.json().get('message')}")
                except Exception as e:
                    st.error(f"Error adding simulator: {e}")
        else:
            st.error("Room identifier cannot be empty.")

# --------------------------
# Update an existing simulator
# --------------------------
with st.sidebar.expander("Update Simulator"):
    try:
        resp = requests.get(f"{API_BASE}/simulators")
        if resp.ok:
            data = resp.json()
            simulators = data.get("active_simulators", [])
        else:
            simulators = []
    except Exception:
        simulators = []

    if simulators:
        update_room = st.selectbox("Select Room to Update", sorted(simulators))
        if update_room:
            # For simplicity, we only update temperature range here, but you can extend to all parameters.
           
            
            current_ranges = current_config = data.get(
                "configurations", {}).get(update_room, {})
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
                # Prepare updated configuration (extend to other sensors as needed)
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
                payload = {"ranges": new_ranges}
                try:
                    resp = requests.put(
                        f"{API_BASE}/simulators/{update_room}", json=payload)
                    if resp.ok:
                        st.success(f"Updated simulator for {update_room}")
                    else:
                        st.error(f"Failed to update simulator: {resp.json().get('message')}")
                except Exception as e:
                    st.error(f"Error updating simulator: {e}")
    else:
        st.write("No simulators available for update.")
        


# --------------------------
# Remove a simulator
# --------------------------
with st.sidebar.expander("Remove Simulator"):
    try:
        resp = requests.get(f"{API_BASE}/simulators")
        if resp.ok:
            data = resp.json()
            simulators = data.get("active_simulators", [])
        else:
            simulators = []
    except Exception:
        simulators = []

    if simulators:
        remove_room = st.selectbox("Select Room to Remove", sorted(simulators))
        if st.button("Remove Simulator"):
            try:
                resp = requests.delete(f"{API_BASE}/simulators/{remove_room}")
                if resp.ok:
                    st.success(f"Removed simulator for {remove_room}")
                else:
                    st.error(f"Failed to remove simulator: {resp.json().get('message')}")
            except Exception as e:
                st.error(f"Error removing simulator: {e}")
    else:
        st.write("No simulators to remove.")
