# pages/EquipmentEditor.py
import os
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from db import SessionLocal
from models import Room, Equipment
import requests

API_BASE = "http://localhost:9999"  # Adjust if your API is hosted elsewhere

st.title("Room Equipment Editor")
st.markdown("""
This page displays all rooms along with their equipment.
Use the provided widgets to update the equipment values:
- **Boolean values:** use checkboxes.
- **Integer values:** use number inputs.
- **Other types:** use text inputs.
""")

# Create a database session.
session = SessionLocal()

try:
    devices = session.query(Room).order_by(Room.name).all()
    if not devices:
        st.info("No devices found in the database.")
    else:
        # Loop over each device
        for device in devices:
            st.subheader(f"Room: {device.name}")
            with st.form(key=f"form_device_{device.id}"):
                updated_values = {}  # Will hold new values keyed by equipment id
                # Loop over each equipment item for this device.
                for equip in sorted(device.equipment, key=lambda equip: equip.name):
                    equip_key = f"device_{device.id}_equip_{equip.id}"
                    # Choose a widget based on the equipment type.
                    if equip.type.lower() == "boolean":
                        # Convert the stored string value to a boolean.
                        current_val = equip.value.lower() in ["true", "1", "yes"]
                        new_val = st.checkbox(f"{equip.name} (Boolean)", value=current_val, key=equip_key)
                        updated_values[equip.id] = "True" if new_val else "False"
                    elif equip.type.lower() == "integer":
                        try:
                            current_val = int(equip.value)
                        except (ValueError, TypeError):
                            current_val = 0
                        # Using number_input for integers; adjust min/max as needed.
                        new_val = st.number_input(f"{equip.name} (Integer)", value=current_val, step=1, key=equip_key)
                        updated_values[equip.id] = str(int(new_val))
                    else:
                        # For any other type, default to text input.
                        new_val = st.text_input(f"{equip.name} (String)", value=equip.value, key=equip_key)
                        updated_values[equip.id] = new_val

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    # Update the equipment values in the database.
                    for equip in device.equipment:
                        if equip.id in updated_values:
                            equip.value = updated_values[equip.id]
                    try:
                        session.commit()
                        st.success(f"Updated equipment for {device.name} successfully!")
                    except SQLAlchemyError as e:
                        session.rollback()
                        st.error(f"An error occurred while updating {device.name}: {e}")
except Exception as e:
    st.error(f"Error fetching devices: {e}")
finally:
    session.close()
    
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
