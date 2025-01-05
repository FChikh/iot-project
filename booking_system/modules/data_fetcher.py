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
        api_url = f"http://localhost:8080/room/{room_id}/{sensor_name}"
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


def download_room_bookings(api_url: str, date: str):

    pass


def check_eu_regulations_co2(df: pd.DataFrame):
    """
    Checks if the room meets EU regulations for CO₂ levels for the provided two-week data.
    
    EU regulations:
    - Good air quality: CO₂ levels < 1000 ppm.
    - Acceptable threshold: CO₂ levels should not exceed 1500 ppm.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'co2_level'.
        
    Returns:
        dict: A summary of compliance, including:
            - 'max_co2_level': Maximum CO₂ level recorded.
            - 'avg_co2_level': Average CO₂ level.
            - 'below_1000_ppm': Percentage of time CO₂ levels were below 1000 ppm.
            - 'exceeded_1500_ppm': Boolean indicating if levels exceeded 1500 ppm.
            - 'compliant': Boolean indicating if the room meets EU regulations.
    """
    # Calculate key statistics
    max_co2_level = df['co2_level'].max()
    avg_co2_level = df['co2_level'].mean()
    below_1000_ppm = (df['co2_level'] < 1000).mean() * 100
    exceeded_1500_ppm = (df['co2_level'] > 1500).any()
    
    # Determine compliance
    compliant = not exceeded_1500_ppm and below_1000_ppm > 50  # At least 50% below 1000 ppm
    
    # Return summary
    return {
        'max_co2_level': max_co2_level,
        'avg_co2_level': avg_co2_level,
        'below_1000_ppm': below_1000_ppm,
        'exceeded_1500_ppm': exceeded_1500_ppm,
        'compliant': compliant
    }

import pandas as pd

def check_eu_regulations_air_quality(df: pd.DataFrame):
    """
    Checks if the room meets EU air quality regulations for PM2.5 and PM10 levels
    based on 24-hour rolling averages.

    EU Regulations:
    - PM2.5: 24-hour average should not exceed 25 µg/m³.
    - PM10: 24-hour average should not exceed 50 µg/m³.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp', 'pm2.5', and 'pm10'.
                          Data should cover at least two weeks and have regular timestamps.
                          
    Returns:
        dict: A summary of compliance, including:
            - 'avg_pm2.5': Overall average PM2.5.
            - 'avg_pm10': Overall average PM10.
            - 'pm2.5_non_compliant_hours': Count of non-compliant 24-hour periods for PM2.5.
            - 'pm10_non_compliant_hours': Count of non-compliant 24-hour periods for PM10.
            - 'overall_compliant': Boolean indicating if all rolling averages are compliant.
    """

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    df['pm2.5_rolling'] = df['pm2.5'].rolling(window=24, min_periods=24).mean()
    df['pm10_rolling'] = df['pm10'].rolling(window=24, min_periods=24).mean()
    
    pm25_non_compliant = (df['pm2.5_rolling'] > 25).sum()
    pm10_non_compliant = (df['pm10_rolling'] > 50).sum()
    
    overall_compliant = pm25_non_compliant == 0 and pm10_non_compliant == 0
    
    avg_pm25 = df['pm2.5'].mean()
    avg_pm10 = df['pm10'].mean()
    
    # Return results
    return {
        'avg_pm2.5': avg_pm25,
        'avg_pm10': avg_pm10,
        'pm2.5_non_compliant_hours': pm25_non_compliant,
        'pm10_non_compliant_hours': pm10_non_compliant,
        'overall_compliant': overall_compliant
    }


import pandas as pd

def check_noise_compliance(df: pd.DataFrame):
    """
    Checks if indoor noise levels in a classroom comply with WHO recommendations.
    
    WHO Recommendations:
    - Background noise: ≤ 35 dB (average noise level).
    - Peak noise levels: ≤ 55 dB.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'noise_level' (in dB).
        
    Returns:
        dict: A summary of compliance, including:
            - 'avg_noise_level': Average noise level.
            - 'max_noise_level': Maximum noise level recorded.
            - 'below_35_db': Percentage of time noise levels were ≤ 35 dB.
            - 'exceeded_55_db': Boolean indicating if any noise level exceeded 55 dB.
            - 'compliant': Boolean indicating overall compliance.
    """

    avg_noise_level = df['noise_level'].mean()
    max_noise_level = df['noise_level'].max()
    below_35_db = (df['noise_level'] <= 35).mean() * 100
    exceeded_55_db = (df['noise_level'] > 55).any()
    
    compliant = (avg_noise_level <= 35) and not exceeded_55_db
    
    return {
        'avg_noise_level': avg_noise_level,
        'max_noise_level': max_noise_level,
        'below_35_db': below_35_db,
        'exceeded_55_db': exceeded_55_db,
        'compliant': compliant
    }
