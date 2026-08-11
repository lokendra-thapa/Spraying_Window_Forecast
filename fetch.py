import os
from datetime import datetime, timedelta
from pathlib import Path
import requests
import numpy as np


def load_local_env():
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        return

    with env_path.open('r', encoding='utf-8') as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_api_url():
    load_local_env()
    api_url = os.getenv('API_URL')
    if not api_url:
        raise RuntimeError(
            'API_URL is not configured. Create a local .env file or set the API_URL environment variable.'
        )
    return api_url


def fetch_weather_forecast(latitude, longitude):
    """
    Fetch forecast by making a POST request to the API with
    longitude and latitude in the request body.
    
    Args:
        latitude (float): The latitude coordinate
        longitude (float): The longitude coordinate
    
    Returns:
        list: List of forecast data points
    """
    API_URL = get_api_url()

    # Payload to send in the POST request body
    payload = {
        "longitude": longitude,
        "latitude": latitude
    }

    try:
        # Make a POST request with form-data (x-www-form-urlencoded)
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract the hourly forecast array
        hourly_data = data.get("hourly_parameters", [])
        
        # Convert the API data into the structure your visualization needs
        forecast_data = []
        for entry in hourly_data:
            forecast_data.append({
                'time': entry['datetime'],   
                'temperature': entry['air_temperature'],
                'wind_speed': entry['wind_speed'],
                'precipitation': entry['hourly_rainfall']
            })

    except Exception as e:
        print("Error fetching forecast from API:", e)
        forecast_data = []
    
    return forecast_data
