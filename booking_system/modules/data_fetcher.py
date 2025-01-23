import pandas as pd
import requests
import json

def download_sensor_data(room_id: str, sensor_name: str) -> pd.DataFrame:
    """
    Fetches a JSON file from a REST API and loads the content of a specific sensor into a pandas DataFrame.

    Args:
        room_id (str): The room id from where the sensor data should be retrieved.
        sensor_name (str): The key in the JSON data corresponding to the desired sensor data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the JSON data, or an empty DataFrame if an error occurs.
    """
    try:
        api_url = f"https://localhost:8087/{room_id}/{sensor_name}"
        
        response = requests.get(api_url)
        response.raise_for_status()  
        
        json_data = response.json() 
        
        
        df = pd.DataFrame(json_data[sensor_name])
        
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except ValueError as e:
        print(f"Error decoding JSON data from API response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None


def download_room_bookings(date: str, days: int):

    try:
        api_url = f"https://localhost:8080/rooms/bookings?startDate={date}&days={days}"

        response = requests.get(api_url)
        response.raise_for_status()  
            
        json_data = response.json()

        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except ValueError as e:
        print(f"Error decoding JSON data from API response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None