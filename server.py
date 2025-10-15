from mcp.server.fastmcp import FastMCP
from tools import (
    # Session
    get_session_details,
    get_session_results,
    get_laps,
    get_session_drivers,
    get_tire_strategy,
    get_advanced_session_data,
    get_qualifying_sessions,
    get_track_evolution,
    # Telemetry
    get_lap_telemetry,
    compare_driver_telemetry,
    # Weather
    get_session_weather,
    # Control
    get_race_control_messages,
    get_penalties,
    get_investigations,
    get_flag_history,
    # Standings
    get_standings,
    # Media
    get_f1_news,
    # Schedule
    get_schedule,
    # Reference
    get_reference_data,
    # Track
    get_circuit,
    # Analysis
    get_analysis,
    # Live (OpenF1)
    get_driver_radio,
    get_live_pit_stops,
    get_live_intervals,
    get_meeting_info,
    get_stints_live,
    # Forecast (Weather)
    get_race_weather_forecast,
    get_session_forecast,
    get_rain_probability,
)

mcp = FastMCP(name="Pitstop")

# Session tools
mcp.tool()(get_session_details)
mcp.tool()(get_session_results)
mcp.tool()(get_laps)
mcp.tool()(get_session_drivers)
mcp.tool()(get_tire_strategy)
mcp.tool()(get_advanced_session_data)
mcp.tool()(get_qualifying_sessions)
mcp.tool()(get_track_evolution)

# Telemetry tools
mcp.tool()(get_lap_telemetry)
mcp.tool()(compare_driver_telemetry)

# Weather tools
mcp.tool()(get_session_weather)

# Control tools
mcp.tool()(get_race_control_messages)
mcp.tool()(get_penalties)
mcp.tool()(get_investigations)
mcp.tool()(get_flag_history)

# Standings tools
mcp.tool()(get_standings)

# Media tools
mcp.tool()(get_f1_news)

# Schedule tools
mcp.tool()(get_schedule)

# Reference tools
mcp.tool()(get_reference_data)

# Track tools
mcp.tool()(get_circuit)

# Analysis tools
mcp.tool()(get_analysis)

# Live tools (OpenF1)
mcp.tool()(get_driver_radio)
mcp.tool()(get_live_pit_stops)
mcp.tool()(get_live_intervals)
mcp.tool()(get_meeting_info)
mcp.tool()(get_stints_live)

# Forecast tools (Weather)
mcp.tool()(get_race_weather_forecast)
mcp.tool()(get_session_forecast)
mcp.tool()(get_rain_probability)