import os
import requests

HEADERS={"User-Agent":"weather-advisory-support-bot/1.0"}

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
        response=requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()
        data=response.json()
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

def fetch_weather(location:dict):
    if not location:
        return {"error":"Location is unavailable."}

    latitude=location.get("latitude")
    longitude=location.get("longitude")

    if latitude is None or longitude is None:
        return {"error":"Invalid location coordinates."}

    proxy_url=os.getenv("WEATHER_PROXY_URL")
    proxy_token=os.getenv("WEATHER_PROXY_TOKEN")

    if not proxy_url or not proxy_token:
        return {"error":"Weather proxy is not configured."}

    try:
        response=requests.get(
            proxy_url,
            params={
                "latitude":latitude,
                "longitude":longitude
            },
            headers={
                "Authorization":f"Bearer {proxy_token}"
            },
            timeout=20
        )

        response.raise_for_status()
        data=response.json()

        current=data.get("current")

        if not current:
            return {"error":"Weather API returned no current weather data."}

        hourly=data.get("hourly",{})
        probabilities=hourly.get("precipitation_probability",[])

        current["precipitation_probability"]=(
            probabilities[0] if probabilities else None
        )

        return {"weather":current}

    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code==401:
            return {"error":"Weather proxy authentication failed."}

        if e.response is not None and e.response.status_code==429:
            return {"error":"Weather provider rate limit reached."}

        return {"error":f"Weather API error: {e}"}

    except requests.RequestException as e:
        return {"error":f"Weather service is unavailable: {e}"}

def detect_weather_events(weather:dict):
    weather_code=weather.get("weather_code")

    if weather_code in [95,96,99]:
        return ["thunderstorm"]

    return []