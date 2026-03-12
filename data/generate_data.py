#!/usr/bin/env python3
"""
Synthetic Air Quality Data Generator for Ward-Level Monitoring
Generates realistic sensor data for pollution monitoring across city wards
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Configuration
NUM_WARDS = 250
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
HOURS_PER_DAY = 24

# Ward coordinates (lat, lon) - simulating a city grid
def generate_ward_locations(num_wards):
    """Generate realistic ward center coordinates"""
    wards = []
    base_lat, base_lon = 28.6139, 77.2090  # Delhi-like coordinates
    
    for ward_id in range(1, num_wards + 1):
        # Create grid-like distribution with some randomness
        row = (ward_id - 1) // 16
        col = (ward_id - 1) % 16
        
        lat = base_lat + (row * 0.05) + random.uniform(-0.01, 0.01)
        lon = base_lon + (col * 0.05) + random.uniform(-0.01, 0.01)
        
        wards.append({
            'ward_id': ward_id,
            'ward_name': f'Ward {ward_id}',
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'population': random.randint(50000, 200000),
            'area_km2': round(random.uniform(2, 10), 2)
        })
    
    return wards

# Pollution source characteristics
POLLUTION_SOURCES = {
    'traffic': {
        'pm25_factor': 1.5,
        'pm10_factor': 2.0,
        'no2_factor': 2.5,
        'co_factor': 2.0,
        'peak_hours': [7, 8, 9, 17, 18, 19, 20]
    },
    'construction': {
        'pm25_factor': 2.0,
        'pm10_factor': 3.5,
        'no2_factor': 1.2,
        'co_factor': 1.0,
        'peak_hours': [10, 11, 12, 13, 14, 15]
    },
    'industrial': {
        'pm25_factor': 2.5,
        'pm10_factor': 2.0,
        'no2_factor': 3.0,
        'so2_factor': 4.0,
        'co_factor': 1.5,
        'peak_hours': list(range(6, 22))
    },
    'biomass_burning': {
        'pm25_factor': 4.0,
        'pm10_factor': 3.0,
        'co_factor': 3.5,
        'peak_hours': [18, 19, 20, 21]
    },
    'residential': {
        'pm25_factor': 1.0,
        'pm10_factor': 1.0,
        'no2_factor': 1.0,
        'co_factor': 1.0,
        'peak_hours': [6, 7, 18, 19, 20]
    }
}

def assign_ward_characteristics(ward_id):
    """Assign pollution source profile to each ward"""
    # Different wards have different dominant pollution sources
    ward_profiles = {
        'traffic_heavy': list(range(1, 11)),
        'construction_zone': list(range(11, 21)),
        'industrial': list(range(21, 31)),
        'residential': list(range(31, 41)),
        'mixed': list(range(41, 51))
    }
    
    for profile, wards in ward_profiles.items():
        if ward_id in wards:
            if profile == 'traffic_heavy':
                return 'traffic', 0.7
            elif profile == 'construction_zone':
                return 'construction', 0.8
            elif profile == 'industrial':
                return 'industrial', 0.75
            elif profile == 'residential':
                return 'residential', 0.5
            else:
                return random.choice(['traffic', 'residential', 'construction']), 0.6
    
    return 'residential', 0.5

def calculate_base_pollution(hour, source_type, intensity):
    """Calculate base pollution levels based on time and source"""
    source_config = POLLUTION_SOURCES[source_type]
    
    # Time-based multiplier
    time_multiplier = 1.5 if hour in source_config['peak_hours'] else 1.0
    
    # Base levels (µg/m³)
    base_pm25 = 35 * source_config.get('pm25_factor', 1.0) * intensity * time_multiplier
    base_pm10 = 50 * source_config.get('pm10_factor', 1.0) * intensity * time_multiplier
    base_no2 = 40 * source_config.get('no2_factor', 1.0) * intensity * time_multiplier
    base_so2 = 10 * source_config.get('so2_factor', 1.0) * intensity * time_multiplier
    base_co = 1.0 * source_config.get('co_factor', 1.0) * intensity * time_multiplier
    base_o3 = 30 * (1.5 if 11 <= hour <= 16 else 0.8)  # Ozone peaks in afternoon
    
    return {
        'pm25': max(5, base_pm25 + np.random.normal(0, base_pm25 * 0.15)),
        'pm10': max(10, base_pm10 + np.random.normal(0, base_pm10 * 0.15)),
        'no2': max(5, base_no2 + np.random.normal(0, base_no2 * 0.2)),
        'so2': max(2, base_so2 + np.random.normal(0, base_so2 * 0.25)),
        'co': max(0.1, base_co + np.random.normal(0, base_co * 0.2)),
        'o3': max(5, base_o3 + np.random.normal(0, base_o3 * 0.2))
    }

def calculate_aqi(pollutants):
    """Calculate AQI based on pollutant concentrations (simplified Indian AQI)"""
    def get_sub_index(concentration, breakpoints):
        for bp in breakpoints:
            if bp['c_low'] <= concentration <= bp['c_high']:
                aqi = ((bp['i_high'] - bp['i_low']) / (bp['c_high'] - bp['c_low'])) * \
                      (concentration - bp['c_low']) + bp['i_low']
                return aqi
        return 500  # Severe
    
    # PM2.5 breakpoints
    pm25_bp = [
        {'c_low': 0, 'c_high': 30, 'i_low': 0, 'i_high': 50},
        {'c_low': 31, 'c_high': 60, 'i_low': 51, 'i_high': 100},
        {'c_low': 61, 'c_high': 90, 'i_low': 101, 'i_high': 200},
        {'c_low': 91, 'c_high': 120, 'i_low': 201, 'i_high': 300},
        {'c_low': 121, 'c_high': 250, 'i_low': 301, 'i_high': 400},
        {'c_low': 251, 'c_high': 10000, 'i_low': 401, 'i_high': 500}
    ]
    
    # PM10 breakpoints
    pm10_bp = [
        {'c_low': 0, 'c_high': 50, 'i_low': 0, 'i_high': 50},
        {'c_low': 51, 'c_high': 100, 'i_low': 51, 'i_high': 100},
        {'c_low': 101, 'c_high': 250, 'i_low': 101, 'i_high': 200},
        {'c_low': 251, 'c_high': 350, 'i_low': 201, 'i_high': 300},
        {'c_low': 351, 'c_high': 430, 'i_low': 301, 'i_high': 400},
        {'c_low': 431, 'c_high': 10000, 'i_low': 401, 'i_high': 500}
    ]
    
    pm25_aqi = get_sub_index(pollutants['pm25'], pm25_bp)
    pm10_aqi = get_sub_index(pollutants['pm10'], pm10_bp)
    
    # Overall AQI is the maximum sub-index
    aqi = max(pm25_aqi, pm10_aqi)
    
    # AQI category
    if aqi <= 50:
        category = 'Good'
    elif aqi <= 100:
        category = 'Satisfactory'
    elif aqi <= 200:
        category = 'Moderate'
    elif aqi <= 300:
        category = 'Poor'
    elif aqi <= 400:
        category = 'Very Poor'
    else:
        category = 'Severe'
    
    return round(aqi), category

def generate_weather_data(timestamp):
    """Generate weather data for given timestamp"""
    month = timestamp.month
    hour = timestamp.hour
    
    # Seasonal temperature variation
    base_temp = 15 + 10 * np.sin((month - 1) * np.pi / 6)
    # Diurnal variation
    temp = base_temp + 8 * np.sin((hour - 6) * np.pi / 12) + np.random.normal(0, 2)
    
    # Humidity (inversely related to temperature)
    humidity = 70 - (temp - 15) * 1.5 + np.random.normal(0, 5)
    humidity = np.clip(humidity, 30, 95)
    
    # Wind speed
    wind_speed = abs(np.random.normal(10, 5))
    
    # Wind direction (0-360 degrees)
    wind_direction = random.randint(0, 360)
    
    return {
        'temperature': round(temp, 1),
        'humidity': round(humidity, 1),
        'wind_speed': round(wind_speed, 1),
        'wind_direction': wind_direction,
        'pressure': round(1013 + np.random.normal(0, 5), 1)
    }

def generate_sensor_data():
    """Generate complete sensor dataset"""
    print("Generating ward locations...")
    wards = generate_ward_locations(NUM_WARDS)
    
    print("Generating sensor data...")
    sensor_data = []
    
    current_date = START_DATE
    while current_date <= END_DATE:
        for hour in range(HOURS_PER_DAY):
            timestamp = current_date + timedelta(hours=hour)
            weather = generate_weather_data(timestamp)
            
            for ward in wards:
                ward_id = ward['ward_id']
                source_type, intensity = assign_ward_characteristics(ward_id)
                
                # Calculate pollution levels
                pollutants = calculate_base_pollution(hour, source_type, intensity)
                
                # Weather impact on pollution
                # Lower wind speed = higher pollution accumulation
                wind_factor = 1 + (15 - weather['wind_speed']) * 0.05
                for key in pollutants:
                    pollutants[key] *= wind_factor
                
                # Calculate AQI
                aqi, category = calculate_aqi(pollutants)
                
                # Create record
                record = {
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'ward_id': ward_id,
                    'ward_name': ward['ward_name'],
                    'latitude': ward['latitude'],
                    'longitude': ward['longitude'],
                    'pm25': round(pollutants['pm25'], 2),
                    'pm10': round(pollutants['pm10'], 2),
                    'no2': round(pollutants['no2'], 2),
                    'so2': round(pollutants['so2'], 2),
                    'co': round(pollutants['co'], 2),
                    'o3': round(pollutants['o3'], 2),
                    'aqi': aqi,
                    'aqi_category': category,
                    'temperature': weather['temperature'],
                    'humidity': weather['humidity'],
                    'wind_speed': weather['wind_speed'],
                    'wind_direction': weather['wind_direction'],
                    'pressure': weather['pressure'],
                    'pollution_source': source_type
                }
                
                sensor_data.append(record)
        
        current_date += timedelta(days=1)
        if current_date.day == 1:
            print(f"Generated data up to {current_date.strftime('%Y-%m')}")
    
    return pd.DataFrame(sensor_data), wards

def main():
    print("=== Air Quality Sensor Data Generator ===\n")
    
    # Generate data
    df, wards = generate_sensor_data()
    
    # Save sensor data
    print(f"\nSaving sensor data ({len(df)} records)...")
    df.to_csv('sensor_data.csv', index=False)
    
    # Save ward information
    print("Saving ward information...")
    with open('ward_info.json', 'w') as f:
        json.dump(wards, f, indent=2)
    
    # Generate summary statistics
    print("\n=== Data Summary ===")
    print(f"Total records: {len(df):,}")
    print(f"Number of wards: {NUM_WARDS}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"\nAQI Category Distribution:")
    print(df['aqi_category'].value_counts())
    print(f"\nPollution Source Distribution:")
    print(df['pollution_source'].value_counts())
    print(f"\nAverage AQI by Ward (Top 10 worst):")
    print(df.groupby('ward_name')['aqi'].mean().sort_values(ascending=False).head(10))
    
    print("\n✓ Data generation complete!")
    print("Files saved:")
    print("  - data/sensor_data.csv")
    print("  - data/ward_info.json")

if __name__ == '__main__':
    main()
