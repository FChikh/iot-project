import pandas as pd
import numpy as np

def check_compliance_co2(df: pd.DataFrame):
    """
    Checks if the classroom meets EU regulations for CO2 levels for the provided two-week data.
    
    German Committee on Indoor Air Guide Values:
    - Good air quality: CO2 levels < 1000 ppm.
    - Acceptable threshold: CO2 levels should not exceed 1500 ppm.
    
    Parameters:
        df (pd.DataFrame): DataFrame with columns 'timestamp' and 'co2_level'.
        
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
    exceeded_1500_ppm = (df['co2_level'] > 1500).any()
    

    compliant = not exceeded_1500_ppm and below_1000_ppm > 50 
    

    return {
        'max_co2_level': max_co2_level,
        'avg_co2_level': avg_co2_level,
        'below_1000_ppm': below_1000_ppm,
        'exceeded_1500_ppm': exceeded_1500_ppm,
        'compliant': compliant
    }

import pandas as pd

def check_compliance_air_quality(df: pd.DataFrame):
    """
    Checks if the classroom meets EU air quality regulations for PM2.5 and PM10 levels
    based on 24-hour rolling averages.

    EU Regulations:
    - PM2.5: 24-hour average should not exceed 25 µg/m^3.
    - PM10: 24-hour average should not exceed 50 µg/m^3.
    
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
    Checks if indoor noise levels in a classroom comply with ISO 3382-2:2008 standard.
    
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

import pandas as pd

def check_compliance_lighting(df: pd.DataFrame):
    """    
    Checks if the lighting intensity complies with the EN 12464-1 standard

    Parameters:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'illuminance' (in lux).
        
    Returns:
        dict: Summary of compliance, including:
            - 'avg_illuminance': Average illuminance over the recorded period.
            - 'min_illuminance': Minimum illuminance.
            - 'max_illuminance': Maximum illuminance.
            - 'compliant': Boolean indicating if illuminance consistently meets the threshold.
    """
    # Recommended illuminance for lecture halls
    recommended_lux = 500
    
    avg_illuminance = df['illuminance'].mean()
    min_illuminance = df['illuminance'].min()
    max_illuminance = df['illuminance'].max()
    
    compliant = min_illuminance >= recommended_lux
    
    return {
        'avg_illuminance': avg_illuminance,
        'min_illuminance': min_illuminance,
        'max_illuminance': max_illuminance,
        'compliant': compliant
    }

