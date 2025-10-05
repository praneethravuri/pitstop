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
  - [📰 News &amp; Updates](#-news--updates)
  - [🏁 Session Data](#-session-data)
  - [📊 Telemetry](#-telemetry)
  - [🌤️ Weather](#️-weather)
  - [🚦 Race Control](#-race-control)
- [Setup](#setup)
- [Usage Examples](#usage-examples)
- [Testing with Playground](#testing-with-playground)
- [Project Structure](#project-structure)
- [Development](#development)

## Overview

Pitstop is an MCP server that provides comprehensive Formula 1 data access through Claude Desktop. Built on top of the FastF1 library and RSS feeds, it offers:

✨ **Features**

- 📰 Latest F1 news from multiple trusted sources
- 🔄 Silly season & transfer rumors with smart filtering
- 🏁 Complete session data (practice, qualifying, race)
- 📊 Detailed telemetry & lap-by-lap analysis
- 🌤️ Session weather conditions
- 🚦 Race control messages & incidents
- ⚡ Fast caching for improved performance
- 🎯 Type-safe responses with Pydantic models

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

| Tool Name                     | Category          | Description                                                   |
| ----------------------------- | ----------------- | ------------------------------------------------------------- |
| `get_f1_news`               | 📰 News & Updates | Get F1 news with flexible filtering (general, transfers, management, contracts, silly season) |
| `get_standings`             | 🏆 Championships  | Get driver/constructor championship standings for any season or round |
| `get_session_details`       | 🏁 Session Data   | Get comprehensive details of a specific F1 session            |
| `get_session_results`       | 🏁 Session Data   | Get results/classification from a specific session            |
| `get_laps`                  | 🏁 Session Data   | Get lap data with filtering (all laps, driver laps, fastest laps) |
| `get_session_drivers`       | 🏁 Session Data   | Get list of drivers who participated in a session             |
| `get_tire_strategy`         | 🏁 Session Data   | Get tire strategy and compound usage for a session            |
| `get_lap_telemetry`         | 📊 Telemetry      | Get detailed telemetry data for a specific lap                |
| `compare_driver_telemetry`  | 📊 Telemetry      | Compare telemetry data between two drivers                    |
| `get_session_weather`       | 🌤️ Weather      | Get weather data throughout a session                         |
| `get_race_control_messages` | 🚦 Race Control   | Get official race control messages for a session              |

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

## Testing with Playground

Pitstop includes a comprehensive testing playground (`playground.py`) that lets you test all tools without running the MCP server. This is perfect for:

- **Development** - Test your changes quickly
- **Learning** - Understand how each tool works
- **Debugging** - Isolate and fix issues

### Quick Start

```bash
# Run all tests
python playground.py

# Run specific test functions (edit playground.py)
python playground.py
```

### Available Test Functions

- `test_news()` - Test F1 news with various filters
- `test_standings()` - Test championship standings
- `test_session_data()` - Test session details and results
- `test_laps()` - Test lap data and fastest laps
- `test_tire_strategy()` - Test tire strategy analysis
- `test_telemetry()` - Test telemetry data and comparisons
- `test_weather()` - Test weather data
- `test_race_control()` - Test race control messages

### Example Output

```
==================================================
Testing Championship Standings
==================================================

1. 2024 Driver Standings (top 5):
  1. Max Verstappen - 393 pts
  2. Lando Norris - 331 pts
  3. Charles Leclerc - 307 pts
  ...
```

## Development

### Run Locally

Test the server using the MCP CLI:

```bash
uv run mcp run server.py
```

### Test Tools Directly

Use the provided **playground.py** for interactive testing:

```bash
# Run all tests
python playground.py

# Or test individual tools by editing playground.py
```

Quick command-line tests:

```bash
# Test F1 news
uv run python -c "from tools import get_f1_news; result = get_f1_news(limit=3); print(result.articles[0].title)"

# Test standings
uv run python -c "from tools import get_standings; result = get_standings(2024, type='driver'); print(result.drivers[0].family_name)"

# Test session laps
uv run python -c "from tools import get_laps; laps = get_laps(2024, 'Monaco', 'R', driver='VER', lap_type='fastest'); print(laps['LapTime'])"
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
