import requests

def resolve_location(city: str):
    if not city:
        return {"error": "Could not determine the location."}

    if city.lower() == "bangalore":
        city = "Bengaluru"

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 10,
        "language": "en",
        "format": "json",
        "countryCode": "IN"
    }

    try:
        result = requests.get(url, params=params, timeout=10)
        result.raise_for_status()
        data = result.json()

        if not data.get("results"):
            return {"error": f"Could not resolve location: {city}"}

        place = data["results"][0]

        return {
            "location": {
                "city": place["name"],
                "latitude": place["latitude"],
                "longitude": place["longitude"]
            }
        }

    except requests.RequestException:
        return {"error": "Location service is unavailable."}

def fetch_weather(location: dict):
    if not location:
        return {"error": "Location is unavailable."}

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "wind_speed_10m,"
            "precipitation,"
            "precipitation_probability,"
            "uv_index,"
            "weather_code"
        )
    }

    try:
        result = requests.get(url, params=params, timeout=10)
        result.raise_for_status()
        data = result.json()

        if not data.get("current"):
            return {"error": "Weather data is unavailable."}

        return {"weather": data["current"]}

    except requests.RequestException:
        return {"error": "Weather service is unavailable."}

def detect_weather_events(weather: dict):
    weather_code = weather.get("weather_code")

    if weather_code in [95, 96, 99]:
        return ["thunderstorm"]

    return []