"""
Pitstop F1 MCP Server
====================

A comprehensive Formula 1 data server using the Model Context Protocol.
100% FREE - No API keys required!

Data Sources:
- FastF1: Session data, telemetry, historical weather (2018-present)
- OpenF1 API: Real-time timing, radio, pit stops (2023-present)
- Ergast API: Historical data (1950-2024)
- RSS Feeds: News from 12+ outlets

Total Tools: 24 | All Free & Open Source
"""

from mcp.server.fastmcp import FastMCP

# Import all tools organized by category
from tools import (
    # ========================================
    # CORE SESSION DATA
    # ========================================
    get_session_details,          # Complete session overview
    get_session_results,           # Final classification
    get_laps,                      # Lap-by-lap data
    get_session_drivers,           # Driver list
    get_tire_strategy,             # Tire compounds and stints
    get_advanced_session_data,     # Fastest laps, sectors, pit stops
    get_qualifying_sessions,       # Q1/Q2/Q3 splits
    get_track_evolution,           # Lap time progression

    # ========================================
    # TELEMETRY & ANALYSIS
    # ========================================
    get_lap_telemetry,             # High-frequency telemetry data
    compare_driver_telemetry,      # Side-by-side comparison
    get_analysis,                  # Race pace, tire deg, stints
    get_session_weather,           # Historical weather data

    # ========================================
    # RACE CONTROL & TRACK
    # ========================================
    get_race_control_messages,     # Flags, penalties, investigations, safety car
    get_circuit,                   # Circuit layout and corners

    # ========================================
    # LIVE TIMING - OpenF1
    # ========================================
    get_driver_radio,              # Team radio messages
    get_live_pit_stops,            # Pit stop timing
    get_live_intervals,            # Gaps and intervals
    get_meeting_info,              # Session schedule
    get_stints_live,               # Real-time tire stints

    # ========================================
    # CHAMPIONSHIP & SCHEDULE
    # ========================================
    get_standings,                 # Driver/constructor standings
    get_schedule,                  # F1 calendar

    # ========================================
    # REFERENCE & MEDIA
    # ========================================
    get_reference_data,            # Drivers, teams, circuits, tires
    get_f1_news,                   # News from 12+ sources
)

# Initialize MCP server
mcp = FastMCP(
    name="Pitstop",
    description="Formula 1 data via MCP - 100% free, no API keys required"
)


# ============================================================================
# REGISTER TOOLS
# ============================================================================

# Core Session Data
mcp.tool()(get_session_details)
mcp.tool()(get_session_results)
mcp.tool()(get_laps)
mcp.tool()(get_session_drivers)
mcp.tool()(get_tire_strategy)
mcp.tool()(get_advanced_session_data)
mcp.tool()(get_qualifying_sessions)
mcp.tool()(get_track_evolution)

# Telemetry & Analysis
mcp.tool()(get_lap_telemetry)
mcp.tool()(compare_driver_telemetry)
mcp.tool()(get_analysis)
mcp.tool()(get_session_weather)

# Race Control & Track
mcp.tool()(get_race_control_messages)
mcp.tool()(get_circuit)

# Live Timing (OpenF1)
mcp.tool()(get_driver_radio)
mcp.tool()(get_live_pit_stops)
mcp.tool()(get_live_intervals)
mcp.tool()(get_meeting_info)
mcp.tool()(get_stints_live)

# Championship & Schedule
mcp.tool()(get_standings)
mcp.tool()(get_schedule)

# Reference & Media
mcp.tool()(get_reference_data)
mcp.tool()(get_f1_news)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
