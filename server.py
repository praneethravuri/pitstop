from mcp.server.fastmcp import FastMCP
from tools import get_f1_driver_standings

mcp = FastMCP(name="Pitstop")

mcp.tool()(get_f1_driver_standings)