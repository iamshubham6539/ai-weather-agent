from app.sop import match_sops, select_sop

def test_cycling_high_wind():
    weather = {
        "wind_speed_10m": 45,
        "precipitation": 0,
        "uv_index": 0,
        "weather_code": 3
    }

    matches = match_sops("cycling", weather)
    result = select_sop(matches)

    assert result["selected_sop"]["id"] == "CYCLING_WIND_01"
    assert result["decision"]["decision"] == "restricted"

def test_cycling_moderate_wind():
    weather = {
        "wind_speed_10m": 30,
        "precipitation": 0,
        "uv_index": 0,
        "weather_code": 3
    }

    matches = match_sops("cycling", weather)
    result = select_sop(matches)

    assert result["selected_sop"]["id"] == "CYCLING_WIND_02"
    assert result["decision"]["decision"] == "caution"

def test_thunderstorm_priority():
    weather = {
        "wind_speed_10m": 45,
        "precipitation": 0,
        "uv_index": 0,
        "weather_code": 95
    }

    matches = match_sops("cycling", weather)
    result = select_sop(matches)

    assert result["selected_sop"]["id"] == "OUTDOOR_THUNDERSTORM_01"
    assert result["decision"]["decision"] == "prohibited"

def test_normal_cycling():
    weather = {
        "wind_speed_10m": 10,
        "precipitation": 0,
        "uv_index": 0,
        "weather_code": 3
    }

    matches = match_sops("cycling", weather)
    result = select_sop(matches)

    assert result["selected_sop"]["id"] == "CYCLING_NORMAL_01"
    assert result["decision"]["decision"] == "allowed"