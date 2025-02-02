import pandas as pd
import requests
import json
import time


def fetch_api_data(url: str, retries: int = 5, backoff_factor: float = 1.0):
    """
    Fetches JSON data from the given API URL.

    Args:
        url (str): The API URL to fetch data from.

    Returns:
        dict: A dictionary containing the JSON data, or None if an error occurs.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed (attempt {attempt+1}/{retries}): {str(e)}")
            if attempt == retries - 1:
                return None
            sleep_time = backoff_factor * (2 ** attempt)
            time.sleep(sleep_time)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {str(e)}")
            return None
    return None


def download_sensor_data(room_id: str, sensor_name: str):
    """
    Fetches a JSON file from a REST API and loads the content of a specific sensor into a pandas DataFrame.

    Args:
        room_id (str): The room id from where the sensor data should be retrieved.
        sensor_name (str): The key in the JSON data corresponding to the desired sensor data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the JSON data, or an empty DataFrame if an error occurs.
    """
    api_url = f"http://restapi_rooms:8080/rooms/{room_id}/{sensor_name}"
    json_data = fetch_api_data(api_url)
    if json_data and sensor_name in json_data:
        return pd.DataFrame(json_data[sensor_name])
    return pd.DataFrame()


def fetch_room_bookings(date: str, days: int):
    """
    Fetches room bookings from the API.

    Args:
        date (str): The start date for the bookings.
        days (int): The number of days to fetch bookings for.

    Returns:
        dict: A dictionary containing the JSON data, or None if an error occurs.
    """
    api_url = f"http://restapi_rooms:8080/rooms/bookings?startDate={date}&days={days}"
    return fetch_api_data(api_url)


def fetch_rooms_and_equipments():
    """
    Fetches Equipments from the API.

    Returns:
        dict: A dictionary containing the JSON data, or None if an error occurs.
    """
    api_url = f"http://restapi_rooms:8080/rooms/equipment"
    return fetch_api_data(api_url)


def fetch_rooms(rooms_and_equipments):

    return [room_info["room"] for room_info in rooms_and_equipments]


def fetch_equipment(rooms_and_equipments, room_id):

    for room in rooms_and_equipments:
        if room["room"] == room_id:
            equipment = room['equipment']
            for key, value in equipment.items():
                if isinstance(value, bool):  # Check if the value is boolean
                    room['equipment'][key] = 1 if value else 0
            return equipment