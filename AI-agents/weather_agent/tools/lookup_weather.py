import requests
from weather_agent.config import GEOCODE_URL, WEATHER_REQUEST_TIMEOUT,FORECAST_URL

def lookup_weather(location:str)->str:
    try:
        geo = requests.get(GEOCODE_URL, params={"name": location, "count": 1}, timeout=WEATHER_REQUEST_TIMEOUT)
        geo.raise_for_status()
        geo_data = geo.json().get("results")

        if not geo_data:
            print("Location not found.")
            return ""   

        place = geo_data[0]
        lat,lng = place.get("latitude"), place.get("longitude")

        label = ", ".join(
            part for part in [place.get("name"),place.get("country")] if part
        )

        forecast = requests.get(FORECAST_URL, params={"latitude": lat, "longitude": lng, "current": "temperature_2m,weather_code,wind_speed_10m"}, timeout=WEATHER_REQUEST_TIMEOUT)
        forecast.raise_for_status()
        current = forecast.json().get("current")
        temperature = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        wind_speed = current.get("wind_speed_10m")
        # print(current)
        return f"Temperature: {temperature}, Weather Code: {weather_code}, Wind Speed: {wind_speed}"
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching weather data: {e}")
        return ""

print(lookup_weather("Australia"))