import pandas as pd
import json


def load_json_to_dataframe(file_path: str, sensor_name: str) -> pd.DataFrame:
    """
    Opens a JSON file and loads the content of a specific sensor into a pandas DataFrame.

    Args:
        file_path (str): The path to the JSON file.
        sensor_name (str): The key in the JSON file corresponding to the desired sensor data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the JSON data, or an empty DataFrame if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)  # Load the JSON content
            
            # Convert the relevant part of the JSON into a DataFrame
            df = pd.DataFrame(json_data[sensor_name])

        return df
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except KeyError:
        print(f"Key '{sensor_name}' not found in JSON file: {file_path}")
        return pd.DataFrame()  # Return an empty DataFrame if the key is missing


def download_sensor_data(room, sensor_name, start, end):
    pass

