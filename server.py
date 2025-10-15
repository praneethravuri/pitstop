from mcp.server.fastmcp import FastMCP
from tools import (
    # Session
    get_session_details,
    get_session_results,
    get_laps,
    get_session_drivers,
    get_tire_strategy,
    get_advanced_session_data,
    # Telemetry
    get_lap_telemetry,
    compare_driver_telemetry,
    # Weather
    get_session_weather,
    # Control
    get_race_control_messages,
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
)

mcp = FastMCP(name="Pitstop")

# Session tools
mcp.tool()(get_session_details)
mcp.tool()(get_session_results)
mcp.tool()(get_laps)
mcp.tool()(get_session_drivers)
mcp.tool()(get_tire_strategy)
mcp.tool()(get_advanced_session_data)

# Telemetry tools
mcp.tool()(get_lap_telemetry)
mcp.tool()(compare_driver_telemetry)

# Weather tools
mcp.tool()(get_session_weather)

# Control tools
mcp.tool()(get_race_control_messages)

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