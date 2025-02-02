import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Import external modules (assumed to be available in your project)
from modules.data_fetcher import fetch_rooms, fetch_rooms_and_equipments, fetch_equipment, fetch_room_bookings, download_sensor_data
from modules.compliance_check import (
    check_compliance_co2,
    check_compliance_pm25,
    check_compliance_pm10,
    check_compliance_noise,
    check_compliance_lighting,
    check_humidity_compliance,
    check_compliance_voc,
    check_compliance_temperature,
)


def topsis_decision_logic(room_data: pd.DataFrame, user_pref: dict, weights=None, lower_better_cols=[]) -> pd.DataFrame:
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
        # Validate input
        if room_data.empty:
            return pd.DataFrame()

        # Adjust the decision matrix based on user preferences
        adjusted_df = pd.DataFrame(index=room_data.index)
        for col in room_data.columns:
            if col in user_pref:
                adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))
            else:
                adjusted_df[col] = room_data[col]

        # Normalize the decision matrix
        norm = np.sqrt((adjusted_df ** 2).sum())
        normalized = adjusted_df / norm

        # Apply weights (if not provided, use equal weighting)
        if weights is None:
            weights = np.ones(len(room_data.columns))
        weights = np.array(weights) / np.sum(weights)
        weighted = normalized * weights

        # Handle single-room scenario
        if len(room_data) == 1:
            result = room_data.copy()
            result['score'] = 1.0
            result['rank'] = 1
            return result

        # Determine the positive ideal solution (PIS) and negative ideal solution (NIS)
        # Adjusting the logic for columns where lower values are better.
        ideal_best = {}
        ideal_worst = {}
        for col in weighted.columns:
            if col in lower_better_cols:
                ideal_best[col] = weighted[col].min()  # lower is better
                ideal_worst[col] = weighted[col].max()
            else:
                ideal_best[col] = weighted[col].max()  # higher is better
                ideal_worst[col] = weighted[col].min()

        # Convert the ideal values to a Series for vectorized computation
        ideal_best_series = pd.Series(ideal_best)
        ideal_worst_series = pd.Series(ideal_worst)

        # Calculate Euclidean distances from the PIS and NIS
        dist_pis = np.sqrt(((weighted - ideal_best_series) ** 2).sum(axis=1))
        dist_nis = np.sqrt(((weighted - ideal_worst_series) ** 2).sum(axis=1))

        # Calculate the closeness coefficient
        closeness = dist_nis / (dist_pis + dist_nis)

        # Prepare and return the final results with scores and rankings
        result = room_data.copy()
        result['score'] = closeness
        result['rank'] = closeness.rank(ascending=False)
        return result.sort_values('rank')

    except Exception as e:
        print(f"TOPSIS error: {str(e)}")
        return pd.DataFrame()



def perform_compliance_check(sensor: str, sensor_data: pd.DataFrame, compliance_functions: dict) -> dict:
    """
    Performs compliance check for a given sensor using the appropriate function.

    Parameters:
        sensor (str): Sensor name.
        sensor_data (pd.DataFrame): DataFrame containing sensor data.
        compliance_functions (dict): Mapping of sensor names to their compliance functions.

    Returns:
        dict: Dictionary with compliance result.
    """
    compliance_func = compliance_functions.get(sensor)
    if not compliance_func:
        print(f"No compliance function defined for sensor '{sensor}'. Assuming compliant.")
        return {'compliant': True}
    return compliance_func(sensor_data)


def extract_sensor_attributes(sensor: str, compliance_result: dict) -> dict:
    """
    Extracts relevant attributes from the compliance result for the given sensor.

    Parameters:
        sensor (str): Sensor name.
        compliance_result (dict): Result from the compliance check.

    Returns:
        dict: Dictionary of extracted attributes.
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


def build_topsis_matrix(rooms: list, environmental_sensors: list, rooms_and_equipments: list) -> pd.DataFrame:
    """
    Constructs the TOPSIS decision matrix by evaluating the compliance of each room based on environmental data,
    and incorporating equipment attributes.

    Parameters:
        rooms (list): List of room IDs.
        environmental_sensors (list): List of environmental sensor names.
        rooms_and_equipments (list): List of dictionaries containing room equipment data.

    Returns:
        pd.DataFrame: DataFrame with attributes of compliant rooms for TOPSIS ranking.
    """
    # Mapping sensor names to their compliance functions
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
    compliant_room_ids = []

    for room_id in rooms:
        print(f"Evaluating room: {room_id}")
        room_attributes = {}
        is_compliant = True

        # Evaluate each environmental sensor for compliance
        for sensor in environmental_sensors:
            sensor_data = download_sensor_data(room_id, sensor)
            compliance_result = perform_compliance_check(sensor, sensor_data, compliance_functions)
            if not compliance_result.get('compliant', False):
                print(f"Room {room_id} failed compliance for sensor '{sensor}'. Skipping room.")
                is_compliant = False
                break

            # Extract and update sensor-specific attributes
            room_attributes.update(extract_sensor_attributes(sensor, compliance_result))

        # If room passed environmental compliance, add equipment data
        if is_compliant:
            equipment_data = fetch_equipment(rooms_and_equipments, room_id)
            if equipment_data:
                room_attributes.update(equipment_data)
                compliant_rooms.append(room_attributes)
                compliant_room_ids.append(room_id)
                print(f"Room {room_id} is compliant. Equipment data added.\n")
            else:
                print(f"Room {room_id}: No equipment data found. Skipping room.\n")
        else:
            print(f"Room {room_id} is not compliant and will be excluded from ranking.\n")

    if not compliant_rooms:
        print("No compliant rooms found.")
        return pd.DataFrame()

    # Construct and return the decision matrix DataFrame
    return pd.DataFrame(compliant_rooms, index=compliant_room_ids)

def check_seats(room_id: str, rooms_and_equipments: list, needed_seats: int) -> bool:
    """
    Checks if a room has enough seating capacity.

    Parameters:
        room_id (str): The room identifier.
        rooms_and_equipments (list): Equipment data for rooms.
        needed_seats (int): Number of required seats.

    Returns:
        bool: True if the room meets or exceeds the required seating capacity.
    """
    equipments = fetch_equipment(rooms_and_equipments, room_id)
    return equipments.get("capacity", 0) >= needed_seats


def check_availability(date: str, start_time: str, end_time: str, rooms_and_equipments: dict, needed_seats: int) -> list:
    """
    Checks which rooms are available within a specified time period and have sufficient seating capacity.

    Parameters:
        date (str): Date in "YYYY-MM-DD" format.
        start_time (str): Start time in "HH:MM:SS" format (must be on 30-minute increments).
        end_time (str): End time in "HH:MM:SS" format (must be on 30-minute increments and after start_time).
        rooms_and_equipments (dict): Dictionary containing room and equipment information.
        needed_seats (int): Number of seats required.

    Returns:
        list: List of available room IDs.
    """
    try:
        # Validate and parse date and time inputs
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M:%S")
        if end_datetime <= start_datetime:
            raise ValueError("End time must be after start time")
        if start_datetime.date() != end_datetime.date():
            raise ValueError("Start and end times must be on the same date")
        if (start_datetime.minute % 30 != 0) or (start_datetime.second != 0):
            raise ValueError("Start time must be in 30-minute increments with 0 seconds")
        if (end_datetime.minute % 30 != 0) or (end_datetime.second != 0):
            raise ValueError("End time must be in 30-minute increments with 0 seconds")

        # Generate required time slots in 30-minute increments
        required_slots = []
        current_slot = start_datetime
        while current_slot < end_datetime:
            required_slots.append(current_slot.strftime("%Y-%m-%d %H:%M:%S"))
            current_slot += timedelta(minutes=30)

        all_rooms = fetch_rooms(rooms_and_equipments) or []
        bookings_data = fetch_room_bookings(date, days=1)

        # Determine available rooms
        available_rooms = []
        for room_id in all_rooms:
            booked_slots = bookings_data.get(room_id, [])
            if not any(slot in booked_slots for slot in required_slots):
                if check_seats(room_id, rooms_and_equipments, needed_seats):
                    available_rooms.append(room_id)
                else:
                    print(f"Room {room_id} does not have enough seats.")

        return available_rooms

    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return []
    except Exception as e:
        print(f"Availability check failed: {str(e)}")
        return []


def create_user_prefs(seating_capacity: int, projector: bool, blackboard: bool, smartboard: bool,
                      microphone: bool, pc: bool, whiteboard: bool,
                      air_quality_preference: str, noise_level: str, lighting: str) -> dict:
    """
    Creates a dictionary of user preferences based on provided parameters.
    """
    # Set environmental preferences based on air quality
    if air_quality_preference.lower() == "high":
        co2 = 350
        pm2_5 = 5
        pm10 = 10
    else:
        co2 = 500
        pm2_5 = 10
        pm10 = 15

    # Set noise preference
    noise = 15 if noise_level.lower() == "silent" else 30

    # Set lighting preference
    light = 800 if lighting.lower() == "bright" else 500

    user_prefs = {
        'co2': co2,
        'noise': noise,
        'pm2_5': pm2_5,
        'pm10': pm10,
        'light': light,
        'humidity': 50,
        'voc': 50,
        'temperature': 21,
        'projector': 1 if projector else 0,
        'capacity': seating_capacity,
        'blackboard': 1 if blackboard else 0,
        'microphone': 1 if microphone else 0,
        'pc': 1 if pc else 0,
        'smartboard': 1 if smartboard else 0,
        'whiteboard': 1 if whiteboard else 0,
    }
    return user_prefs


def get_ranking(date: str, start_time: str, end_time: str, seating_capacity: int, projector: bool,
                blackboard: bool, smartboard: bool, microphone: bool, pc: bool,
                whiteboard: bool, air_quality_preference: str, noise_level: str, lighting: str) -> list:
    """
    Determines the ranking of available and compliant rooms based on user preferences and TOPSIS.

    Parameters:
        date (str): Date in "YYYY-MM-DD" format.
        start_time (str): Start time in "HH:MM:SS" format.
        end_time (str): End time in "HH:MM:SS" format.
        seating_capacity (int): Required seating capacity.
        projector (bool): Whether a projector is required.
        blackboard (bool): Whether a blackboard is required.
        smartboard (bool): Whether a smartboard is required.
        microphone (bool): Whether a microphone is required.
        pc (bool): Whether a PC is required.
        whiteboard (bool): Whether a whiteboard is required.
        air_quality_preference (str): Air quality preference.
        noise_level (str): Noise level preference.
        lighting (str): Lighting preference.

    Returns:
        list: List of dictionaries representing ranked rooms.
    """
    # Define sensor list used for environmental evaluation
    sensors = ['co2', 'temperature', 'noise', 'light', 'humidity', 'voc', 'pm2_5', 'pm10']

    # Fetch the room and equipment data from external sources
    rooms_and_equipments = fetch_rooms_and_equipments()

    # Check for available rooms based on date, time, and seating capacity
    available_rooms = check_availability(date, start_time, end_time, rooms_and_equipments, seating_capacity)
    print("Available rooms:", available_rooms)
    if not available_rooms:
        print("No available rooms. Returning empty list.")
        return []

    # Build the decision matrix using compliant room data
    decision_matrix = build_topsis_matrix(available_rooms, sensors, rooms_and_equipments)
    print("Decision Matrix:\n", decision_matrix)
    if decision_matrix.empty:
        print("Decision matrix is empty. Returning empty list.")
        return []

    # Specify columns where lower values are preferable (if applicable)
    lower_better_cols = ['co2', 'noise', 'voc', 'temperature', 'capacity']

    # Example weights array: adjust the weights as needed.
    # The order of the attributes in the decision matrix is as follows:
    # 
    # 1. co2
    # 2. noise
    # 3. pm2_5
    # 4. pm10
    # 5. light
    # 6. humidity
    # 7. voc
    # 8. temperature
    # 9. projector
    # 10. capacity
    # 11. blackboard
    # 12. microphone
    # 13. pc
    # 14. smartboard
    # 15. whiteboard

    weights = [2, 4, 2, 2, 3, 2, 1, 3, 4, 4, 4, 4, 4, 4, 4]

    # Create the user preferences based on input parameters
    user_prefs = create_user_prefs(seating_capacity, projector, blackboard, smartboard,
                                   microphone, pc, whiteboard,
                                   air_quality_preference, noise_level, lighting)

    # Run TOPSIS decision logic to rank rooms
    topsis_result = topsis_decision_logic(room_data=decision_matrix, user_pref=user_prefs,
                                          weights=weights, lower_better_cols=lower_better_cols)
    if topsis_result.empty:
        print("No rooms ranked. Returning empty list.")
        return []

    # Convert equipment columns to boolean values if present
    equipment_columns = ['projector', 'blackboard', 'smartboard', 'microphone', 'pc', 'whiteboard']
    for column in equipment_columns:
        if column in topsis_result.columns:
            topsis_result[column] = topsis_result[column].map({0: False, 1: True})
        else:
            print(f"Column '{column}' not found in TOPSIS results. Skipping conversion.")

    print("TOPSIS Ranking:\n", topsis_result)
    # Convert results to a list of dictionaries
    topsis_dict = topsis_result.reset_index().rename(columns={"index": "room_id"}).to_dict(orient='records')
    return topsis_dict

