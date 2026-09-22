import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from app.graph import app

st.set_page_config(page_title="Weather Advisory",page_icon="🌦️",layout="wide")

st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.block-container{max-width:900px;padding-top:2rem;padding-bottom:7rem}
.hero{text-align:center;margin-top:15vh}
.hero h1{font-size:42px;margin-bottom:8px}
.hero p{color:#888;font-size:18px}
.chips{display:flex;gap:10px;justify-content:center;margin:25px 0}
.chip{padding:10px 16px;border:1px solid #444;border-radius:20px;color:#bbb}
.weather-card{padding:20px;border-radius:18px;background:#1c1f26;border:1px solid #30343d;margin:12px 0}
.metric{font-size:26px;font-weight:600}
.label{font-size:13px;color:#888}
.advisory{padding:18px;border-radius:16px;background:#20242c;border-left:4px solid #ff9f1c;margin-top:12px}
.sop{font-size:13px;color:#888;margin-top:10px}
.error{padding:18px;border-radius:16px;background:#20242c;border-left:4px solid #ff4b4b;margin-top:12px}
</style>
""",unsafe_allow_html=True)

if "thread_id" not in st.session_state:
    st.session_state.thread_id="streamlit_user"

if "messages" not in st.session_state:
    st.session_state.messages=[]

if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h1>🌦️ Weather Advisory</h1>
        <p>Ask about outdoor activities and get live weather-based guidance.</p>
    </div>
    <div class="chips">
        <div class="chip">🚴 Cycling</div>
        <div class="chip">🥾 Hiking</div>
        <div class="chip">🏄 Water activities</div>
    </div>
    """,unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"]=="assistant" and "data" in message:
            data=message["data"]
            weather=data.get("weather",{})
            sop=data.get("sop")
            response=message.get("content","")
            if weather:
                st.markdown(
                    f"""
                    <div class="weather-card">
                        <b>📍 {data.get("city","Unknown location")}</b>
                        <div style="display:flex;gap:45px;margin-top:18px">
                            <div><div class="metric">{weather.get("temperature_2m","N/A")}°C</div><div class="label">Temperature</div></div>
                            <div><div class="metric">{weather.get("wind_speed_10m","N/A")} km/h</div><div class="label">Wind</div></div>
                            <div><div class="metric">{weather.get("precipitation","N/A")} mm</div><div class="label">Rain</div></div>
                            <div><div class="metric">{weather.get("uv_index","N/A")}</div><div class="label">UV Index</div></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown(
                f"""
                <div class="advisory">
                    <b>Weather Advisory</b><br><br>
                    {response}
                    <div class="sop">SOP: {sop or "No applicable SOP"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.write(message.get("content",""))

query=st.chat_input("Ask about cycling, hiking or water activities...")

if query:
    st.session_state.messages.append({"role":"user","content":query})

    with st.chat_message("user"):
        st.write(query)

    config={"configurable":{"thread_id":st.session_state.thread_id}}

    with st.chat_message("assistant"):
        with st.spinner("Checking live weather and SOPs..."):
            result=app.invoke({
                "messages":[],
                "user_query":query,
                "request_context":{},
                "location":{},
                "weather":{},
                "sop_matches":[],
                "selected_sop":{},
                "decision":{},
                "response":"",
                "error":None
            },config=config)

        weather=result.get("weather",{})
        location=result.get("location",{})
        decision=result.get("decision",{})
        selected=result.get("selected_sop",{})
        response=result.get("response","")
        error=result.get("error")

        if weather:
            st.markdown(
                f"""
                <div class="weather-card">
                    <b>📍 {location.get("city","Unknown location")}</b>
                    <div style="display:flex;gap:45px;margin-top:18px">
                        <div><div class="metric">{weather.get("temperature_2m","N/A")}°C</div><div class="label">Temperature</div></div>
                        <div><div class="metric">{weather.get("wind_speed_10m","N/A")} km/h</div><div class="label">Wind</div></div>
                        <div><div class="metric">{weather.get("precipitation","N/A")} mm</div><div class="label">Rain</div></div>
                        <div><div class="metric">{weather.get("uv_index","N/A")}</div><div class="label">UV Index</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if error:
            st.markdown(
                f"""
                <div class="error">
                    <b>Weather Advisory</b><br><br>
                    {response}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="advisory">
                    <b>Weather Advisory</b><br><br>
                    {response}
                    <div class="sop">
                        SOP: {selected.get("id","No applicable SOP")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.session_state.messages.append({
            "role":"assistant",
            "content":response,
            "data":{
                "city":location.get("city","Unknown location"),
                "weather":weather,
                "decision":decision,
                "sop":selected.get("id")
            }
        })