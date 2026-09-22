import json
from .llm import model
from .weather import resolve_location, fetch_weather
from .sop import match_sops, select_sop
from .state import WeatherState

def understand_request(state: WeatherState):
    query = state["user_query"]
    history = state.get("messages", [])

    history_text = "\n".join(
        f"{type(message).__name__}: {message.content}"
        for message in history
    )

    prompt = f"""
Extract the following from the user's question:
- activity
- location
- time
- user_group

Use the conversation history to resolve missing information.
If the current question does not specify a location or time, reuse it from the conversation history.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.
Do not include comments.
Do not add text before or after the JSON.

Use null when a field is unknown.

Example:
{{
  "activity": "cycling",
  "location": "Bangalore",
  "time": "today",
  "user_group": null
}}

Conversation history:
{history_text}

Current user question:
{query}
"""

    try:
        response = model.invoke(prompt)
        text = response.content
        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            return {"error": "Could not understand the user's request."}

        request_context = json.loads(text[start:end])

        return {
            "request_context": request_context,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }

    except Exception:
        return {
            "error": "Could not understand the user's request."
        }

def resolve_location_node(state: WeatherState):
    city = state["request_context"].get("location")
    return resolve_location(city)

def fetch_weather_node(state: WeatherState):
    return fetch_weather(state["location"])

def match_sops_node(state: WeatherState):
    activity = state["request_context"].get("activity")
    weather = state["weather"]
    matches = match_sops(activity, weather)

    return {
        "sop_matches": matches
    }

def select_sop_node(state: WeatherState):
    return select_sop(state["sop_matches"])

def generate_response(state: WeatherState):
    sop = state["selected_sop"]
    weather = state["weather"]
    query = state["user_query"]
    history = state.get("messages", [])

    history_text = "\n".join(
        f"{type(message).__name__}: {message.content}"
        for message in history
    )

    prompt = f"""
Answer the user's question using ONLY the supplied SOP and weather data.

Conversation history:
{history_text}

Current user question:
{query}

Weather:
{weather}

SOP:
{sop}

Do not invent safety advice.
Do not invent weather values.
Do not introduce safety rules not present in the SOP.
Base the decision only on the selected SOP.
Give a concise answer.
"""

    try:
        result = model.invoke(prompt)

        return {
            "response": result.content,
            "messages": [
                {
                    "role": "assistant",
                    "content": result.content
                }
            ]
        }

    except Exception as e:
        return {
            "error": f"Response generation failed: {e}"
        }

def no_sop_response(state: WeatherState):
    weather = state["weather"]

    response = (
        "No applicable SOP applies to the current weather conditions. "
        f"Current weather: temperature {weather.get('temperature_2m')}°C, "
        f"wind {weather.get('wind_speed_10m')} km/h, "
        f"precipitation {weather.get('precipitation')} mm, "
        f"UV index {weather.get('uv_index')}."
    )

    return {
        "response": response,
        "messages": [
            {
                "role": "assistant",
                "content": response
            }
        ]
    }

def error_response(state: WeatherState):
    response = (
        f"I couldn't provide a weather-based advisory. "
        f"{state['error']}"
    )

    return {
        "response": response,
        "messages": [
            {
                "role": "assistant",
                "content": response
            }
        ]
    }