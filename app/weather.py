import time
import requests

HEADERS={"User-Agent":"weather-advisory-support-bot/1.0"}

def _get(url,params):
    last_error=None
    for attempt in range(3):
        try:
            response=requests.get(url,params=params,headers=HEADERS,timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            last_error=e
            if attempt<2:
                time.sleep(1.5*(attempt+1))
    raise last_error

def resolve_location(city:str):
    if not city:
        return {"error":"Could not determine the location."}
    if city.lower().strip()=="bangalore":
        city="Bengaluru"
    url="https://geocoding-api.open-meteo.com/v1/search"
    params={
        "name":city,
        "count":10,
        "language":"en",
        "format":"json",
        "countryCode":"IN"
    }
    try:
        data=_get(url,params)
        results=data.get("results",[])
        if not results:
            return {"error":f"Could not resolve location: {city}"}
        place=results[0]
        return {
            "location":{
                "city":place["name"],
                "latitude":place["latitude"],
                "longitude":place["longitude"]
            }
        }
    except requests.RequestException as e:
        return {"error":f"Location service is unavailable: {e}"}
    except (KeyError,TypeError,ValueError) as e:
        return {"error":f"Invalid location response: {e}"}

def fetch_weather(location:dict):
    if not location:
        return {"error":"Location is unavailable."}

    lat=location.get("latitude")
    lon=location.get("longitude")

    if lat is None or lon is None:
        return {"error":"Invalid location coordinates."}

    url="https://api.open-meteo.com/v1/forecast"

    current_params={
        "latitude":lat,
        "longitude":lon,
        "current":"temperature_2m,wind_speed_10m,precipitation,uv_index,weather_code",
        "timezone":"auto"
    }

    try:
        data=_get(url,current_params)
        current=data.get("current")

        if not current:
            return {"error":"Weather API returned no current weather data."}

        probability_params={
            "latitude":lat,
            "longitude":lon,
            "hourly":"precipitation_probability",
            "forecast_hours":1,
            "timezone":"auto"
        }

        try:
            probability_data=_get(url,probability_params)
            hourly=probability_data.get("hourly",{})
            probabilities=hourly.get("precipitation_probability",[])
            current["precipitation_probability"]=probabilities[0] if probabilities else None
        except requests.RequestException:
            current["precipitation_probability"]=None

        return {"weather":current}

    except requests.RequestException as e:
        try:
            fallback_params={
                "latitude":lat,
                "longitude":lon,
                "hourly":"temperature_2m,wind_speed_10m,precipitation,precipitation_probability,uv_index,weather_code",
                "forecast_hours":1,
                "timezone":"auto"
            }

            fallback=_get(url,fallback_params)
            hourly=fallback.get("hourly",{})

            required=[
                "temperature_2m",
                "wind_speed_10m",
                "precipitation",
                "precipitation_probability",
                "uv_index",
                "weather_code"
            ]

            if not all(hourly.get(field) for field in required):
                return {"error":f"Weather API returned incomplete data: {e}"}

            weather={
                field:hourly[field][0]
                for field in required
            }

            return {"weather":weather}

        except requests.RequestException as fallback_error:
            return {
                "error":f"Weather service is unavailable. Primary: {e}. Fallback: {fallback_error}"
            }

def detect_weather_events(weather:dict):
    weather_code=weather.get("weather_code")
    if weather_code in [95,96,99]:
        return ["thunderstorm"]
    return []