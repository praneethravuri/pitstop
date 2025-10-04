from mcp.server.fastmcp import FastMCP
from tools import (
    driver_standings,
    f1_news,
    silly_season_news,
    driver_transfer_rumors,
    team_management_changes,
    contract_news,
    latest_f1_news,
    get_race_calendar,
    get_race_weekend_schedule,
    get_next_race,
    get_race_results,
    get_qualifying_results,
    get_sprint_results,
    get_fastest_laps,
    get_session_results,
    get_driver_race_performance,
    get_session_weather,
    get_race_weekend_news,
    get_practice_reports,
    get_qualifying_reports,
    get_race_reports,
    get_race_highlights,
)

mcp = FastMCP(name="Pitstop")

# Driver and standings tools
mcp.tool()(driver_standings)

# News and updates tools
mcp.tool()(f1_news)
mcp.tool()(latest_f1_news)

# Silly season tools
mcp.tool()(silly_season_news)
mcp.tool()(driver_transfer_rumors)
mcp.tool()(team_management_changes)
mcp.tool()(contract_news)

# Race weekend schedule tools
mcp.tool()(get_race_calendar)
mcp.tool()(get_race_weekend_schedule)
mcp.tool()(get_next_race)

# Race results and performance tools
mcp.tool()(get_race_results)
mcp.tool()(get_qualifying_results)
mcp.tool()(get_sprint_results)
mcp.tool()(get_fastest_laps)
mcp.tool()(get_session_results)
mcp.tool()(get_driver_race_performance)
mcp.tool()(get_session_weather)

# Race weekend news tools
mcp.tool()(get_race_weekend_news)
mcp.tool()(get_practice_reports)
mcp.tool()(get_qualifying_reports)
mcp.tool()(get_race_reports)
mcp.tool()(get_race_highlights)