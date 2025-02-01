import pandas as pd
import numpy as np
from modules.data_fetcher import *
from modules.compliance_check import *
from datetime import datetime, timedelta

def topsis_decision_logic(room_data, user_pref, weights=None, lower_better_cols=[]):
    """
    Perform TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
    to rank rooms based on user preferences.

    Parameters:
        room_data (pd.DataFrame): DataFrame containing attributes of each room.
        user_pref (dict): Dictionary of user preferences for each attribute.
        weights (list or None): List of weights for each attribute. If None, all attributes are equally weighted.
        lower_better_cols (list): List of columns where lower values are better.

    Returns:
        pd.DataFrame: DataFrame with closeness coefficients and ranks for each room.
    """
    try:
        # Validate inputs
        if room_data.empty:
            return pd.DataFrame()
            
        # Data preparation: compute the inverse of absolute differences between the room's attribute and the user preference.
        adjusted_df = pd.DataFrame(index=room_data.index)
        for col in room_data.columns:
            if col in user_pref:
                # For now, using the same transformation for all attributes;
                # you can customize this if needed for equipment vs. sensor data.
                adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))
            else:
                # If the column is not in user preferences, just copy it over.
                adjusted_df[col] = room_data[col]

        # Normalization of the decision matrix
        norm = np.sqrt((adjusted_df**2).sum())
        normalized = adjusted_df / norm

        # Weight handling
        if weights is None:
            weights = np.ones(len(room_data.columns))
        weights = np.array(weights) / np.sum(weights)
        weighted = normalized * weights

        # Handle single-room case early
        if len(room_data) == 1:
            result = room_data.copy()
            result['score'] = 1.0
            result['rank'] = 1
            return result

        # Determine the ideal (best) and negative ideal (worst) solutions
        pis = weighted.max()
        nis = weighted.min()

        # Calculate distances to the ideal and negative ideal solutions
        dist_pis = np.sqrt(((weighted - pis)**2).sum(axis=1))
        dist_nis = np.sqrt(((weighted - nis)**2).sum(axis=1))

        # Closeness coefficient calculation
        closeness = dist_nis / (dist_pis + dist_nis)

        # Prepare the final results
        result = room_data.copy()
        result['score'] = closeness
        result['rank'] = closeness.rank(ascending=False)
        
        return result.sort_values('rank')

    except Exception as e:
        print(f"TOPSIS error: {str(e)}")
        return pd.DataFrame()



def build_topsis_matrix(rooms, environmental_data, rooms_and_equipments):
    """
    Constructs the TOPSIS decision matrix by evaluating the compliance of each room based on environmental data and including equipment attributes.

    Parameters:
        rooms (list): List of room IDs.
        environmental_data (list): List of environmental sensor names.
        rooms_and_equipments (list): List of dictionaries containing room equipment data.

    Returns:
        pd.DataFrame: DataFrame containing attributes of compliant rooms for TOPSIS ranking.
    """
    # Mapping of sensors to their respective compliance check functions
    compliance_functions = {
        'co2': check_compliance_co2,
        'pm2_5': check_compliance_pm25,
        'pm10': check_compliance_pm10,
        'noise': check_compliance_noise,
        'light': check_compliance_lighting,
        'humidity': check_humidity_compliance,
        'voc': check_compliance_voc,
        'temperature': check_compliance_temperature,
    }

    compliant_rooms = []
    compliant_room_ids = []  # To track compliant room IDs

    for room_id in rooms:
        print(f"Evaluating {room_id}...")
        room_attributes = {}
        is_compliant = True

        # Check environmental compliance
        for sensor in environmental_data:
            sensor_data = download_sensor_data(room_id, sensor)
            compliance_result = perform_compliance_check(sensor, sensor_data, compliance_functions)
            if not compliance_result.get('compliant', False):
                print(f"{room_id} failed compliance for {sensor}. Skipping room.")
                is_compliant = False
                break

            # Extract sensor attributes
            extracted_attributes = extract_sensor_attributes(sensor, compliance_result)
            room_attributes.update(extracted_attributes)

        if is_compliant:
            # Add equipment attributes
            equipment_data = fetch_equipment(rooms_and_equipments, room_id)
            if equipment_data:
                room_attributes.update(equipment_data)
                compliant_rooms.append(room_attributes)
                compliant_room_ids.append(room_id)
                print(f"{room_id} is compliant. Added equipment data.\n")
            else:
                print(f"No equipment data found for {room_id}. Skipping room.\n")
        else:
            print(f"{room_id} is not compliant and will be excluded from ranking.\n")

    if not compliant_rooms:
        print("No compliant rooms found.")
        return pd.DataFrame()

    # Create DataFrame with compliant rooms and their attributes
    topsis_df = pd.DataFrame(compliant_rooms, index=compliant_room_ids)
    return topsis_df


def perform_compliance_check(sensor, sensor_data, compliance_functions):
    """
    Performs compliance check for a given sensor using the appropriate function.

    Parameters:
        sensor (str): Sensor name.
        sensor_data (pd.DataFrame): DataFrame containing sensor data.
        compliance_functions (dict): Mapping of sensors to compliance functions.

    Returns:
        dict: Compliance result dictionary.
    """
    compliance_func = compliance_functions.get(sensor)
    if not compliance_func:
        print(f"No compliance function defined for {sensor}. Skipping sensor.")
        return {'compliant': True}

    compliance_result = compliance_func(sensor_data)
    return compliance_result

def extract_sensor_attributes(sensor, compliance_result):
    """
    Extracts relevant attributes from compliance results based on the sensor type.

    Parameters:
        sensor (str): Sensor name.
        compliance_result (dict): Result from the compliance check function.

    Returns:
        dict: Extracted attributes relevant to TOPSIS.
    """
    attributes = {}
    if sensor == 'co2':
        attributes['co2'] = compliance_result.get('avg_co2_level')
    elif sensor == 'pm2_5':
        attributes['pm2_5'] = compliance_result.get('avg_pm25')
    elif sensor == 'pm10':
        attributes['pm10'] = compliance_result.get('avg_pm10')
    elif sensor == 'noise':
        attributes['noise'] = compliance_result.get('avg_noise_level')
    elif sensor == 'light':
        attributes['light'] = compliance_result.get('avg_light_intensity')
    elif sensor == 'humidity':
        attributes['humidity'] = compliance_result.get('avg_humidity')
    elif sensor == 'voc':
        attributes['voc'] = compliance_result.get('avg_voc_level')
    elif sensor == 'temperature':
        attributes['temperature'] = compliance_result.get('avg_temperature')
    return attributes

def check_seats(room_id, rooms_and_equipments, needed_seats):
    equipments = fetch_equipment(rooms_and_equipments, room_id)
    if equipments["capacity"] >= needed_seats:
        return True
    return False

        
def check_availability(date: str, start_time: str, end_time: str, rooms_and_equipments: dict, needed_seats: int) -> list:
    """
    Checks which rooms are available between the specified start and end times on the given date.

    Args:
        date (str): The date in "YYYY-MM-DD" format.
        start_time (str): The start time in "HH:MM:SS" format, must be in 30-minute increments (00 or 30 minutes).
        end_time (str): The end time in "HH:MM:SS" format, must be in 30-minute increments and after start_time.
        rooms_and_equipments (dict): Dictionary containing room and equipment information.
        needed_seats (int): Number of seats required.

    Returns:
        list: A list of room IDs that have enough seats and are available during the specified time period.
    """
    try:
        # Validate datetime formats
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")

        # Validate time constraints
        if end_datetime <= start_datetime:
            raise ValueError("End time must be after start time")

        if start_datetime.date() != end_datetime.date():
            raise ValueError("Start and end times must be on the same date")

        if (start_datetime.minute % 30 != 0) or (start_datetime.second != 0):
            raise ValueError("Start time must be in 30-minute increments with 0 seconds")

        if (end_datetime.minute % 30 != 0) or (end_datetime.second != 0):
            raise ValueError("End time must be in 30-minute increments with 0 seconds")

        # Calculate required time slots
        required_slots = []
        current_slot = start_datetime
        while current_slot < end_datetime:
            required_slots.append(current_slot.strftime("%Y-%m-%d %H:%M:%S"))
            current_slot += timedelta(minutes=30)

        # Fetch data with error handling
        all_rooms = fetch_rooms(rooms_and_equipments) or []
        bookings_data = fetch_room_bookings(date, days=1)

        # Check availability
        available_rooms = []
        for room_id in all_rooms:
            booked_slots = bookings_data.get(room_id, [])
            if not any(slot in booked_slots for slot in required_slots):
                
                if check_seats(room_id, rooms_and_equipments, needed_seats):
                    available_rooms.append(room_id)
                else:
                    print(f"{room_id} does not have enough seats")

        return available_rooms

    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return []
    except Exception as e:
        print(f"Availability check failed: {str(e)}")
        return []
    
def create_user_prefs(seating_capacity, projector, blackboard, smartboard, microphone, computer_class, pc, whiteboard, air_quality_preference, noise_level, lighting):

    if air_quality_preference == "high":
        co2 = 350
        pm2_5 = 1
        pm10 = 5
    else:
        co2 = 500
        pm2_5 = 10
        pm10 = 15

    if noise_level == "silent":
        noise = 20
    else:
        noise = 40

    if lighting == "bright":
        lighting = 1000
    else:
        lighting = 500



    user_prefs = {
        'co2': co2,
        'noise': noise,
        'pm2_5': pm2_5,
        'pm10': pm10,
        'light': lighting,
        'humidity': 50,
        'voc': 50,
        'temperature': 21,
        'projector': 1 if projector else 0,
        'capacity': seating_capacity,
        'blackboard': 1 if blackboard else 0,
        'computer-class': 1 if computer_class else 0,
        'microphone': 1 if microphone else 0,
        'pc': 1 if pc else 0,
        'smartboard': 1 if smartboard else 0,
        'whiteboard': 1 if whiteboard else 0,
    }

    return user_prefs


def get_ranking(date, start_time, end_time, seating_capacity, projector, blackboard, smartboard, microphone, computer_class, pc, whiteboard, air_quality_preference, noise_level, lighting):
    
    sensors = ['co2', 'temperature', 'noise', 'light', 'humidity', 'voc', 'pm2_5', 'pm10']
    rooms_and_equipments = fetch_rooms_and_equipments()
    available_rooms = check_availability(date, start_time, end_time, rooms_and_equipments, seating_capacity)
    print("Available rooms:", available_rooms)
    
    if not available_rooms:
        print("No available rooms. Returning empty list.")
        return json.dumps([])
    
    decision_matrix = build_topsis_matrix(available_rooms, sensors, rooms_and_equipments)
    print("Decision Matrix:\n", decision_matrix)
    
    if decision_matrix.empty:
        print("Decision matrix is empty. Returning empty list.")
        return json.dumps([])
    
    lower_better_cols = ['co2', 'noise', 'voc', 'temperature', 'capacity']
    weights = [1, 0.5, 1, 0.5, 0.5, 1, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2]
    user_prefs = create_user_prefs(seating_capacity, projector, blackboard, smartboard, microphone, computer_class, pc, whiteboard, air_quality_preference, noise_level, lighting)

    topsis = topsis_decision_logic(room_data=decision_matrix, user_pref=user_prefs, weights=weights, lower_better_cols=lower_better_cols)
    
    if topsis.empty:
        print("No rooms ranked. Returning empty list.")
        return json.dumps([])
    
    columns = ['projector', 'blackboard', 'smartboard', 'microphone', 'computer-class', 'pc', 'whiteboard']
    for column in columns:
        if column in topsis.columns:
            topsis[column] = topsis[column].map({0: False, 1: True})
        else:
            print(f"Column {column} not found in TOPSIS results. Skipping.")
    
    print("TOPSIS Ranking:\n", topsis)
    topsis_json = topsis.reset_index().rename(columns={"index": "room_id"}).to_json(orient="records", indent=4)
    return topsis_json

print(get_ranking("2025-01-24", "08:30:00", "10:30:00", 30, True, True, False, True, False, False, False, "High", "Normal", "Normal"))