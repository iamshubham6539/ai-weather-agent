# Weather Advisory Support Bot

A weather-aware advisory system built using LangGraph, LangChain, Hugging Face, Open-Meteo, YAML-based SOPs, MCP and Streamlit.

## Architecture

User
↓
LangGraph
↓
Request Understanding
↓
Location Resolution
↓
Live Weather
↓
SOP Matching
↓
SOP Selection
↓
Response Generation
↓
User

## Features

- Natural language request understanding
- Live weather data using Open-Meteo
- Location resolution using Open-Meteo geocoding
- YAML-based safety SOPs
- Multiple activity categories
- Multiple severity levels
- Weather-event SOPs
- Deterministic SOP matching
- Severity-based conflict resolution
- LangGraph session memory
- MCP tools
- Evaluation dataset
- Automated SOP tests
- Streamlit interface

## Activities

- Cycling
- Hiking
- Water activities

## Weather Inputs

- Temperature
- Wind speed
- Precipitation
- Precipitation probability
- UV index
- Weather code

## Safety Design

The LLM does not determine safety rules.

The system follows:

Weather Data
→ Deterministic SOP Matching
→ SOP Selection
→ LLM Response Formatting

Safety policies are stored separately in:

sops/policies.yaml

This allows policy changes without modifying the weather or LLM code.

## Run

Install dependencies:

pip install -r requirements.txt

Run the LangGraph application:

python -m app.graph

Run evaluation:

python evaluation/evaluate.py

Run tests:

pytest

Run Streamlit:

streamlit run ui/app.py

Run MCP:

python mcp/server.py