import pandas as pd
import numpy as np
from data_fetcher import *
from compliance_check import *
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
            
        # Data preparation
        adjusted_df = pd.DataFrame(index=room_data.index)
        for col in room_data.columns:
            if col in lower_better_cols:
                adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))
            else:
                adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))

        # Normalization
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
            result['Closeness Coefficient'] = 1.0
            result['Rank'] = 1
            return result

        # Ideal solutions
        pis = weighted.max()
        nis = weighted.min()

        # Distance calculations
        dist_pis = np.sqrt(((weighted - pis)**2).sum(axis=1))
        dist_nis = np.sqrt(((weighted - nis)**2).sum(axis=1))

        # Closeness coefficient
        closeness = dist_nis / (dist_pis + dist_nis)

        # Final result
        result = room_data.copy()
        result['Closeness Coefficient'] = closeness
        result['Rank'] = closeness.rank(ascending=False)
        
        return result.sort_values('Rank')

    except Exception as e:
        print(f"TOPSIS error: {str(e)}")
        return pd.DataFrame()



def build_topsis_matrix(rooms, environmental_data):
    """
    Constructs the TOPSIS decision matrix by evaluating the compliance of each room based on environmental data.

    Parameters:
        rooms (list): List of room IDs.
        environmental_data (list): List of environmental sensor names.

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
    compliant_room_ids = []  # To keep track of room IDs that are compliant

    for room in rooms:
        print(f"Evaluating {room}...")
        room_attributes = {}
        is_compliant = True

        for sensor in environmental_data:
            sensor_data = download_sensor_data(room, sensor)
            compliance_result = perform_compliance_check(sensor, sensor_data, compliance_functions)
            if not compliance_result.get('compliant', False):
                print(f"{room} failed compliance for {sensor}. Skipping room.")
                is_compliant = False
                break

            extracted_attributes = extract_sensor_attributes(sensor, compliance_result)
            room_attributes.update(extracted_attributes)

        if is_compliant:
            print(f"{room} is compliant. Adding to TOPSIS matrix.\n")
            compliant_rooms.append(room_attributes)
            compliant_room_ids.append(room)  # Append the compliant room ID
        else:
            print(f"{room} is not compliant and will be excluded from ranking.\n")

    if not compliant_rooms:
        print("No compliant rooms found.")
        return pd.DataFrame()

    # Use compliant_room_ids as the DataFrame index
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
    elif sensor == ['temperature']:
        attributes['temperature'] = compliance_result.get('avg_temperature')
    return attributes

def check_seats(room_id, equipments_dict, needed_seats):
    for room in equipments_dict:
        if room["room"] == room_id:

            equipments = room["equipment"]
            if equipments["capacity"] >= needed_seats:
                return True
    return False

        
def check_availability(date: str, start_time: str, end_time: str, equipments_dict: dict, needed_seats: int) -> list:
    """
    Checks which rooms are available between the specified start and end times on the given date.

    Args:
        date (str): The date in "YYYY-MM-DD" format.
        start_time (str): The start time in "HH:MM:SS" format, must be in 30-minute increments (00 or 30 minutes).
        end_time (str): The end time in "HH:MM:SS" format, must be in 30-minute increments and after start_time.

    Returns:
        list: A list of room IDs that have enough seats and are available during the specified time period.

    Raises:
        ValueError: If the date, start_time, or end_time are invalid, or if the times are not in 30-minute increments.
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
        all_rooms = fetch_rooms(equipments_dict) or []
        bookings_data = fetch_room_bookings(date, days=1)

        # Check availability
        available_rooms = []
        for room_id in all_rooms:
            booked_slots = bookings_data.get(room_id, [])
            if not any(slot in booked_slots for slot in required_slots):
                
                if check_seats(room_id, equipments_dict, needed_seats):
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


user_prefs = {
    'co2': 0,
    'noise': 33,
    'pm2_5': 0,
    'pm10': 0,
    'light': 500,
    'humidity': 50,
    'voc': 0,
    'temperature': 21,
    'projector': 1,
}

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

date = "2025-01-24"
start_time = "08:30:00"
end_time = "10:30:00"
equipments = fetch_equipments()
available_rooms = check_availability(date, start_time, end_time, equipments, 30)
print(available_rooms)
sensors = ['co2', 'temperature', 'noise', 'light', 'humidity', 'voc', 'pm2_5', 'pm10']
#decision_matrix = build_topsis_matrix(available_rooms, sensors)
#print(decision_matrix)

lower_better_cols=['co2', 'noise', 'voc', 'temperature']


#print(topsis_decision_logic(room_data=decision_matrix, user_pref=user_prefs, weights=None, lower_better_cols=lower_better_cols))