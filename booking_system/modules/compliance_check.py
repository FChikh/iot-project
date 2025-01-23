import pandas as pd
import numpy as np

def check_compliance_co2(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if the classroom meets EU regulations for CO2 levels for the provided two-week data.
    
    German Committee on Indoor Air Guide Values:
    - Good air quality: CO2 levels < 1000 ppm.
    - Acceptable threshold: CO2 levels should not exceed 1500 ppm.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'co2_level'.
        tolerance (float): Allowed percentage of time CO2 levels can exceed the range.
        
    Returns:
        dict: A summary of compliance, including:
            - 'max_co2_level': Maximum CO2 level recorded.
            - 'avg_co2_level': Average CO2 level.
            - 'below_1000_ppm': Percentage of time CO2 levels were below 1000 ppm.
            - 'exceeded_1500_ppm': Boolean indicating if levels exceeded 1500 ppm.
            - 'compliant': Boolean indicating if the room meets EU regulations.
    """

    max_co2_level = df['co2_level'].max()
    avg_co2_level = df['co2_level'].mean()
    below_1000_ppm = (df['co2_level'] < 1000).mean() * 100
    exceeded_1500_ppm = (df['co2_level'] > 1500).mean() * 100

    compliant = exceeded_1500_ppm <= tolerance and below_1000_ppm > 50

    return {
        'max_co2_level': max_co2_level,
        'avg_co2_level': avg_co2_level,
        'below_1000_ppm': below_1000_ppm,
        'exceeded_1500_ppm': exceeded_1500_ppm,
        'compliant': compliant
    }

import pandas as pd

import pandas as pd

def check_compliance_pm25(df_pm25: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if the PM2.5 measurements meet EU air quality regulations based on 24-hour rolling averages.

    EU Regulation:
    - PM2.5: 24-hour average should not exceed 25 µg/m^3.
    
    Parameters:
        df_pm25 (pd.DataFrame): DataFrame with columns 'timestamp' and 'pm2.5'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.
                          
    Returns:
        dict: A summary of compliance, including:
            - 'avg_pm2.5': Overall average PM2.5.
            - 'pm2.5_non_compliant_hours': Percentage of non-compliant 24-hour periods for PM2.5.
            - 'overall_compliant': Boolean indicating if the rolling averages are compliant within tolerance.
    """
    pm25_limit = 25

    # Ensure proper datetime type and sort by timestamp
    df_pm25['timestamp'] = pd.to_datetime(df_pm25['timestamp'])
    df_pm25 = df_pm25.sort_values('timestamp')

    # Calculate rolling mean over a 24-hour window
    df_pm25['pm2.5_rolling'] = df_pm25['pm2.5'].rolling(window=24, min_periods=24).mean()

    # Calculate the percentage of non-compliant periods
    pm25_non_compliant = (df_pm25['pm2.5_rolling'] > pm25_limit).mean() * 100

    # Determine compliance based on tolerance
    overall_compliant = pm25_non_compliant <= tolerance

    # Compute overall average PM2.5
    avg_pm25 = df_pm25['pm2.5'].mean()

    return {
        'avg_pm2.5': avg_pm25,
        'pm2.5_non_compliant_hours': pm25_non_compliant,
        'overall_compliant': overall_compliant
    }


def check_compliance_pm10(df_pm10: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if the PM10 measurements meet EU air quality regulations based on 24-hour rolling averages.

    EU Regulation:
    - PM10: 24-hour average should not exceed 50 µg/m^3.
    
    Parameters:
        df_pm10 (pd.DataFrame): DataFrame with columns 'timestamp' and 'pm10'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.
                          
    Returns:
        dict: A summary of compliance, including:
            - 'avg_pm10': Overall average PM10.
            - 'pm10_non_compliant_hours': Percentage of non-compliant 24-hour periods for PM10.
            - 'overall_compliant': Boolean indicating if the rolling averages are compliant within tolerance.
    """
    pm10_limit = 50

    df_pm10['timestamp'] = pd.to_datetime(df_pm10['timestamp'])
    df_pm10 = df_pm10.sort_values('timestamp')

    df_pm10['pm10_rolling'] = df_pm10['pm10'].rolling(window=24, min_periods=24).mean()

    pm10_non_compliant = (df_pm10['pm10_rolling'] > pm10_limit).mean() * 100

    overall_compliant = pm10_non_compliant <= tolerance

    avg_pm10 = df_pm10['pm10'].mean()

    return {
        'avg_pm10': avg_pm10,
        'pm10_non_compliant_hours': pm10_non_compliant,
        'overall_compliant': overall_compliant
    }


def check_compliance_noise(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if indoor noise levels in a classroom comply with ISO 3382-2:2008 standard.
    
    WHO Recommendations:
    - Background noise: ≤ 35 dB (average noise level).
    - Peak noise levels: ≤ 55 dB.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'noise_level' (in dB).
        tolerance (float): Allowed percentage of time noise can exceed 55 dB.

        
    Returns:
        dict: A summary of compliance, including:
            - 'avg_noise_level': Average noise level.
            - 'max_noise_level': Maximum noise level recorded.
            - 'percent_above_35_db': Percentage of time noise levels were > 35 dB.
            - 'exceeded_55_db': Boolean indicating if any noise level exceeded 55 dB.
            - 'compliant': Boolean indicating overall compliance.
    """
    tolerance_high_db = 1

    avg_noise_level = df['noise_level'].mean()
    max_noise_level = df['noise_level'].max()
    percent_above_35_db = (df['noise_level'] > 35).mean() * 100
    exceeded_55_db = (df['noise_level'] > 55).mean() * 100  # Percentage exceeding 55 dB


    compliant = percent_above_35_db <= tolerance and not exceeded_55_db <= tolerance_high_db

    return {
        'avg_noise_level': avg_noise_level,
        'max_noise_level': max_noise_level,
        'percent_above_35_db': percent_above_35_db,
        'exceeded_55_db': exceeded_55_db,
        'compliant': compliant
    }

import pandas as pd

def check_compliance_lighting(df: pd.DataFrame, tolerance: float = 5.0):
    """    
    Checks if the lighting intensity complies with the EN 12464-1 standard

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'illuminance' (in lux).
        tolerance (float): Allowed percentage of time illuminance can fall below 500 lux.
        
    Returns:
        dict: Summary of compliance, including:
            - 'avg_illuminance': Average illuminance over the recorded period.
            - 'min_illuminance': Minimum illuminance.
            - 'max_illuminance': Maximum illuminance.
            - 'compliant': Boolean indicating if illuminance consistently meets the threshold.
    """
    recommended_lux = 500

    avg_illuminance = df['illuminance'].mean()
    min_illuminance = df['illuminance'].min()
    max_illuminance = df['illuminance'].max()

    below_recommended = (df['illuminance'] < recommended_lux).mean() * 100

    compliant = below_recommended <= tolerance

    return {
        'avg_illuminance': avg_illuminance,
        'min_illuminance': min_illuminance,
        'max_illuminance': max_illuminance,
        'below_recommended': below_recommended,
        'compliant': compliant
    }



def check_humidity_compliance(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Evaluates whether indoor humidity meets EN and DIN standards for comfort and health.

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'humidity' (in % RH).
        tolerance (float): Allowed percentage of time CO2 levels can exceed the range.

    Returns:
        dict: Summary of compliance, including:
            - 'avg_humidity': Average relative humidity (%).
            - 'min_humidity': Minimum relative humidity (%).
            - 'max_humidity': Maximum relative humidity (%).
            - 'compliant': Boolean indicating if humidity consistently meets the recommended range.
    """
    recommended_min = 30
    recommended_max = 70

    avg_humidity = df['humidity'].mean()
    min_humidity = df['humidity'].min()
    max_humidity = df['humidity'].max()

    in_range = (df['humidity'] >= recommended_min) & (df['humidity'] <= recommended_max)
    percent_in_range = in_range.mean() * 100

    compliant = percent_in_range >= (100 - tolerance)

    return {
        'avg_humidity': avg_humidity,
        'min_humidity': min_humidity,
        'max_humidity': max_humidity,
        'percent_in_range': percent_in_range,
        'compliant': compliant
    }


def check_compliance_voc(df: pd.DataFrame, tolerance: float = 1.0):
    """
    Checks compliance for VOC levels with tolerances for brief deviations.

    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'VOC_level' (in ppb).
        tolerance (float): Allowed percentage of time VOC levels can exceed the acceptable limit.

    Returns:
        dict: Compliance summary, including:
            - 'avg_voc_level': Average VOC level.
            - 'max_voc_level': Maximum VOC level recorded.
            - 'percent_above_limit': Percentage of time VOC levels exceeded the acceptable limit.
            - 'compliant': Boolean indicating overall compliance.
    """
    acceptable_limit = 400

    avg_voc_level = df['VOC_level'].mean()
    max_voc_level = df['VOC_level'].max()
    percent_above_limit = (df['VOC_level'] > acceptable_limit).mean() * 100

    compliant = percent_above_limit <= tolerance

    return {
        'avg_voc_level': avg_voc_level,
        'max_voc_level': max_voc_level,
        'percent_above_limit': percent_above_limit,
        'compliant': compliant
    }
