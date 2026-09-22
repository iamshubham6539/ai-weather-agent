from mcp.server.mcpserver import MCPServer
from app.weather import resolve_location, fetch_weather
from app.sop import match_sops, select_sop

mcp = MCPServer("weather-advisory")

@mcp.tool()
def get_weather(city: str) -> dict:
    location_result = resolve_location(city)

    if "error" in location_result:
        return location_result

    return fetch_weather(location_result["location"])

@mcp.tool()
def get_weather_advisory(city: str, activity: str) -> dict:
    location_result = resolve_location(city)

    if "error" in location_result:
        return location_result

    weather_result = fetch_weather(location_result["location"])

    if "error" in weather_result:
        return weather_result

    weather = weather_result["weather"]
    matches = match_sops(activity, weather)
    selection = select_sop(matches)

    return {
        "city": location_result["location"]["city"],
        "weather": weather,
        "matched_sops": [sop["id"] for sop in matches],
        "selected_sop": selection["selected_sop"],
        "decision": selection["decision"]
    }

if __name__ == "__main__":
    mcp.run()