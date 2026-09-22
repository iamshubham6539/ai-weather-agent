from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from typing import TypedDict
import json
import yaml

load_dotenv()

llm= HuggingFaceEndpoint(
    model="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    provider="auto"
)

model= ChatHuggingFace(llm=llm)

class WeatherState(TypedDict):
    messages:str
    user_query:str
    request_context:dict
    location:dict
    weather:dict
    sop_matches:list
    selected_sop:dict
    decision:dict
    response:str
    error:str | None

def understand_request(state: WeatherState):
    query = state["user_query"]

    prompt = f"""
Extract the following from the user's question:
- activity
- location
- time
- user_group

Return the result inside a JSON object.

User question: {query}
"""

    try:
        response = model.invoke(prompt)

        print("\n===== LLM RESPONSE =====")
        print(response.content)
        print("========================\n")

    except Exception as e:
        print("\n===== LLM ERROR =====")
        print(e)
        print("=====================\n")

        return {
            "error": f"LLM service is unavailable: {e}"
        }

    try:
        text = response.content

        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            return {
                "error": "Could not understand the user's request."
            }

        json_text = text[start:end]

        request_context = json.loads(json_text)

        return {
            "request_context": request_context
        }

    except (json.JSONDecodeError, TypeError):
        return {
            "error": "Could not understand the user's request."
        }

import requests


def resolve_location(state: WeatherState):

    city = state["request_context"].get("location")

    if city.lower() == "bangalore":
        city = "Bengaluru"

    if not city:
        return {"error": "Could not determine the location."}

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
        print("\n===== GEOCODING RESPONSE =====")
        print(data)
        print("===============================\n")

        if not data.get("results"):
            return {"error": f"Could not resolve location: {city}"}

        results = data["results"]

        place = results[0]

        return {
            "location": {
                "city": place["name"],
                "latitude": place["latitude"],
                "longitude": place["longitude"]
            }
        }

    except requests.RequestException:
        return {"error": "Location service is unavailable."}

def fetch_weather(state: WeatherState):

    location = state["location"]

    if not location:
        return {
            "error": "Location is unavailable."
        }

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "wind_speed_10m,"
            "precipitation,"
            "precipitation_probability,"
            "uv_index"
        )
    }

    try:
        result = requests.get(
            url,
            params=params,
            timeout=10
        )

        result.raise_for_status()

        data = result.json()

        if not data.get("current"):
            return {
                "error": "Weather data is unavailable."
            }

        return {
            "weather": data["current"]
        }

    except requests.RequestException:
        return {
            "error": "Weather service is unavailable."
        }

def load_sops():
    with open("sops/policies.yaml", "r") as file:
        data = yaml.safe_load(file)

    return data["sops"]

sops = load_sops()
print("\n===== SOPs LOADED =====")
print(len(sops))
print("=======================\n")

def match_sops(state: WeatherState):

    request_context = state["request_context"]
    weather = state["weather"]

    activity = request_context.get("activity")

    if activity == "cycle":
        activity = "cycling"

    sops = load_sops()

    matched_sops = []

    for sop in sops:

        if sop["activity"] != activity:
            continue

        condition = sop["condition"]

        if condition.get("type") == "weather_event":
            continue

        field = condition["field"]
        operator = condition["operator"]
        threshold = condition["value"]

        actual_value = weather.get(field)

        if actual_value is None:
            continue

        if operator == ">" and actual_value > threshold:
            matched_sops.append(sop)

        elif operator == "<" and actual_value < threshold:
            matched_sops.append(sop)

        elif operator == ">=" and actual_value >= threshold:
            matched_sops.append(sop)

        elif operator == "<=" and actual_value <= threshold:
            matched_sops.append(sop)

        elif operator == "==" and actual_value == threshold:
            matched_sops.append(sop)

    return {
        "sop_matches": matched_sops
    }

def evaluate_sops(sop_matches):

    if not sop_matches:
        return {
            "decision": "no_guidance",
            "reason": "No applicable SOP found."
        }

    severity_priority = {
        "low": 1,
        "moderate": 2,
        "high": 3,
        "critical": 4
    }

    selected_sop = max(
        sop_matches,
        key=lambda sop: severity_priority.get(sop["severity"], 0)
    )

    return {
        "decision": selected_sop["decision"],
        "reason": selected_sop["guidance"],
        "sop_id": selected_sop["id"]
    }

def select_sop(state: WeatherState):

    sop_matches = state["sop_matches"]

    if not sop_matches:
        return {"selected_sop": {}}

    # Selection strategy will be implemented
    # after we define severity/priorities.

    selected_sop = sop_matches[0]

    return {"selected_sop": selected_sop}

def generate_response(state: WeatherState):

    sop = state["selected_sop"]
    weather = state["weather"]
    query = state["user_query"]

    prompt = f"""Answer the user's question using ONLY the supplied SOP and weather data.
    User question:{query} Weather:{weather} SOP: {sop}
    Do not invent safety advice.
    Do not invent weather values.
    """
    result = model.invoke(prompt)
    return {"response": result.content}

def no_sop_response(state: WeatherState):

    return {"response": "I don't have guidance for this situation."}

def error_response(state: WeatherState):

    return {"response": f"I couldn't provide a weather-based advisory. {state['error']}"}


graph = StateGraph(WeatherState)

graph.add_node("understand_request", understand_request)
graph.add_node("resolve_location", resolve_location)
graph.add_node("fetch_weather", fetch_weather)
graph.add_node("match_sops", match_sops)
graph.add_node("select_sop", select_sop)
graph.add_node("generate_response", generate_response)
graph.add_node("no_sop_response", no_sop_response)
graph.add_node("error_response", error_response)

def route_after_understanding(state: WeatherState):
    if state.get("error"):
        return "error_response"

    return "resolve_location"


def route_after_location(state: WeatherState):
    if state.get("error"):
        return "error_response"

    return "fetch_weather"


def route_after_weather(state: WeatherState):
    if state.get("error"):
        return "error_response"

    return "match_sops"


def route_after_sop_matching(state: WeatherState):
    if not state["sop_matches"]:
        return "no_sop_response"

    return "select_sop"


graph.add_edge(START, "understand_request")

graph.add_conditional_edges(
    "understand_request",
    route_after_understanding
)

graph.add_conditional_edges(
    "resolve_location",
    route_after_location
)

graph.add_conditional_edges(
    "fetch_weather",
    route_after_weather
)

graph.add_conditional_edges(
    "match_sops",
    route_after_sop_matching
)

graph.add_edge(
    "select_sop",
    "generate_response"
)

graph.add_edge(
    "generate_response",
    END
)

graph.add_edge(
    "no_sop_response",
    END
)

graph.add_edge(
    "error_response",
    END
)

app = graph.compile()

result = app.invoke({
    "messages": "",
    "user_query": "Is it safe to cycle in Bangalore today?",
    "request_context": {},
    "location": {},
    "weather": {},
    "sop_matches": [],
    "selected_sop": {},
    "decision": {},
    "response": "",
    "error": None
})

print(result)


test_sops = load_sops()

test_matches = [
    sop for sop in test_sops
    if sop["id"] in [
        "CYCLING_WIND_01",
        "CYCLING_WIND_02"
    ]
]

print("\n===== SOP EVALUATION TEST =====")
print(evaluate_sops(test_matches))
print("===============================\n")