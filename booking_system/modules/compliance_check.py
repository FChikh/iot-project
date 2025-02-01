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
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'value'.
        tolerance (float): Allowed percentage of time CO2 levels can exceed the range.

    Returns:
        dict: A summary of compliance.
    """

    max_co2_level = df['value'].max()
    avg_co2_level = df['value'].mean()
    below_1000_ppm = calculate_percentage(df['value'] < 1000)
    exceeded_1500_ppm = calculate_percentage(df['value'] > 1500)

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
        df_pm25 (pd.DataFrame): DataFrame with columns 'timestamp' and 'value'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.

    Returns:
        dict: A summary of compliance.
    """

    pm25_limit = 25

    df_pm25['timestamp'] = pd.to_datetime(df_pm25['timestamp'])
    df_pm25 = df_pm25.sort_values('timestamp')

    # Rolling 24-hour average
    df_pm25['pm2_5_rolling'] = df_pm25['value'].rolling(window=24).mean()

    pm25_non_compliant = calculate_percentage(df_pm25['pm2_5_rolling'] > pm25_limit)

    compliant = pm25_non_compliant <= tolerance
    avg_pm25 = df_pm25['value'].mean()

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
        df_pm10 (pd.DataFrame): DataFrame with columns 'timestamp' and 'value'.
        tolerance (float): Allowed percentage of non-compliant 24-hour periods.

    Returns:
        dict: A summary of compliance.
    """

    pm10_limit = 50

    df_pm10['timestamp'] = pd.to_datetime(df_pm10['timestamp'])
    df_pm10 = df_pm10.sort_values('timestamp')

    df_pm10['pm10_rolling'] = df_pm10['value'].rolling(window=24).mean()

    pm10_non_compliant = calculate_percentage(df_pm10['pm10_rolling'] > pm10_limit)

    compliant = pm10_non_compliant <= tolerance
    avg_pm10 = df_pm10['value'].mean()

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
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'value' (in dB).
        tolerance (float): Allowed percentage of time noise can exceed 55 dB.

    Returns:
        dict: A summary of compliance.
    """

    tolerance_high_db = 1  # Allowed % for exceeding 55 dB

    avg_noise_level = df['value'].mean()
    max_noise_level = df['value'].max()

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
        df (pd.DataFrame): DataFrame with 'timestamp' and 'value' (in lux).
        tolerance (float): Allowed percentage of time light intensity can fall below 500 lux.

    Returns:
        dict: Summary of compliance.
    """

    recommended_lux = 500

    avg_light_intensity = df['value'].mean()
    min_light_intensity = df['value'].min()
    max_light_intensity = df['value'].max()

    below_recommended = calculate_percentage(df['value'] < recommended_lux)

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
        df (pd.DataFrame): DataFrame with 'timestamp' and 'value' (in % RH).
        tolerance (float): Allowed percentage of time humidity can fall outside the range.

    Returns:
        dict: Summary of compliance.
    """

    recommended_min = 30
    recommended_max = 70

    avg_humidity = df['value'].mean()
    min_humidity = df['value'].min()
    max_humidity = df['value'].max()

    in_range = df['value'].between(recommended_min, recommended_max)
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

    acceptable_limit = 400

    avg_voc_level = df['value'].mean()
    max_voc_level = df['value'].max()
    percent_above_limit = calculate_percentage(df['value'] > acceptable_limit)

    compliant = percent_above_limit <= tolerance

    return {
        'avg_voc_level': avg_voc_level,
        'max_voc_level': max_voc_level,
        'percent_above_limit': percent_above_limit,
        'compliant': compliant
    }

def check_compliance_temperature(df: pd.DataFrame, tolerance: float = 5.0):
    """
    Evaluates whether indoor temperature meets EU comfort and health guidelines.

    EU & WHO recommendations:
    - Comfortable range: 20°C to 28°C (for general indoor spaces).
    - WHO recommends a minimum of 18°C for indoor living spaces and at least 20°C for vulnerable groups.

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'value' (temperature in °C).
        tolerance (float): Allowed percentage of time temperature can fall outside the recommended range.

    Returns:
        dict: Summary of compliance.
    """
    recommended_min = 20
    recommended_max = 26

    avg_temperature = df['value'].mean()
    min_temperature = df['value'].min()
    max_temperature = df['value'].max()

    in_range = df['value'].between(recommended_min, recommended_max)
    percent_in_range = calculate_percentage(in_range)

    compliant = percent_in_range >= (100 - tolerance)

    return {
        'avg_temperature': avg_temperature,
        'min_temperature': min_temperature,
        'max_temperature': max_temperature,
        'percent_in_range': percent_in_range,
        'compliant': compliant
    }