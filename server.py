from mcp.server.fastmcp import FastMCP
from tools import (
    # Session
    get_session_details,
    get_session_results,
    get_laps,
    get_session_drivers,
    get_tire_strategy,
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
)

mcp = FastMCP(name="Pitstop")

# Session tools
mcp.tool()(get_session_details)
mcp.tool()(get_session_results)
mcp.tool()(get_laps)
mcp.tool()(get_session_drivers)
mcp.tool()(get_tire_strategy)

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