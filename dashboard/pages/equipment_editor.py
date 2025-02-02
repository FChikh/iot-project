# pages/EquipmentEditor.py

import os
import streamlit as st
import requests
import re

API_BASE = "http://localhost:9999"  # Adjust if your API is hosted elsewhere

st.title("Room Equipment Editor")
st.markdown("""
This page displays all rooms along with their equipment.
Use the provided widgets to update the equipment values:
- **Boolean values:** use checkboxes.
- **Integer values:** use number inputs.
- **Other types:** use text inputs.
""")


# Get the list of active rooms from your simulators endpoint.
try:
    simulators_resp = requests.get(f"{API_BASE}/rooms")
    if simulators_resp.ok:
        simulators_data = simulators_resp.json()
        rooms = simulators_data.get("rooms", [])
    else:
        st.error("Failed to fetch rooms data from API.")
        rooms = []
except Exception as e:
    st.error(f"Error fetching rooms: {e}")
    rooms = []

if rooms:
    for room in sorted(rooms):
        # Retrieve equipment list for the room using GET /equipment/<room>
        try:
            eq_resp = requests.get(f"{API_BASE}/equipment/{room}")
            if eq_resp.ok:
                eq_data = eq_resp.json()
                eq_list = eq_data.get("equipment", [])
            else:
                st.error(f"Failed to fetch equipment for room '{room}'.")
                eq_list = []
        except Exception as e:
            st.error(f"Error fetching equipment for room '{room}': {e}")
            eq_list = []
        if len(eq_list) == 0:
            continue
        st.subheader(f"Room: {room}")
        with st.form(key=f"form_{room}"):
            updated_equipment = []
            # Display each equipment item (sorted by name) with the appropriate widget.
            for eq in sorted(eq_list, key=lambda x: x["name"]):
                eq_name = eq["name"]
                eq_type = str(eq["type"]).lower()
                eq_value = eq["value"]
                widget_key = f"{room}_{eq['id']}"
                
                if eq_type == "boolean":
                    current_val = True if str(eq_value).lower() in ["true", "1", "yes"] else False
                    new_val = st.checkbox(f"{eq_name} (Boolean)", value=current_val, key=widget_key)
                    updated_equipment.append({
                        "name": eq_name,
                        "value": str(new_val),
                        "type": "boolean"
                    })
                elif eq_type == "integer":
                    try:
                        current_val = int(eq_value)
                    except (ValueError, TypeError):
                        current_val = 0
                    new_val = st.number_input(f"{eq_name} (Integer)", value=current_val, step=1, key=widget_key)
                    updated_equipment.append({
                        "name": eq_name,
                        "value": str(new_val),
                        "type": "integer"
                    })
                else:
                    new_val = st.text_input(f"{eq_name} (String)", value=str(eq_value), key=widget_key)
                    updated_equipment.append({
                        "name": eq_name,
                        "value": new_val,
                        "type": "string"
                    })
            
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                payload = {"equipment": updated_equipment}
                try:
                    put_resp = requests.put(f"{API_BASE}/equipment/{room}", json=payload)
                    if put_resp.ok:
                        st.success(f"Updated equipment for room '{room}'.")
                    else:
                        error_msg = put_resp.json().get("error") or put_resp.json().get("message")
                        st.error(f"Failed to update equipment for room '{room}': {error_msg}")
                except Exception as e:
                    st.error(f"Error updating equipment for room '{room}': {e}")
else:
    st.info("No rooms found.")


# Add equipment for new room
with st.sidebar.expander("Add Room Equipment"):
    new_room = st.text_input("Room Identifier", "")
    if st.button("Add Room"):
        if new_room:
            if not re.match("^[A-Za-z0-9_-]+$", new_room):
                st.error("Invalid room identifier. Use only letters, numbers, underscores, or hyphens.")
            else:
                payload = {"room": new_room}
                try:
                    # POST to /equipment/<room> creates equipment records for the new room.
                    post_resp = requests.post(f"{API_BASE}/equipment/", json=payload)
                    if post_resp.ok:
                        st.success(f"Room '{new_room}' with default equipment added.")
                    else:
                        error_msg = post_resp.json().get("error") or post_resp.json().get("message")
                        st.error(f"Failed to add room: {error_msg}")
                except Exception as e:
                    st.error(f"Error adding room: {e}")
        else:
            st.error("Room identifier cannot be empty.")

# Remove equipment for existing room
with st.sidebar.expander("Remove Room Equipment"):
    if rooms:
        remove_room = st.selectbox("Select Room to Remove", sorted(rooms))
        if st.button("Remove Room"):
            try:
                del_resp = requests.delete(f"{API_BASE}/equipment/{remove_room}")
                if del_resp.ok:
                    st.success(f"Equipment for room '{remove_room}' has been deleted.")
                else:
                    error_msg = del_resp.json().get("error") or del_resp.json().get("message")
                    st.error(f"Failed to remove equipment for room '{remove_room}': {error_msg}")
            except Exception as e:
                st.error(f"Error removing equipment for room '{remove_room}': {e}")
    else:
        st.write("No rooms available to remove.")
