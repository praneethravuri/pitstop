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
  - [📰 News & Updates](#-news--updates)
  - [🏁 Session Data](#-session-data)
  - [📊 Telemetry](#-telemetry)
  - [🌤️ Weather](#️-weather)
  - [🚦 Race Control](#-race-control)
- [Setup](#setup)
- [Usage Examples](#usage-examples)
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

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `f1_news` | 📰 News & Updates | Get latest F1 news from trusted RSS feeds |
| `latest_f1_news` | 📰 News & Updates | Get latest F1 news from multiple sources |
| `silly_season_news` | 📰 News & Updates | Get F1 silly season news including transfers and rumors |
| `driver_transfer_rumors` | 📰 News & Updates | Get latest driver transfer rumors and speculation |
| `team_management_changes` | 📰 News & Updates | Get news about team management changes |
| `contract_news` | 📰 News & Updates | Get contract-related news (renewals, extensions, expirations) |
| `get_session_details` | 🏁 Session Data | Get comprehensive details of a specific F1 session |
| `get_session_results` | 🏁 Session Data | Get results/classification from a specific session |
| `get_session_laps` | 🏁 Session Data | Get all laps from a specific session |
| `get_driver_laps` | 🏁 Session Data | Get all laps for a specific driver in a session |
| `get_fastest_lap` | 🏁 Session Data | Get the fastest lap from a session |
| `get_session_drivers` | 🏁 Session Data | Get list of drivers who participated in a session |
| `get_tire_strategy` | 🏁 Session Data | Get tire strategy and compound usage for a session |
| `get_lap_telemetry` | 📊 Telemetry | Get detailed telemetry data for a specific lap |
| `compare_driver_telemetry` | 📊 Telemetry | Compare telemetry data between two drivers |
| `get_session_weather` | 🌤️ Weather | Get weather data throughout a session |
| `get_race_control_messages` | 🚦 Race Control | Get official race control messages for a session |

### 📰 News & Updates

#### `f1_news`
Get the latest Formula 1 news from trusted RSS feeds.

**Parameters:**
- `source` (str, optional): News source - `"formula1"`, `"fia"`, `"autosport"`, `"the-race"`, `"racefans"`, `"planetf1"`, `"motorsport"`, or `"all"` (default: `"formula1"`)
- `limit` (int, optional): Max articles 1-50 (default: `10`)

**Returns:** News articles with titles, links, publication dates, summaries, and source information.

**Example Prompts:**
```
What's the latest F1 news?
Show me the top 5 articles from Autosport
Get me 20 F1 news articles from all sources
```

---

#### `latest_f1_news`
Get the latest Formula 1 news from multiple sources.

**Parameters:**
- `source` (str, optional): News source (default: `"all"`)
- `limit` (int, optional): Max articles 1-50 (default: `15`)

**Returns:** Latest news from all sources including race results, driver announcements, and team updates.

**Example Prompts:**
```
What happened in F1 this week?
Any breaking F1 news today?
```

---

#### `silly_season_news`
Get F1 silly season news including driver transfers, team changes, and rumors.

**Parameters:**
- `year` (int, optional): Filter by year (e.g., 2024, 2025)
- `driver` (str, optional): Filter by driver name (e.g., "Hamilton", "Verstappen")
- `constructor` (str, optional): Filter by team name (e.g., "Ferrari", "Red Bull")
- `limit` (int, optional): Max articles 1-50 (default: `20`)

**Returns:** Silly season articles with relevance scores, sorted by relevance.

**Example Prompts:**
```
What's the latest silly season news?
Show me driver transfer rumors for 2025
Any silly season news about Ferrari?
```

---

#### `driver_transfer_rumors`
Get the latest driver transfer rumors and speculation.

**Parameters:**
- `driver` (str, optional): Filter by driver name
- `limit` (int, optional): Max articles 1-50 (default: `15`)

**Returns:** Transfer-related news including rumored moves, confirmed signings, and negotiations.

**Example Prompts:**
```
Are there any transfer rumors about Lewis Hamilton?
What are the latest rumors about Carlos Sainz?
Show me all driver transfer rumors
```

---

#### `team_management_changes`
Get news about team management changes.

**Parameters:**
- `constructor` (str, optional): Filter by team name
- `limit` (int, optional): Max articles 1-50 (default: `15`)

**Returns:** Management news including appointments, resignations, and team restructuring.

**Example Prompts:**
```
Any management changes at Ferrari?
Show me recent team principal appointments
What management changes happened at Red Bull?
```

---

#### `contract_news`
Get contract-related news including renewals, extensions, and expirations.

**Parameters:**
- `driver` (str, optional): Filter by driver name
- `constructor` (str, optional): Filter by team name
- `limit` (int, optional): Max articles 1-50 (default: `15`)

**Returns:** Contract news including extensions, renewals, and multi-year deals.

**Example Prompts:**
```
Which driver contracts are expiring soon?
Show me contract extension news for Lando Norris
Any contract news for McLaren?
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

#### `get_session_laps`
Get all laps from a specific session.

**Parameters:**
- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type

**Returns:** All laps with lap times, sectors, tire compounds, and track status.

**Example Prompts:**
```
Get all laps from the 2024 Monza race
Show me lap data from qualifying at Monaco 2024
```

---

#### `get_driver_laps`
Get all laps for a specific driver in a session.

**Parameters:**
- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `driver` (str | int): Driver identifier - 3-letter code (e.g., "VER") or number (e.g., 1)

**Returns:** Driver's laps with timing data, sectors, compounds, and more.

**Example Prompts:**
```
Get all laps for Verstappen in the 2024 Monza race
Show me Hamilton's qualifying laps from Monaco 2024
What were Leclerc's lap times in FP1 at Singapore 2023?
```

---

#### `get_fastest_lap`
Get the fastest lap from a session.

**Parameters:**
- `year` (int): Season year (2018+)
- `gp` (str | int): Grand Prix name or round number
- `session` (str): Session type
- `driver` (str | int, optional): Driver identifier (if None, returns overall fastest)

**Returns:** Fastest lap data including driver, time, lap number, and compound.

**Example Prompts:**
```
Who set the fastest lap in the 2024 Monza qualifying?
Get Verstappen's fastest lap from the 2024 Monaco race
What was the fastest lap in FP2 at Singapore 2023?
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
      "command": "C:\\projects\\pitstop\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp.server.fastmcp", "run", "C:\\projects\\pitstop\\server.py"]
    }
  }
}
```

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "pitstop": {
      "command": "/path/to/pitstop/.venv/bin/python",
      "args": ["-m", "mcp.server.fastmcp", "run", "/path/to/pitstop/server.py"]
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

## Project Structure

```
pitstop/
├── server.py                          # MCP server entry point
├── clients/                           # API clients
│   ├── fastf1_client.py              # FastF1 core functions
│   └── rss_client.py                 # RSS feed aggregator
├── tools/                            # Tool implementations
│   ├── news_and_updates/
│   │   ├── general/                 # General F1 news
│   │   │   ├── f1_news.py
│   │   │   └── latest_news.py
│   │   └── silly_season/            # Transfer & contract news
│   │       ├── filters.py           # Keyword filtering logic
│   │       ├── general_news.py
│   │       ├── transfers.py
│   │       ├── management.py
│   │       └── contracts.py
│   ├── sessions/                    # Session data tools
│   │   ├── session_details.py
│   │   ├── results.py
│   │   ├── laps.py
│   │   ├── drivers.py
│   │   └── tire_strategy.py
│   ├── telemetry/                   # Telemetry analysis
│   │   ├── lap_telemetry.py
│   │   └── compare.py
│   ├── weather/                     # Weather data
│   │   └── session_weather.py
│   └── race_control/                # Race control messages
│       └── messages.py
├── models/                          # Pydantic data models
│   ├── news_and_updates/
│   │   ├── general.py
│   │   └── silly_season.py
│   └── sessions/
│       └── session_details.py
└── utils/                           # Utility functions
    ├── date_validator.py
    └── text_cleaner.py
```

## Development

### Run Locally

Test the server using the MCP CLI:

```bash
uv run mcp run server.py
```

### Test Tools Directly

```bash
# Test F1 news
uv run python -c "from tools import f1_news; result = f1_news('autosport', 3); print(result.articles[0].title)"

# Test session details
uv run python -c "from tools import get_session_details; result = get_session_details(2019, 'Monza', 'FP1'); print(result.session_info.name)"

# Test telemetry comparison
uv run python -c "from tools import compare_driver_telemetry; tel1, tel2 = compare_driver_telemetry(2024, 'Monaco', 'Q', 'VER', 'HAM'); print('Telemetry compared')"
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
