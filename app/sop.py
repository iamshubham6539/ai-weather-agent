import yaml

def load_sops():
    with open("sops/policies.yaml", "r") as file:
        data = yaml.safe_load(file)

    return data["sops"]

def detect_weather_events(weather: dict):
    weather_code = weather.get("weather_code")

    if weather_code in [95, 96, 99]:
        return ["thunderstorm"]

    return []

def match_sops(activity: str, weather: dict):
    if activity == "cycle":
        activity = "cycling"

    sops = load_sops()
    matched_sops = []
    weather_events = detect_weather_events(weather)

    for sop in sops:
        sop_activity = sop["activity"]
        condition = sop["condition"]

        if condition.get("type") == "weather_event":
            if condition["event"] in weather_events:
                if sop_activity == "all_outdoor":
                    matched_sops.append(sop)

            continue

        if sop_activity != activity:
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

    return matched_sops

def evaluate_sops(sop_matches: list):
    if not sop_matches:
        return {
            "decision": "no_guidance",
            "reason": "No applicable SOP applies."
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
        "sop_id": selected_sop["id"],
        "severity": selected_sop["severity"]
    }

def select_sop(sop_matches: list):
    decision = evaluate_sops(sop_matches)

    if decision["decision"] == "no_guidance":
        return {
            "selected_sop": {},
            "decision": decision
        }

    selected_sop = next(
        sop for sop in sop_matches
        if sop["id"] == decision["sop_id"]
    )

    return {
        "selected_sop": selected_sop,
        "decision": decision
    }