# Pitstop 🏎️

> **Comprehensive Formula 1 data via Model Context Protocol (MCP) for Claude Desktop**

![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue) ![MCP](https://img.shields.io/badge/MCP-1.16.0%2B-green) ![FastF1](https://img.shields.io/badge/FastF1-3.6.1%2B-red) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
uv sync
```

### Set Up Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API keys (at minimum, add OPENWEATHER_API_KEY for forecast tools)
# Get free key at: https://openweathermap.org/appid
```

### Configure Claude Desktop

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pitstop": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/pitstop",
        "mcp",
        "run",
        "/absolute/path/to/pitstop/server.py"
      ]
    }
  }
}
```

**Note:** Replace `/absolute/path/to/pitstop` with your installation path. Use double backslashes (`\\`) on Windows.

Restart Claude Desktop to activate.

---

## 📊 Data Sources

| Source                   | Coverage       | Data Types                                           | Status    |
| ------------------------ | -------------- | ---------------------------------------------------- | --------- |
| **FastF1**         | 2018-present   | Session data, telemetry, weather, race control       | ✅ Active |
| **Ergast API**     | 1950-2024      | Historical results, standings, driver/team info      | ✅ Active |
| **RSS Feeds**      | Real-time      | News from 12+ outlets (F1.com, FIA, Autosport, etc.) | ✅ Active |
| **OpenF1 API**     | 2023-present   | Real-time radio, pit stops, intervals                | ✅ Active |
| **OpenWeatherMap** | 5-day forecast | Weather predictions for race weekends                | ✅ Active |

---

## 🛠️ Available Tools (30 Implemented)

| Tool                           | Category      | Description                                                              | Key Parameters                                                                   | Use Cases                                                 |
| ------------------------------ | ------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Session Data**         |               |                                                                          |                                                                                  |                                                           |
| `get_session_details`        | 🏁 Session    | Complete session overview with results, weather, fastest lap             | `year`, `gp`, `session`, `include_weather`, `include_fastest_lap`      | Session summary, race overview, practice analysis         |
| `get_session_results`        | 🏁 Session    | Final classification/results for any session                             | `year`, `gp`, `session`                                                    | Race/qualifying/practice results, driver positions        |
| `get_laps`                   | 🏁 Session    | Lap-by-lap data with filtering (all/driver/fastest)                      | `year`, `gp`, `session`, `driver?`, `lap_type?`                        | All laps, driver-specific laps, fastest lap analysis      |
| `get_session_drivers`        | 🏁 Session    | List of drivers in session                                               | `year`, `gp`, `session`                                                    | Who participated in session                               |
| `get_tire_strategy`          | 🏁 Session    | Tire compound usage and stint data per driver                            | `year`, `gp`, `session`, `driver?`                                       | Tire strategy analysis, compound usage                    |
| `get_advanced_session_data`  | 🏁 Session    | Fastest laps, sector times, pit stops                                    | `year`, `gp`, `session`, `data_type`, `driver?`, `top_n?`            | Sector analysis, pit stop timing, fastest laps per driver |
| `get_qualifying_sessions`    | 🏁 Session    | Split qualifying into Q1/Q2/Q3 segments                                  | `year`, `gp`, `segment?`                                                   | Q1/Q2/Q3 analysis, qualifying progression                 |
| `get_track_evolution`        | 🏁 Session    | Track lap time improvement through session                               | `year`, `gp`, `session`, `max_laps?`                                     | Practice evolution, track rubbering in                    |
| **Telemetry**            |               |                                                                          |                                                                                  |                                                           |
| `get_lap_telemetry`          | 📊 Telemetry  | High-frequency telemetry (speed, throttle, brake, gear, RPM, DRS)        | `year`, `gp`, `session`, `driver`, `lap_number`                        | Detailed lap analysis, corner speed, braking points       |
| `compare_driver_telemetry`   | 📊 Telemetry  | Side-by-side telemetry comparison between drivers                        | `year`, `gp`, `session`, `driver1`, `driver2`, `lap1?`, `lap2?`    | Driver comparison, performance delta analysis             |
| **Weather**              |               |                                                                          |                                                                                  |                                                           |
| `get_session_weather`        | 🌤️ Weather  | Historical weather data throughout session                               | `year`, `gp`, `session`                                                    | Air/track temp, humidity, wind, rainfall during session   |
| `get_race_weather_forecast`  | 🌤️ Forecast | 5-day weather forecast for race weekend                                  | `circuit`, `latitude?`, `longitude?`                                       | Race weekend weather prediction, rain probability         |
| `get_session_forecast`       | 🌤️ Forecast | Hourly forecast for specific session window                              | `circuit`, `session_datetime`, `hours_before?`, `hours_after?`           | Qualifying/race session forecast, 3h windows              |
| `get_rain_probability`       | 🌤️ Forecast | Rain probability timeline with filtered forecasts                        | `circuit`, `start_datetime?`, `end_datetime?`                              | Rain likelihood, precipitation tracking                   |
| **Race Control**         |               |                                                                          |                                                                                  |                                                           |
| `get_race_control_messages`  | 🚦 Control    | All race control messages (flags, safety car, investigations, penalties) | `year`, `gp`, `session`                                                    | Incident timeline, flag periods, safety car               |
| `get_penalties`              | 🚦 Control    | Filter for penalty decisions only                                        | `year`, `gp`, `session`                                                    | Time penalties, grid drops, warnings                      |
| `get_investigations`         | 🚦 Control    | Filter for investigation notices                                         | `year`, `gp`, `session`                                                    | Incidents under investigation                             |
| `get_flag_history`           | 🚦 Control    | All flag periods (yellow, red, safety car, VSC)                          | `year`, `gp`, `session`                                                    | Flag timeline, safety car periods                         |
| **Standings & Schedule** |               |                                                                          |                                                                                  |                                                           |
| `get_standings`              | 🏆 Standings  | Driver/constructor championship standings                                | `year`, `round?`, `type?`, `driver_name?`, `team_name?`                | Championship positions, points, wins                      |
| `get_schedule`               | 📅 Schedule   | F1 calendar with sessions, testing, upcoming races                       | `year`, `include_testing?`, `round?`, `event_name?`, `only_remaining?` | Season calendar, next race, testing sessions              |
| **Reference Data**       |               |                                                                          |                                                                                  |                                                           |
| `get_reference_data`         | 📚 Reference  | Driver info, team details, circuit metadata, tire compounds              | `reference_type`, `year?`, `name?`                                         | Driver/team/circuit information, tire specs               |
| **Track & Circuit**      |               |                                                                          |                                                                                  |                                                           |
| `get_circuit`                | 🏎️ Track    | Circuit layout, corners, track status, flag periods                      | `year`, `gp`, `data_type`, `session?`                                    | Circuit info, corner analysis, track status changes       |
| **Analysis**             |               |                                                                          |                                                                                  |                                                           |
| `get_analysis`               | 📈 Analysis   | Race pace, tire degradation, stint summaries, consistency metrics        | `year`, `gp`, `session`, `analysis_type`, `driver?`                    | Advanced race analysis, pace comparison, tire wear        |
| **News & Media**         |               |                                                                          |                                                                                  |                                                           |
| `get_f1_news`                | 📰 News       | F1 news from 12+ sources with filtering                                  | `source?`, `limit?`, `category?`, `driver?`, `team?`, `year?`        | Latest news, transfer rumors, contracts, silly season     |
| **Live Data (OpenF1)**   |               |                                                                          |                                                                                  |                                                           |
| `get_driver_radio`           | 📻 Live       | Team radio messages with audio transcripts                               | `year`, `country`, `session_name?`, `driver_number?`                     | Radio communications, team messages                       |
| `get_live_pit_stops`         | ⚡ Live       | Pit stop analysis with crew timing                                       | `year`, `country`, `session_name?`, `driver_number?`                     | Pit stop duration, fastest/slowest stops                  |
| `get_live_intervals`         | ⚡ Live       | Real-time gaps and intervals between drivers                             | `year`, `country`, `session_name?`, `driver_number?`                     | Gap to leader, interval to car ahead                      |
| `get_meeting_info`           | ⚡ Live       | Meeting and session schedule with precise times                          | `year`, `country`                                                            | Race weekend schedule, session keys, start times          |
| `get_stints_live`            | ⚡ Live       | Real-time tire stint tracking with compounds                             | `year`, `country`, `session_name?`, `driver_number?`, `compound?`      | Tire strategy tracking, stint analysis                    |

**Parameter Conventions:**

- `year`: Season year (2018+ for FastF1, 1950+ for Ergast, 2023+ for OpenF1)
- `gp`: Grand Prix name (e.g., "Monaco", "Silverstone") or round number
- `session`: Session type - `"FP1"`, `"FP2"`, `"FP3"`, `"Q"`, `"S"`, `"R"`
- `driver`: 3-letter code (e.g., "VER") or driver number
- `?` suffix: Optional parameter

---

## 💡 Usage Examples

```
# Session Analysis
"Get qualifying results from Monaco 2024"
"What was Verstappen's tire strategy in the race?"
"Show me sector times for all drivers"

# Telemetry
"Compare telemetry between Verstappen and Hamilton in qualifying"
"Get Leclerc's fastest lap data"

# Weather
"What's the weather forecast for Silverstone?"
"Show me weather during the 2024 Spa race"

# Race Control
"What penalties were given in Monaco?"
"Show me all investigations from the race"

# Live Data
"Get team radio messages from the race"
"Show me pit stop times for all drivers"
"What was the gap between Verstappen and Hamilton?"

# News & Schedule
"What's the latest F1 news?"
"When is the next race?"
"Show me transfer rumors about Hamilton"
```

---

## ⚙️ Configuration

### Environment Variables

Some tools require API keys to function. Set them up using a `.env` file:

#### 1. Create .env file

```bash
# Copy the example file
cp .env.example .env
```

#### 2. Edit .env and add your API keys

```bash
# Pitstop F1 MCP Server - Environment Variables

# ==========================================
# WEATHER FORECASTING (Required for forecast tools)
# ==========================================
# Get your free API key at: https://openweathermap.org/appid
# Free tier: 1,000 calls/day, 60 calls/minute
OPENWEATHER_API_KEY=your_openweathermap_api_key_here

# ==========================================
# FUTURE API KEYS (Not yet required)
# ==========================================
# REDDIT_CLIENT_ID=your_reddit_client_id
# REDDIT_CLIENT_SECRET=your_reddit_client_secret
# YOUTUBE_API_KEY=your_youtube_api_key
# ODDS_API_KEY=your_odds_api_key
```

#### Required API Keys

| API Key                 | Required For                                                                                               | Free Tier       | Get Key At                                                |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- | --------------- | --------------------------------------------------------- |
| `OPENWEATHER_API_KEY` | Weather forecast tools (`get_race_weather_forecast`, `get_session_forecast`, `get_rain_probability`) | 1,000 calls/day | [openweathermap.org/appid](https://openweathermap.org/appid) |

#### Optional Future API Keys

| API Key                                         | Future Use                | Free Tier          | Get Key At                                                                 |
| ----------------------------------------------- | ------------------------- | ------------------ | -------------------------------------------------------------------------- |
| `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` | Community sentiment tools | Yes                | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)                    |
| `YOUTUBE_API_KEY`                             | Video content tools       | 10,000 units/day   | [console.cloud.google.com](https://console.cloud.google.com/apis/credentials) |
| `ODDS_API_KEY`                                | Betting odds tools        | 500 requests/month | [the-odds-api.com](https://the-odds-api.com/)                                 |

**Notes:**

- Tools gracefully handle missing API keys by returning empty responses
- The `.env` file is already in `.gitignore` - never commit it
- All API keys listed above have free tiers available
- Only `OPENWEATHER_API_KEY` is currently used by implemented tools

### Cache Management

FastF1 caches session data in `cache/` for performance. Clear if needed:

```bash
rm -rf cache/     # Unix/macOS
rmdir /s cache    # Windows
```

---

## 🧪 Testing

Test individual tools:

```bash
# Test session tool
python tools/session/results.py

# Test telemetry
python tools/telemetry/lap_telemetry.py

# Test OpenF1 live data
python tools/live/radio.py

# Test weather forecast
python tools/forecast/race_weather.py
```

All tools include standalone test blocks in `if __name__ == "__main__"`.

## 🤝 Contributing

Contributions welcome! Please submit a Pull Request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - Formula 1 data library
- [OpenF1](https://openf1.org/) - Real-time F1 data API
- [Ergast API](http://ergast.com/mrd/) - Historical F1 database
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

---

**Built with ❤️ for F1 fans and data enthusiasts**
