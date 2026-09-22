from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class WeatherState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    request_context: dict
    location: dict
    weather: dict
    sop_matches: list
    selected_sop: dict
    decision: dict
    response: str
    error: str | None