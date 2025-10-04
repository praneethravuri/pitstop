from mcp.server.fastmcp import FastMCP
from tools import driver_standings

mcp = FastMCP(name="Pitstop")

mcp.tool()(driver_standings)