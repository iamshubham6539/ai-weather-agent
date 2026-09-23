from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import WeatherState

from .nodes import (
    understand_request,
    resolve_location_node,
    fetch_weather_node,
    match_sops_node,
    select_sop_node,
    generate_response,
    no_sop_response,
    error_response
)

from .routing import (
    route_after_understanding,
    route_after_location,
    route_after_weather,
    route_after_sop_selection
)

graph = StateGraph(WeatherState)

graph.add_node("understand_request", understand_request)
graph.add_node("resolve_location", resolve_location_node)
graph.add_node("fetch_weather", fetch_weather_node)
graph.add_node("match_sops", match_sops_node)
graph.add_node("select_sop", select_sop_node)
graph.add_node("generate_response", generate_response)
graph.add_node("no_sop_response", no_sop_response)
graph.add_node("error_response", error_response)

graph.add_edge(START, "understand_request")
graph.add_conditional_edges("understand_request",route_after_understanding)
graph.add_conditional_edges("resolve_location",route_after_location)
graph.add_conditional_edges("fetch_weather",route_after_weather)
graph.add_edge("match_sops","select_sop")
graph.add_conditional_edges("select_sop",route_after_sop_selection)
graph.add_edge("generate_response",END)
graph.add_edge("no_sop_response",END)
graph.add_edge("error_response",END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "user_1"
        }
    }

    first_result = app.invoke(
        {
            "messages": [],
            "user_query": "Is it safe to cycle in Bangalore today?",
            "request_context": {},
            "location": {},
            "weather": {},
            "sop_matches": [],
            "selected_sop": {},
            "decision": {},
            "response": "",
            "error": None
        },
        config=config
    )

    print("\nFIRST RESPONSE")
    print(first_result["response"])

    second_result = app.invoke(
        {
            "messages": [],
            "user_query": "What about hiking?",
            "request_context": {},
            "location": {},
            "weather": {},
            "sop_matches": [],
            "selected_sop": {},
            "decision": {},
            "response": "",
            "error": None
        },
        config=config
    )

    print("\nSECOND RESPONSE")
    print(second_result["response"])

    print("\nMESSAGES")
    print(second_result["messages"])