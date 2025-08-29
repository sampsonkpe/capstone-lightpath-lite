import requests
from django.conf import settings

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_current_weather(city: str = None):
    """
    Fetch current weather for a given city.
    Defaults to settings.DEFAULT_CITY if city not provided.
    """
    if city is None:
        city = getattr(settings, "DEFAULT_CITY", "Accra")

    url = f"{OPENWEATHER_BASE_URL}/weather"
    params = {
        "q": city,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_weather_forecast(lat: float, lon: float):
    """
    Fetch 7-day weather forecast for a given latitude and longitude.
    """
    url = f"{OPENWEATHER_BASE_URL}/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly,alerts",
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
