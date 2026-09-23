import os
import requests

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

        current["precipitation_probability"] = (
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