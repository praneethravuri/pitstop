from mcp.server.fastmcp import FastMCP
from tools import driver_standings, f1_news

mcp = FastMCP(name="Pitstop")

mcp.tool()(driver_standings)
mcp.tool()(f1_news)