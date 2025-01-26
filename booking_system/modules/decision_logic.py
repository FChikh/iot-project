import pandas as pd
import numpy as np
from data_fetcher import *
from compliance_check import *

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

    adjusted_df = pd.DataFrame(index=room_data.index)
    for col in room_data.columns:
        if col in lower_better_cols:
            adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))
        else:
            adjusted_df[col] = 1 / (1 + abs(room_data[col] - user_pref[col]))


    norm = np.sqrt((adjusted_df**2).sum())
    normalized = adjusted_df / norm

    if weights is None:
        weights = np.ones(len(room_data.columns))
    weights = np.array(weights) / np.sum(weights)
    weighted = normalized * weights


    pis = weighted.max()
    nis = weighted.min()

    dist_pis = np.sqrt(((weighted - pis)**2).sum(axis=1))
    dist_nis = np.sqrt(((weighted - nis)**2).sum(axis=1))


    closeness = dist_nis / (dist_pis + dist_nis)


    result = room_data.copy()
    result['Closeness Coefficient'] = closeness
    result['Rank'] = closeness.rank(ascending=False)
    
    return result.sort_values('Rank')


def check_availability(date, start_time, end_time, seating_capacity, videoprojector_needed, num_computers):

    pass


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
        'co2_level': check_compliance_co2,
        'pm2_5': check_compliance_pm25,
        'pm10': check_compliance_pm10,
        'sound_values': check_compliance_noise,
        'light_intensity': check_compliance_lighting,
        'humidity': check_humidity_compliance,
        'voc_values': check_compliance_voc
    }

    compliant_rooms = []

    for room in rooms:
        print(f"Evaluating {room}...")
        room_attributes = {}
        is_compliant = True

        for sensor in environmental_data:
            if sensor == 'seating_capacity':
                # Handle 'seating_capacity' separately
                seating_capacity = retrieve_seating_capacity(room)
                if seating_capacity is not None:
                    room_attributes['seating_capacity'] = seating_capacity
                else:
                    print(f"Failed to retrieve seating_capacity for {room}. Skipping room.")
                    is_compliant = False
                    break
                continue  # Move to the next sensor

            # Download sensor data
            sensor_data = download_and_validate_sensor_data(room, sensor)
            if sensor_data is None or sensor_data.empty:
                print(f"Failed to retrieve {sensor} data for {room}. Skipping room.")
                is_compliant = False
                break

            # Check compliance
            compliance_result = perform_compliance_check(sensor, sensor_data, compliance_functions)
            if not compliance_result.get('compliant', False):
                print(f"{room} failed compliance for {sensor}. Skipping room.")
                is_compliant = False
                break

            # Extract and store relevant attributes based on sensor type
            extracted_attributes = extract_sensor_attributes(sensor, compliance_result)
            room_attributes.update(extracted_attributes)

        if is_compliant:
            print(f"{room} is compliant. Adding to TOPSIS matrix.\n")
            compliant_rooms.append(room_attributes)
        else:
            print(f"{room} is not compliant and will be excluded from ranking.\n")

    if not compliant_rooms:
        print("No compliant rooms found.")
        return pd.DataFrame()

    # Create DataFrame for TOPSIS with room names as index
    topsis_df = pd.DataFrame(compliant_rooms, index=rooms)

    # Ensure all required attributes are present, assign default values if necessary
    required_attributes = [
        'co2_level', 'pm2_5', 'pm10', 'sound_values', 
        'light_intensity', 'humidity', 'voc_values', 'seating_capacity'
    ]
    for attr in required_attributes:
        if attr not in topsis_df.columns:
            print(f"Attribute '{attr}' is missing. Assigning default value of 0.")
            topsis_df[attr] = 0

    # Replace any NaN values with 0 to maintain data integrity
    topsis_df.fillna(0, inplace=True)

    return topsis_df

def download_and_validate_sensor_data(room, sensor):
    """
    Downloads sensor data for a given room and sensor, validates it, and returns the DataFrame.

    Parameters:
        room (str): Room ID.
        sensor (str): Sensor name.

    Returns:
        pd.DataFrame or None: Sensor data DataFrame if successful, else None.
    """
    sensor_data = download_sensor_data(room, sensor)
    if sensor_data is None or sensor_data.empty:
        print(f"Failed to retrieve {sensor} data for {room}. Skipping room.")
        return None
    return sensor_data

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
        return {'compliant': True}  # Assume compliant if no function is defined

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
    if sensor == 'co2_level':
        attributes['co2_level'] = compliance_result.get('avg_co2_level')
        attributes['below_1000_ppm'] = compliance_result.get('below_1000_ppm')
    elif sensor == 'pm2_5':
        attributes['pm2_5'] = compliance_result.get('avg_pm25')
    elif sensor == 'pm10':
        attributes['pm10'] = compliance_result.get('avg_pm10')
    elif sensor == 'sound_values':
        attributes['sound_values'] = compliance_result.get('avg_noise_level')
        attributes['above_35_db'] = compliance_result.get('percent_above_35_db')
    elif sensor == 'light_intensity':
        attributes['light_intensity'] = compliance_result.get('avg_light_intensity')
        attributes['below_recommended'] = compliance_result.get('below_recommended')
    elif sensor == 'humidity':
        attributes['humidity'] = compliance_result.get('avg_humidity')
    elif sensor == 'voc_values':
        attributes['voc_values'] = compliance_result.get('avg_voc_level')
    return attributes

def retrieve_seating_capacity(room):
    """
    Retrieves seating capacity for the given room.

    Parameters:
        room (str): Room ID.

    Returns:
        float or None: Seating capacity value, or None if retrieval fails.
    """
    try:
        df_seating = download_sensor_data(room, 'seating_capacity')
        if df_seating.empty:
            print(f"Failed to retrieve seating_capacity for {room}.")
            return None
        # Assuming seating_capacity is a single value, take the maximum reported
        seating_capacity = df_seating['seating_capacity'].max()
        return seating_capacity
    except Exception as e:
        print(f"Error retrieving seating_capacity for {room}: {e}")
        return None


        

        



def booking(date, start_time, end_time, seating_capacity, videoprojector_needed, num_computers, air_quality_preference, noise_level_preference):





    #check available rooms

    available_rooms= check_availability(date, start_time, end_time, seating_capacity, videoprojector_needed, num_computers)

    environmental_data = ['co2_level', 'pm2_5', 'pm10', 'sound_values', 'light_intensity', 'humidity', 'voc_values', 'seating_capacity']

    room_data_matrix = build_topsis_matrix(available_rooms, environmental_data)


    pm25_preference = 0
    pm10_preference = 0

    preferences = {
    'co2_level': 0,
    'pm2_5': 0,
    'pm10': 0,
    'noise_level': 0,
    'light_intensity': 500,
    'humidity': 45,
    'VOC_level': 200,
    'seating_capacity': seating_capacity,
    }





