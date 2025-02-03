import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd

# Import external modules (assumed to be available in your project)
from modules.data_fetcher import (
    fetch_rooms,
    fetch_rooms_and_equipments,
    fetch_equipment,
    fetch_room_bookings,
    download_sensor_data,
)
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


def topsis_decision_logic(
    room_data: pd.DataFrame, 
    user_pref: Dict[str, Any], 
    weights: Optional[List[float]] = None, 
    lower_better_cols: List[str] = []
) -> pd.DataFrame:
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
        if room_data.empty:
            return pd.DataFrame()

        # Step 1: Normalize the decision matrix using vectorized operations
        # (adding a small constant to avoid division by zero)
        norm = np.linalg.norm(room_data, axis=0)
        normalized = room_data / (norm + 1e-9)

        # Step 2: Apply weights (if not provided, use equal weights)
        if weights is None:
            weights = [1] * normalized.shape[1]
        weights = np.array(weights) / np.sum(weights)  # Normalize weights
        weighted = normalized * weights

        # Step 3: Identify ideal best and worst values
        ideal_best = weighted.max(axis=0)
        ideal_worst = weighted.min(axis=0)

        # Adjust for attributes where lower values are better
        for col in lower_better_cols:
            if col in room_data.columns:
                ideal_best[col], ideal_worst[col] = ideal_worst[col], ideal_best[col]

        # Step 4: Calculate Euclidean distances to ideal best & worst
        dist_pis = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
        dist_nis = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

        # Step 5: Compute the TOPSIS closeness coefficient
        closeness = dist_nis / (dist_pis + dist_nis + 1e-9)  # Avoid zero division

        # Step 6: Assign ranks based on closeness scores
        result = room_data.copy()
        result["score"] = closeness
        result["rank"] = closeness.rank(ascending=False).astype(int)

        return result.sort_values("rank")
    except Exception as e:
        print(f"TOPSIS error: {str(e)}")
        return pd.DataFrame()


def perform_compliance_check(sensor: str, sensor_data: pd.DataFrame, compliance_functions: Dict[str, Any]) -> Dict[str, Any]:
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
        return {"compliant": True}
    return compliance_func(sensor_data)


def extract_sensor_attributes(sensor: str, compliance_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts relevant attributes from the compliance result for the given sensor.

    Parameters:
        sensor (str): Sensor name.
        compliance_result (dict): Result from the compliance check.

    Returns:
        dict: Dictionary of extracted attributes.
    """
    attributes = {}
    if sensor == "co2":
        attributes["co2"] = compliance_result.get("avg_co2_level")
    elif sensor == "pm2_5":
        attributes["pm2_5"] = compliance_result.get("avg_pm25")
    elif sensor == "pm10":
        attributes["pm10"] = compliance_result.get("avg_pm10")
    elif sensor == "noise":
        attributes["noise"] = compliance_result.get("avg_noise_level")
    elif sensor == "light":
        attributes["light"] = compliance_result.get("avg_light_intensity")
    elif sensor == "humidity":
        attributes["humidity"] = compliance_result.get("avg_humidity")
    elif sensor == "voc":
        attributes["voc"] = compliance_result.get("avg_voc_level")
    elif sensor == "temperature":
        attributes["temperature"] = compliance_result.get("avg_temperature")
    return attributes


def build_topsis_matrix(rooms: List[str], environmental_sensors: List[str], rooms_and_equipments: List[Dict[str, Any]]) -> pd.DataFrame:
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
        "co2": check_compliance_co2,
        "pm2_5": check_compliance_pm25,
        "pm10": check_compliance_pm10,
        "noise": check_compliance_noise,
        "light": check_compliance_lighting,
        "humidity": check_humidity_compliance,
        "voc": check_compliance_voc,
        "temperature": check_compliance_temperature,
    }

    compliant_rooms = []
    compliant_room_ids = []

    for room_id in rooms:
        print(f"Evaluating room: {room_id}")
        room_attributes: Dict[str, Any] = {}
        is_compliant = True

        # Evaluate each environmental sensor for compliance
        for sensor in environmental_sensors:
            sensor_data = download_sensor_data(room_id, sensor)
            compliance_result = perform_compliance_check(sensor, sensor_data, compliance_functions)
            if not compliance_result.get("compliant", False):
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


def check_seats(room_id: str, rooms_and_equipments: List[Dict[str, Any]], needed_seats: int) -> bool:
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


def check_availability(
    date: str, 
    start_time: str, 
    end_time: str, 
    rooms_and_equipments: Any, 
    needed_seats: int
) -> List[str]:
    """
    Checks which rooms are available within a specified time period and have sufficient seating capacity.

    Parameters:
        date (str): Date in "YYYY-MM-DD" format.
        start_time (str): Start time in "HH:MM:SS" format (must be on 30-minute increments).
        end_time (str): End time in "HH:MM:SS" format (must be on 30-minute increments and after start_time).
        rooms_and_equipments (Any): Room and equipment information.
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

        available_rooms = []
        for room_id in all_rooms:
            booked_slots = bookings_data.get(room_id, [])
            # Check if none of the required slots are booked
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


def create_user_prefs(
    seating_capacity: int, 
    projector: bool, 
    blackboard: bool, 
    smartboard: bool,
    microphone: bool, 
    pc: bool, 
    whiteboard: bool, 
    air_quality_preference: str, 
    noise_level: str, 
    lighting: str, 
    temperature_preference: str
) -> Dict[str, Any]:
    """
    Creates a dictionary of user preferences based on provided parameters.

    Parameters:
        seating_capacity (int): Number of seats required.
        projector (bool): Whether a projector is required.
        blackboard (bool): Whether a blackboard is required.
        smartboard (bool): Whether a smartboard is required.
        microphone (bool): Whether a microphone is required.
        pc (bool): Whether a PC is required.
        whiteboard (bool): Whether a whiteboard is required.
        air_quality_preference (str): Air quality preference ("high" or other).
        noise_level (str): Noise level preference ("silent" or other).
        lighting (str): Lighting preference ("bright" or other).
        temperature_preference (str): Temperature preference ("warm", "moderate", etc.).

    Returns:
        dict: Dictionary representing user preferences.
    """
    # Set environmental preferences based on air quality preference
    if air_quality_preference.lower() == "high":
        co2 = 100
        pm2_5 = 1
        pm10 = 5
        voc = 50
    else:
        co2 = 400
        pm2_5 = 10
        pm10 = 15
        voc = 200

    # Set noise preference
    noise = 0 if noise_level.lower() == "silent" else 30

    # Set lighting preference
    light = 1500 if lighting.lower() == "bright" else 500

    # Set temperature based on preference
    if temperature_preference.lower() == "warm":
        temperature = 27
    elif temperature_preference.lower() == "moderate":
        temperature = 23
    else:
        temperature = 17

    user_prefs = {
        "co2": co2,
        "noise": noise,
        "pm2_5": pm2_5,
        "pm10": pm10,
        "light": light,
        "humidity": 50,  # Default value; adjust as needed
        "voc": voc,
        "temperature": temperature,
        "projector": 1 if projector else 0,
        "capacity": seating_capacity,
        "blackboard": 1 if blackboard else 0,
        "microphone": 1 if microphone else 0,
        "pc": 1 if pc else 0,
        "smartboard": 1 if smartboard else 0,
        "whiteboard": 1 if whiteboard else 0,
    }
    return user_prefs


def get_ranking(
    date: str, 
    start_time: str, 
    end_time: str, 
    seating_capacity: int, 
    projector: bool,
    blackboard: bool, 
    smartboard: bool, 
    microphone: bool, 
    pc: bool,
    whiteboard: bool, 
    air_quality_preference: str, 
    noise_level: str, 
    lighting: str,
    temperature_preference: str, 
    equipment_weight: int, 
    air_quality_weight: int, 
    temperature_weight: int, 
    noise_weight: int, 
    light_weight: int
) -> List[Dict[str, Any]]:
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
        temperature_preference (str): Temperature preference.
        equipment_weight (int): Weight for equipment-related criteria.
        air_quality_weight (int): Weight for air quality sensors (applied to co2, pm2_5, pm10, voc).
        temperature_weight (int): Weight for temperature sensor.
        noise_weight (int): Weight for noise sensor.
        light_weight (int): Weight for light sensor.

    Returns:
        list: List of dictionaries representing ranked rooms.
    """
    # Define sensor list used for environmental evaluation
    sensors = ["co2", "temperature", "noise", "light", "humidity", "voc", "pm2_5", "pm10"]

    # Fetch room and equipment data from external sources
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
    if temperature_preference.lower() == "cool":
        lower_better_cols = ["co2", "noise", "pm10", "pm2_5", "voc", "capacity", "temperature"]
    else:
        lower_better_cols = ["co2", "noise", "pm10", "pm2_5", "voc", "capacity"]

    # Equipment weights: only add the weight if the feature is requested
    projector_weight = equipment_weight if projector else 0
    blackboard_weight = equipment_weight if blackboard else 0
    microphone_weight = equipment_weight if microphone else 0
    pc_weight = equipment_weight if pc else 0
    smartboard_weight = equipment_weight if smartboard else 0
    whiteboard_weight = equipment_weight if whiteboard else 0

    # Weights for the decision matrix must align with the ordering of columns in the matrix.
    # The assumed order is: 
    # ['co2', 'temperature', 'noise', 'light', 'humidity', 'voc', 'pm2_5', 'pm10', 
    #  'projector', 'capacity', 'blackboard', 'microphone', 'pc', 'smartboard', 'whiteboard']
    weights = [
        air_quality_weight,      # co2
        temperature_weight,      # temperature
        noise_weight,            # noise
        light_weight,            # light
        1,                       # humidity (default weight)
        air_quality_weight,      # voc (using air quality weight)
        air_quality_weight,      # pm2_5
        air_quality_weight,      # pm10
        projector_weight,        # projector
        1,                       # capacity (default weight)
        blackboard_weight,       # blackboard
        microphone_weight,       # microphone
        pc_weight,               # pc
        smartboard_weight,       # smartboard
        whiteboard_weight        # whiteboard
    ]

    # Create the user preferences based on input parameters
    user_prefs = create_user_prefs(
        seating_capacity, projector, blackboard, smartboard,
        microphone, pc, whiteboard,
        air_quality_preference, noise_level, lighting, temperature_preference
    )

    # Run TOPSIS decision logic to rank rooms
    topsis_result = topsis_decision_logic(
        room_data=decision_matrix, 
        user_pref=user_prefs,
        weights=weights, 
        lower_better_cols=lower_better_cols
    )
    if topsis_result.empty:
        print("No rooms ranked. Returning empty list.")
        return []

    # Convert equipment columns to boolean values if present
    equipment_columns = ["projector", "blackboard", "smartboard", "microphone", "pc", "whiteboard"]
    for column in equipment_columns:
        if column in topsis_result.columns:
            topsis_result[column] = topsis_result[column].map({0: False, 1: True})
        else:
            print(f"Column '{column}' not found in TOPSIS results. Skipping conversion.")

    print("TOPSIS Ranking:\n", topsis_result)
    # Convert results to a list of dictionaries
    topsis_dict = topsis_result.reset_index().rename(columns={"index": "room_id"}).to_dict(orient="records")
    return topsis_dict


# Optional: you can include a main block for testing purposes.
if __name__ == "__main__":
    # Example parameters (adjust these as needed for your testing)
    ranking = get_ranking(
        date="2025-03-01",
        start_time="09:00:00",
        end_time="11:00:00",
        seating_capacity=20,
        projector=True,
        blackboard=False,
        smartboard=True,
        microphone=False,
        pc=True,
        whiteboard=False,
        air_quality_preference="high",
        noise_level="silent",
        lighting="bright",
        temperature_preference="warm",
        equipment_weight=5,
        air_quality_weight=3,
        temperature_weight=2,
        noise_weight=1,
        light_weight=1
    )
    print("Final Ranked Rooms:")
    print(json.dumps(ranking, indent=4))
