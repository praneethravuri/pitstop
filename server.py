from mcp.server.fastmcp import FastMCP
from tools import (
    # News and updates
    f1_news,
    latest_f1_news,
    silly_season_news,
    driver_transfer_rumors,
    team_management_changes,
    contract_news,
    # Sessions
    get_session_details,
    get_session_results,
    get_session_laps,
    get_driver_laps,
    get_fastest_lap,
    get_session_drivers,
    get_tire_strategy,
    # Telemetry
    get_lap_telemetry,
    compare_driver_telemetry,
    # Weather
    get_session_weather,
    # Race Control
    get_race_control_messages,
)

mcp = FastMCP(name="Pitstop")

# News and updates tools
mcp.tool()(f1_news)
mcp.tool()(latest_f1_news)
mcp.tool()(silly_season_news)
mcp.tool()(driver_transfer_rumors)
mcp.tool()(team_management_changes)
mcp.tool()(contract_news)

# Session tools
mcp.tool()(get_session_details)
mcp.tool()(get_session_results)
mcp.tool()(get_session_laps)
mcp.tool()(get_driver_laps)
mcp.tool()(get_fastest_lap)
mcp.tool()(get_session_drivers)
mcp.tool()(get_tire_strategy)

# Telemetry tools
mcp.tool()(get_lap_telemetry)
mcp.tool()(compare_driver_telemetry)

# Weather tools
mcp.tool()(get_session_weather)

# Race control tools
mcp.tool()(get_race_control_messages)