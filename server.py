from mcp.server.fastmcp import FastMCP
from tools import (
    driver_standings,
    f1_news,
    silly_season_news,
    driver_transfer_rumors,
    team_management_changes,
    contract_news,
    latest_f1_news,
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