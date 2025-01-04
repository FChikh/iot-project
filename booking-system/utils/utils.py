import pandas as pd
import requests
import json

def download_sensor_data(api_url: str, sensor_name: str) -> pd.DataFrame:
    """
    Fetches a JSON file from a REST API and loads the content of a specific sensor into a pandas DataFrame.

    Args:
        api_url (str): The URL of the REST API endpoint returning JSON data.
        sensor_name (str): The key in the JSON data corresponding to the desired sensor data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the JSON data, or an empty DataFrame if an error occurs.
    """
    try:
        # Fetch the JSON data from the REST API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        json_data = response.json()  # Parse the JSON content
        
        # Convert the relevant part of the JSON into a DataFrame
        df = pd.DataFrame(json_data[sensor_name])

        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error
    except KeyError:
        print(f"Key '{sensor_name}' not found in JSON data from API: {api_url}")
        return pd.DataFrame()  # Return an empty DataFrame if the key is missing
    except ValueError:
        print("Error decoding JSON data from API response.")
        return pd.DataFrame()  # Return an empty DataFrame on JSON decoding error


