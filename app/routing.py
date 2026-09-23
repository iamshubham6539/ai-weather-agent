from .state import WeatherState

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

def route_after_sop_selection(state: WeatherState):
    if state["decision"]["decision"] == "no_guidance":
        return "no_sop_response"

    return "generate_response"