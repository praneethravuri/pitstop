# Pitstop 🏎️

Your one-stop shop for Formula 1 data and insights via the Model Context Protocol (MCP).

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![MCP](https://img.shields.io/badge/MCP-1.16.0%2B-green)
![FastF1](https://img.shields.io/badge/FastF1-3.6.1%2B-red)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Available Tools](#available-tools)
  - [Tools Reference Table](#tools-reference-table)
  - [Tool Details](#tool-details)
- [Setup](#setup)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Testing](#testing)

## Overview

Pitstop is an MCP server that provides comprehensive Formula 1 data access through Claude Desktop. Built on top of the FastF1 library and RSS feeds, it offers:

✨ **Features**

- 📰 Latest F1 news from multiple trusted sources
- 📅 Full F1 calendar with schedules and upcoming races
- 🏁 Complete session data (practice, qualifying, race)
- 📊 Detailed telemetry & lap-by-lap analysis
- 📈 Advanced race analysis (pace, tire degradation, consistency)
- 🏎️ Circuit information with corners and track status
- 📚 Driver, team, and circuit reference data
- 🌤️ Session weather conditions
- 🚦 Race control messages & incidents
- ⚡ Fast caching for improved performance
- 🎯 Type-safe responses with Pydantic models

**16 Comprehensive Tools** covering all aspects of F1 data

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
uv sync
```

### Configure Claude Desktop

**Windows:** Edit `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pitstop": {
      "command": "C:\\projects\\pitstop\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "mcp.server.fastmcp",
        "run",
        "C:\\projects\\pitstop\\server.py"
      ]
    }
  }
}
```

**Note:** Adjust paths to match your installation location. Use double backslashes (`\\`) on Windows.

Restart Claude Desktop to activate the tools.

## Available Tools

**🎯 Composable & Generic Tools** - Each tool is designed to handle multiple use cases with flexible parameters, reducing complexity and improving usability.

### Tools Reference Table

All tools return Pydantic models in JSON-serializable format for consistent data exchange.

| Tool Name | Category | Description | Key Parameters | Return Type | Usage |
|-----------|----------|-------------|----------------|-------------|-------|
| `get_f1_news` | 📰 News & Updates | Get F1 news with flexible filtering options | `source` (str), `limit` (int), `category` (str), `filter_text` (str), `date_from` (str), `date_to` (str) | `NewsResponse` | General news, transfer rumors, contracts, technical updates, regulations |
| `get_standings` | 🏆 Championships | Get driver/constructor championship standings | `year` (int), `round` (int\|str), `type` (str), `driver_name` (str), `team_name` (str) | `StandingsResponse` | Find champions, get standings, check positions |
| `get_schedule` | 📅 Schedule | Get F1 calendar and event schedules | `year` (int), `include_testing` (bool), `round` (int), `event_name` (str), `only_remaining` (bool) | `ScheduleResponse` | Full season calendar, upcoming races, testing sessions, event details |
| `get_session_details` | 🏁 Session Data | Get comprehensive session details | `year` (int), `gp` (str\|int), `session` (str), `include_weather` (bool), `include_fastest_lap` (bool) | `SessionDetailsResponse` | Complete session overview with results and weather |
| `get_session_results` | 🏁 Session Data | Get session results/classification | `year` (int), `gp` (str\|int), `session` (str) | `SessionResultsResponse` | Race/qualifying/practice results with driver data |
| `get_laps` | 🏁 Session Data | Get lap data with flexible filtering | `year` (int), `gp` (str\|int), `session` (str), `driver` (str\|int), `lap_type` (str) | `LapsResponse\|FastestLapResponse` | All laps, driver laps, or fastest lap with full data |
| `get_session_drivers` | 🏁 Session Data | Get list of drivers in a session | `year` (int), `gp` (str\|int), `session` (str) | `SessionDriversResponse` | Driver abbreviations who participated |
| `get_tire_strategy` | 🏁 Session Data | Get tire strategy and compound usage | `year` (int), `gp` (str\|int), `session` (str), `driver` (str\|int) | `TireStrategyResponse` | Tire compounds, life, and stint data per lap |
| `get_advanced_session_data` | 🏁 Session Data | Get fastest laps, sector times, pit stops | `year` (int), `gp` (str\|int), `session` (str), `data_type` (str), `driver` (str\|int), `top_n` (int) | `AdvancedSessionDataResponse` | Fastest laps per driver, sector time breakdowns, pit stop analysis |
| `get_lap_telemetry` | 📊 Telemetry | Get detailed telemetry for a specific lap | `year` (int), `gp` (str\|int), `session` (str), `driver` (str\|int), `lap_number` (int) | `LapTelemetryResponse` | High-frequency speed, throttle, brake, gear, RPM, DRS |
| `compare_driver_telemetry` | 📊 Telemetry | Compare telemetry between two drivers | `year` (int), `gp` (str\|int), `session` (str), `driver1` (str\|int), `driver2` (str\|int), `lap1` (int), `lap2` (int) | `TelemetryComparisonResponse` | Side-by-side telemetry comparison for two drivers |
| `get_session_weather` | 🌤️ Weather | Get weather data throughout a session | `year` (int), `gp` (str\|int), `session` (str) | `SessionWeatherDataResponse` | Time-series weather data (temp, humidity, wind, rain) |
| `get_race_control_messages` | 🚦 Race Control | Get official race control messages | `year` (int), `gp` (str\|int), `session` (str) | `RaceControlMessagesResponse` | Flags, safety cars, penalties, investigations |
| `get_reference_data` | 📚 Reference | Get driver, team, circuit, tire metadata | `reference_type` (str), `year` (int), `name` (str) | `ReferenceDataResponse` | Driver info, constructor details, circuit data, tire compounds |
| `get_circuit` | 🏎️ Track & Circuit | Get circuit layout and track status | `year` (int), `gp` (str\|int), `data_type` (str), `session` (str) | `CircuitDataResponse` | Circuit corners, layout, track status changes, flag periods |
| `get_analysis` | 📈 Analysis | Advanced race analysis and insights | `year` (int), `gp` (str\|int), `session` (str), `analysis_type` (str), `driver` (str\|int) | `AnalysisResponse` | Race pace, tire degradation, stint summaries, consistency metrics |

### Tool Details

### 📰 News & Updates

#### `get_f1_news`

Get Formula 1 news with flexible filtering options - a single composable tool for all news needs.

**Parameters:**

- `source` (str, optional): News source - `"formula1"`, `"fia"`, `"autosport"`, `"the-race"`, `"racefans"`, `"planetf1"`, `"motorsport"`, or `"all"` (default: `"formula1"`)
- `limit` (int, optional): Max articles 1-50 (default: `10`)
- `category` (str, optional): News category - `"general"`, `"transfers"`, `"management"`, `"contracts"`, `"silly_season"` (default: `"general"`)
- `driver` (str, optional): Filter by driver name (works with transfers, contracts, silly_season)
- `team` (str, optional): Filter by team name (works with management, contracts, silly_season)
- `year` (int, optional): Filter by year (works with silly_season)

**Returns:** News articles with titles, links, dates, summaries, and sources. Filtered news includes relevance scores.

**Example Prompts:**

```
What's the latest F1 news?
Show me driver transfer rumors
Get contract news about Hamilton
Any management changes at Ferrari?
What's the silly season news for 2025?
Show me all Red Bull silly season news
```

---

### 🏆 Championships

#### `get_standings`

Get F1 World Championship standings for drivers and constructors.

**Parameters:**

- `year` (int): Season year (1950+)
- `round` (int | str, optional): Round number or GP name (e.g., "Monaco", 10)
- `type` (str, optional): `"driver"` or `"constructor"` (default: both)
- `driver_name` (str, optional): Filter by driver name
- `team_name` (str, optional): Filter by team name

**Returns:** Championship standings with positions, points, wins, and nationality.

**Example Prompts:**

```
Who won the 2021 drivers championship?
Show me the 2024 constructor standings
Get standings after Monaco 2024
What's Verstappen's championship position?
```

---

### 🏁 Session Data

#### `get_session_details`

Get comprehensive details of a specific F1 session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name (e.g., "Monza", "Monaco") or round number
- `session` (str): Session type - `"FP1"`, `"FP2"`, `"FP3"`, `"Q"`, `"S"`, `"R"`
- `include_weather` (bool, optional): Include weather data (default: `True`)
- `include_fastest_lap` (bool, optional): Include fastest lap (default: `True`)

**Returns:** Complete session details including results, weather, fastest lap, and session stats.

**Example Prompts:**

```
Give me the session details of free practice 1 of the 2019 Monza GP
Get the race details from the 2024 Monaco GP
Show me qualifying session details for 2023 Silverstone
```

---

#### `get_session_results`

Get results/classification from a specific session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type - `"FP1"`, `"FP2"`, `"FP3"`, `"Q"`, `"S"`, `"R"`

**Returns:** Session results with positions, driver info, times, teams, and status.

**Example Prompts:**

```
Get the race results from the 2024 Monaco Grand Prix
Show me qualifying results from 2023 Singapore
What were the FP1 results for the 2024 Bahrain GP?
```

---

#### `get_laps`

Get lap data from an F1 session with flexible filtering - a single composable tool for all lap queries.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type - `"FP1"`, `"FP2"`, `"FP3"`, `"Q"`, `"S"`, `"R"`
- `driver` (str | int, optional): Driver identifier - 3-letter code or number (default: all drivers)
- `lap_type` (str, optional): `"all"` or `"fastest"` (default: `"all"`)

**Returns:** Lap data with times, sectors, tire compounds, track status, and speed data.

**Example Prompts:**

```
Get all laps from the 2024 Monza race
Show me Verstappen's laps in Monaco 2024
What was the fastest lap in qualifying?
Get Hamilton's fastest lap from the race
```

---

#### `get_session_drivers`

Get list of drivers who participated in a session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type

**Returns:** List of driver identifiers who participated.

**Example Prompts:**

```
Which drivers participated in the 2024 Monza race?
Show me all drivers from FP1 at Monaco 2024
```

---

#### `get_tire_strategy`

Get tire strategy and compound usage for a session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `driver` (str | int, optional): Driver identifier (if None, returns all drivers)

**Returns:** Tire data per lap including compound, tire life, and stint information.

**Example Prompts:**

```
What was the tire strategy in the 2024 Monza race?
Show me Verstappen's tire strategy for the Monaco race
Analyze tire usage in qualifying at Singapore 2023
```

---

### 📊 Telemetry

#### `get_lap_telemetry`

Get detailed telemetry data for a specific lap.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `driver` (str | int): Driver identifier
- `lap_number` (int): Specific lap number

**Returns:** High-frequency telemetry including speed, throttle, brake, gear, RPM, and DRS.

**Example Prompts:**

```
Get telemetry for Verstappen's lap 15 in the 2024 Monza race
Show me Hamilton's fastest lap telemetry from Monaco qualifying
Analyze Leclerc's lap 10 telemetry from Singapore 2023
```

---

#### `compare_driver_telemetry`

Compare telemetry data between two drivers.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `driver1` (str | int): First driver identifier
- `driver2` (str | int): Second driver identifier
- `lap1` (int, optional): Lap number for driver1 (uses fastest if None)
- `lap2` (int, optional): Lap number for driver2 (uses fastest if None)

**Returns:** Tuple of telemetry DataFrames for side-by-side comparison.

**Example Prompts:**

```
Compare the telemetry between Verstappen and Hamilton in 2024 Monza qualifying
Compare Leclerc and Sainz fastest laps from Monaco 2024
Show me telemetry comparison for lap 20 between VER and NOR at Silverstone
```

---

### 🌤️ Weather

#### `get_session_weather`

Get weather data throughout a session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type

**Returns:** Weather data including air/track temps, humidity, pressure, wind, and rainfall.

**Example Prompts:**

```
What was the weather like during the 2024 Spa race?
Show me weather conditions for Monaco qualifying 2024
Get weather data from FP1 at Singapore 2023
```

---

### 🚦 Race Control

#### `get_race_control_messages`

Get official race control messages for a session.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type

**Returns:** Race control messages including flags, safety car periods, investigations, and penalties.

**Example Prompts:**

```
What race control messages were issued during the 2024 Monaco race?
Show me all flags and safety car periods from Spa 2024
Get race control messages from Singapore qualifying 2023
```

---

### 📅 Schedule

#### `get_schedule`

Get comprehensive F1 calendar and schedule information.

**Parameters:**

- `year` (int): Season year
- `include_testing` (bool, optional): Include testing events (default: True)
- `round` (int, optional): Get details for specific round
- `event_name` (str, optional): Filter by event name
- `only_remaining` (bool, optional): Only show upcoming events (default: False)

**Returns:** Complete schedule with event details, session dates, and locations.

**Example Prompts:**

```
What's the 2024 F1 calendar?
Show me upcoming races this season
Get details for the Monaco Grand Prix 2024
When is the next race?
Show me all testing sessions for 2024
```

---

### 📚 Reference

#### `get_reference_data`

Get F1 reference data including driver, team, circuit, and tire information.

**Parameters:**

- `reference_type` (str): Type - 'driver', 'constructor', 'circuit', 'tire_compounds'
- `year` (int, optional): Season year for driver/constructor data
- `name` (str, optional): Filter by name

**Returns:** Reference metadata in structured format.

**Example Prompts:**

```
Get all drivers from 2024
Show me Verstappen's driver information
What teams competed in 2024?
Get circuit information for Monaco
Show me tire compound information
Get Red Bull team details
```

---

### 🏎️ Track & Circuit

#### `get_circuit`

Get comprehensive circuit and track information.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `data_type` (str): 'circuit_info' for layout/corners, 'track_status' for flags
- `session` (str, optional): Session type (required for track_status)

**Returns:** Circuit layout, corners, track status changes, and flag periods.

**Example Prompts:**

```
Get Monaco circuit information
Show me the corners at Silverstone
What was the track status during the Monaco race?
Get track status changes in qualifying
Show me all flag periods from the race
```

---

### 🏁 Advanced Session Data

#### `get_advanced_session_data`

Get advanced session data including fastest laps, sector times, and pit stops.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `data_type` (str): 'fastest_laps', 'sector_times', or 'pit_stops'
- `driver` (str | int, optional): Driver filter
- `top_n` (int, optional): Limit results to top N

**Returns:** Advanced session analysis data.

**Example Prompts:**

```
Get fastest laps from Monaco qualifying
Show me sector times for all drivers
Get Verstappen's pit stops in the race
Show me the top 5 fastest laps
Get Hamilton's sector times in qualifying
Analyze pit stop strategy in the race
```

---

### 📈 Analysis

#### `get_analysis`

Get advanced race analysis including pace, tire degradation, and consistency.

**Parameters:**

- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `analysis_type` (str): 'race_pace', 'tire_degradation', 'stint_summary', or 'consistency'
- `driver` (str | int, optional): Driver filter

**Returns:** Advanced analysis and insights.

**Example Prompts:**

```
Analyze race pace for Monaco 2024
Show me tire degradation in the race
Get stint summaries for all drivers
Analyze Verstappen's consistency in qualifying
Compare tire degradation between drivers
Show me average pace excluding pit stops
```

---

## Setup

### 1. Install Dependencies

```bash
uv sync
```

This installs:

- **FastF1** - Formula 1 data access
- **feedparser** - RSS feed parsing
- **MCP** - Model Context Protocol
- **Pydantic** - Data validation
- **httpx** - HTTP client

### 2. Configure Claude Desktop

Add the following to your Claude Desktop config:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pitstop": {
      "command": "[ABSOLUTE PATH TO uv]\\.local\\bin\\uv.EXE",
        "args": [
          "run",
          "--directory",
          [ABSOLUTE PATH TO PROJECT]\\pitstop",
          "mcp",
          "run",
          "[ABSOLUTE PATH TO PROJECT]\\pitstop\\server.py"
        ]
    }
  }
}
```

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

## Usage Examples

Once configured, you can use Pitstop through Claude Desktop with natural language:

**News & Updates:**

```
What's the latest F1 news?
Show me transfer rumors about Hamilton
Any contract news for McLaren?
```

**Session Analysis:**

```
Give me the session details of free practice 1 of the 2019 Monza GP
What was the tire strategy in the 2024 Monaco race?
Show me qualifying results from 2023 Singapore
```

**Telemetry & Performance:**

```
Compare the telemetry between Verstappen and Hamilton in qualifying
Get Leclerc's fastest lap data from the Monaco race
Show me the weather during the 2024 Spa race
```

**Race Control:**

```
What penalties were given in the Monaco race?
Show me all safety car periods from the 2024 season
```

## Development

### Run Locally

Test the server using the MCP CLI:

```bash
uv run mcp run server.py
```

## Testing

Each tool can be tested individually using its built-in test function. All tools include a `if __name__ == "__main__"` block for standalone testing.

### Test Individual Tools

```bash
# Test news tool
python tools/media/news.py

# Test standings
python tools/standings/standings.py

# Test session results
python tools/session/results.py

# Test telemetry
python tools/telemetry/lap_telemetry.py

# Test any other tool by running its Python file directly
```

### Quick Command-Line Tests

```bash
# Test F1 news
python -c "from tools.media.news import get_f1_news; news = get_f1_news(limit=3); print(news.articles[0].title)"

# Test standings
python -c "from tools.standings.standings import get_standings; result = get_standings(2024, type='driver'); print(f'{result.drivers[0].given_name} {result.drivers[0].family_name}')"

# Test session laps
python -c "from tools.session.laps import get_laps; laps = get_laps(2024, 'Monaco', 'R', driver='VER', lap_type='fastest'); print(laps['LapTime'])"
```

### Cache Management

FastF1 caches data in `cache/` for performance. To clear:

```bash
# Unix/macOS
rm -rf cache/

# Windows
rmdir /s cache
```

## Troubleshooting

**Import Errors:**

- Run `uv sync` to install dependencies
- Verify Python 3.13+ is installed

**Connection Issues:**

- Check paths in Claude Desktop config are correct
- Ensure double backslashes on Windows
- Restart Claude Desktop after config changes

**Data Issues:**

- Clear cache if data seems corrupted
- Verify year is 2018+ for session data
- Check that Grand Prix names are spelled correctly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - Excellent Formula 1 data library
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- F1 community for open data support

---

Built with ❤️ for F1 fans and data enthusiasts
