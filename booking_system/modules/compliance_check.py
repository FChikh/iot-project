import pandas as pd
import numpy as np

def calculate_percentage(series):
    """Helper function to calculate the percentage of True values in a boolean series."""
    return series.mean() * 100

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
        dict: A summary of compliance.
    """
    required_columns = {'timestamp', 'co2_level'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    max_co2_level = df['co2_level'].max()
    avg_co2_level = df['co2_level'].mean()
    below_1000_ppm = calculate_percentage(df['co2_level'] < 1000)
    exceeded_1500_ppm = calculate_percentage(df['co2_level'] > 1500)

    # Must have < tolerance% above 1500, and > 50% below 1000
    compliant = (exceeded_1500_ppm <= tolerance) and (below_1000_ppm > 50)

    return {
        'avg_co2_level': avg_co2_level,
        'max_co2_level': max_co2_level,
        'below_1000_ppm': below_1000_ppm,
        'exceeded_1500_ppm': exceeded_1500_ppm,
        'compliant': compliant
    }


def check_compliance_pm25(df_pm25: pd.DataFrame, tolerance: float = 1.0):
    """
    Checks if the PM2.5 measurements meet EU air quality regulations based on 24-hour rolling averages.
    EU Regulation:
    - PM2.5: 24-hour average should not exceed 25 µg/m^3.

    Parameters:
        df_pm25 (pd.DataFrame): DataFrame with columns 'timestamp' and 'pm2_5'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.

    Returns:
        dict: A summary of compliance.
    """
    required_columns = {'timestamp', 'pm2_5'}
    if not required_columns.issubset(df_pm25.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    pm25_limit = 25

    df_pm25['timestamp'] = pd.to_datetime(df_pm25['timestamp'])
    df_pm25 = df_pm25.sort_values('timestamp')

    # Rolling 24-hour average
    df_pm25['pm2_5_rolling'] = df_pm25['pm2_5'].rolling(window=24, min_periods=24).mean()

    pm25_non_compliant = calculate_percentage(df_pm25['pm2_5_rolling'] > pm25_limit)

    compliant = pm25_non_compliant <= tolerance
    avg_pm25 = df_pm25['pm2_5'].mean()

    return {
        'avg_pm25': avg_pm25,
        'pm2_5_non_compliant': pm25_non_compliant,
        'compliant': compliant
    }


def check_compliance_pm10(df_pm10: pd.DataFrame, tolerance: float = 1.0):
    """
    Checks if the PM10 measurements meet EU air quality regulations based on 24-hour rolling averages.
    EU Regulation:
    - PM10: 24-hour average should not exceed 50 µg/m^3.

    Parameters:
        df_pm10 (pd.DataFrame): DataFrame with columns 'timestamp' and 'pm10'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.

    Returns:
        dict: A summary of compliance.
    """
    required_columns = {'timestamp', 'pm10'}
    if not required_columns.issubset(df_pm10.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    pm10_limit = 50

    df_pm10['timestamp'] = pd.to_datetime(df_pm10['timestamp'])
    df_pm10 = df_pm10.sort_values('timestamp')

    df_pm10['pm10_rolling'] = df_pm10['pm10'].rolling(window=24, min_periods=24).mean()

    pm10_non_compliant = calculate_percentage(df_pm10['pm10_rolling'] > pm10_limit)

    compliant = pm10_non_compliant <= tolerance
    avg_pm10 = df_pm10['pm10'].mean()

    return {
        'avg_pm10': avg_pm10,
        'pm10_non_compliant': pm10_non_compliant,
        'compliant': compliant
    }


def check_compliance_noise(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if indoor noise levels in a classroom comply with ISO 3382-2:2008 standard.
    WHO Recommendations:
    - Background noise: ≤ 35 dB (average noise level).
    - Peak noise levels: ≤ 55 dB.

    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'sound_values' (in dB).
        tolerance (float): Allowed percentage of time noise can exceed 55 dB.

    Returns:
        dict: A summary of compliance.
    """
    required_columns = {'timestamp', 'sound_values'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    tolerance_high_db = 1  # Allowed % for exceeding 55 dB

    avg_noise_level = df['sound_values'].mean()
    max_noise_level = df['sound_values'].max()

    # Percentage of time above 35 dB and 55 dB
    above_35_db = calculate_percentage(df['sound_values'] > 35)
    exceeded_55_db = calculate_percentage(df['sound_values'] > 55)

    compliant = (above_35_db <= tolerance) and (exceeded_55_db <= tolerance_high_db)

    return {
        'avg_noise_level': avg_noise_level,
        'max_noise_level': max_noise_level,
        'above_35_db': above_35_db,
        'exceeded_55_db': exceeded_55_db,
        'compliant': compliant
    }


def check_compliance_lighting(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Checks if the lighting intensity complies with the EN 12464-1 standard

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'light_intensity' (in lux).
        tolerance (float): Allowed percentage of time light intensity can fall below 500 lux.

    Returns:
        dict: Summary of compliance.
    """
    required_columns = {'timestamp', 'light_intensity'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    recommended_lux = 500

    avg_light_intensity = df['light_intensity'].mean()
    min_light_intensity = df['light_intensity'].min()
    max_light_intensity = df['light_intensity'].max()

    below_recommended = calculate_percentage(df['light_intensity'] < recommended_lux)

    compliant = below_recommended <= tolerance

    return {
        'avg_light_intensity': avg_light_intensity,
        'min_light_intensity': min_light_intensity,
        'max_light_intensity': max_light_intensity,
        'below_recommended': below_recommended,
        'compliant': compliant
    }


def check_humidity_compliance(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Evaluates whether indoor humidity meets EN and DIN standards for comfort and health.

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'humidity' (in % RH).
        tolerance (float): Allowed percentage of time humidity can fall outside the range.

    Returns:
        dict: Summary of compliance.
    """
    required_columns = {'timestamp', 'humidity'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    recommended_min = 30
    recommended_max = 70

    avg_humidity = df['humidity'].mean()
    min_humidity = df['humidity'].min()
    max_humidity = df['humidity'].max()

    in_range = df['humidity'].between(recommended_min, recommended_max)
    percent_in_range = calculate_percentage(in_range)

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
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'voc_values' (in ppb).
        tolerance (float): Allowed percentage of time VOC levels can exceed the acceptable limit.

    Returns:
        dict: Compliance summary.
    """
    required_columns = {'timestamp', 'voc_values'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")

    acceptable_limit = 400

    avg_voc_level = df['voc_values'].mean()
    max_voc_level = df['voc_values'].max()
    percent_above_limit = calculate_percentage(df['voc_values'] > acceptable_limit)

    compliant = percent_above_limit <= tolerance

    return {
        'avg_voc_level': avg_voc_level,
        'max_voc_level': max_voc_level,
        'percent_above_limit': percent_above_limit,
        'compliant': compliant
    }