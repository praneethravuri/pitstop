# Pitstop 🏎️

> **Comprehensive Formula 1 data via Model Context Protocol (MCP) for Claude Desktop**

![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue) ![MCP](https://img.shields.io/badge/MCP-1.16.0%2B-green) ![FastF1](https://img.shields.io/badge/FastF1-3.6.1%2B-red) ![100% Free](https://img.shields.io/badge/100%25-FREE-brightgreen) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Production-ready MCP server** with 25 optimized F1 data tools, comprehensive logging, health checks, and flexible configuration. Aggregates data from 4 free sources (FastF1, OpenF1, Ergast, 25+ RSS feeds) covering Formula 1 from 1950 to present.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
uv sync

# Optional: Configure environment variables
cp .env.example .env
# Edit .env to customize settings
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

| Source               | Coverage       | Data Types                                      |  |
| -------------------- | -------------- | ----------------------------------------------- | - |
| **FastF1**     | 2018-present   | Session data, telemetry, weather, race control  |  |
| **Ergast API** | 1950-2024      | Historical results, standings, driver/team info |  |
| **RSS Feeds**  | Latest F1 News | Latest news from 25+ sources                    |  |
| **OpenF1 API** | 2023-present   | Real-time radio, pit stops, intervals           |  |

> **Note:** RSS feeds only contain recent articles. For historical F1 news (e.g., 2013 Indian GP), use web search instead.

---

## 🛠️ Available Tools

### Core Session Data

| Tool                        | Description                                                | Key Parameters                                            |
| --------------------------- | ---------------------------------------------------------- | --------------------------------------------------------- |
| `get_session_details`     | Complete session overview with results and weather         | `year`, `gp`, `session`                             |
| `get_session_results`     | Final classification/results                               | `year`, `gp`, `session`                             |
| `get_laps`                | Lap-by-lap data including fastest laps, sectors, pit stops | `year`, `gp`, `session`, `driver?`, `lap_type?` |
| `get_session_drivers`     | List of drivers in session                                 | `year`, `gp`, `session`                             |
| `get_tire_strategy`       | Tire compound usage and stint data                         | `year`, `gp`, `session`, `driver?`                |
| `get_qualifying_sessions` | Split qualifying into Q1/Q2/Q3 segments                    | `year`, `gp`, `segment?`                            |
| `get_track_evolution`     | Track lap time improvement through session                 | `year`, `gp`, `session`, `max_laps?`              |

### Telemetry & Analysis

| Tool                         | Description                                | Key Parameters                                                                 |
| ---------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------ |
| `get_lap_telemetry`        | High-frequency telemetry data              | `year`, `gp`, `session`, `driver`, `lap_number`                      |
| `compare_driver_telemetry` | Side-by-side telemetry comparison          | `year`, `gp`, `session`, `driver1`, `driver2`, `lap1?`,  `lap2?` |
| `get_analysis`             | Race pace, tire degradation, stints        | `year`, `gp`, `session`, `analysis_type`, `driver?`                  |
| `get_session_weather`      | Historical weather data throughout session | `year`, `gp`, `session`                                                  |

### Race Control & Track

| Tool                          | Description                                        | Key Parameters                                   |
| ----------------------------- | -------------------------------------------------- | ------------------------------------------------ |
| `get_race_control_messages` | All race control messages (flags, penalties, etc.) | `year`, `gp`, `session`, `message_type?` |
| `get_circuit`               | Circuit layout, corners, track status              | `year`, `gp`, `data_type`, `session?`    |

**Note:** `get_race_control_messages` supports filtering with `message_type`: `"all"`, `"penalties"`, `"investigations"`, `"flags"`, `"safety_car"`

### Live Timing - OpenF1

| Tool                   | Description                          | Key Parameters                                                              |
| ---------------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| `get_driver_radio`   | Team radio messages with transcripts | `year`, `country`, `session_name?`, `driver_number?`                |
| `get_live_pit_stops` | Pit stop timing and statistics       | `year`, `country`, `session_name?`, `driver_number?`                |
| `get_live_intervals` | Real-time gaps and intervals         | `year`, `country`, `session_name?`, `driver_number?`                |
| `get_meeting_info`   | Meeting and session schedule         | `year`, `country`                                                       |
| `get_stints_live`    | Real-time tire stint tracking        | `year`, `country`, `session_name?`, `driver_number?`, `compound?` |

### Championship & Schedule

| Tool              | Description                  | Key Parameters                                                                   |
| ----------------- | ---------------------------- | -------------------------------------------------------------------------------- |
| `get_standings` | Driver/constructor standings | `year`, `round?`, `type?`, `driver_name?`, `team_name?`                |
| `get_schedule`  | F1 calendar with sessions    | `year`, `include_testing?`, `round?`, `event_name?`, `only_remaining?` |

### Reference & Media

| Tool                   | Description                         | Key Parameters                                                 |
| ---------------------- | ----------------------------------- | -------------------------------------------------------------- |
| `get_reference_data` | Driver info, team details, circuits | `reference_type`, `year?`, `name?`                       |
| `get_f1_news`        | Latest F1 news                      | `source?`, `limit?`, `keywords?`, `driver?`, `team?` |

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

# Race Control
"What penalties were given in Monaco?"
"Show me all flag periods from the race"
"Get safety car periods"

# Live Data
"Get team radio messages from the race"
"Show me pit stop times for all drivers"
"What was the gap between Verstappen and Hamilton?"

# News & Schedule (Recent only)
"What's the latest F1 news?"
"Show me recent news about Ferrari"
"What are the transfer rumors this week?"
"When is the next race?"

# Note: For historical news (e.g., "2013 Indian GP"), use web search
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Pitstop uses environment variables for configuration. A `.env` file is included for easy setup:

```bash
# Copy the example file and customize
cp .env.example .env
```

**Available Configuration Options:**

| Variable                       | Default                           | Description                                                             |
| ------------------------------ | --------------------------------- | ----------------------------------------------------------------------- |
| `PITSTOP_ENV`                | `development`                   | Environment mode:`development` or `production`                      |
| `PITSTOP_LOG_LEVEL`          | `DEBUG` (dev) / `INFO` (prod) | Logging level:`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `PITSTOP_ENABLE_CACHING`     | `true`                          | Enable caching for improved performance                                 |
| `PITSTOP_CACHE_TTL`          | `300`                           | Cache time-to-live in seconds (5 minutes)                               |
| `PITSTOP_RATE_LIMIT_ENABLED` | `false`                         | Enable rate limiting per client                                         |
| `PITSTOP_RATE_LIMIT`         | `1000`                          | Maximum requests per hour per client                                    |
| `PITSTOP_TIMEOUT`            | `30`                            | Default timeout in seconds                                              |
| `PITSTOP_TELEMETRY_TIMEOUT`  | `60`                            | Telemetry timeout in seconds                                            |

**Production Mode** (`PITSTOP_ENV=production`):

- ✅ Structured JSON logging for log aggregation
- ✅ Error message masking for security
- ✅ Optimized performance settings
- ✅ Health check resources enabled

**Development Mode** (`PITSTOP_ENV=development`):

- ✅ Human-readable text logging
- ✅ Detailed error messages with stack traces
- ✅ Debug-level logging by default
- ✅ Full error context for debugging

### Cache Management

FastF1 caches session data in `cache/` for performance. Clear if needed:

```bash
rm -rf cache/     # Unix/macOS
rmdir /s cache    # Windows
```

### Health Check

Access server status and health information via the `server://status` resource:

```json
{
  "server": "Pitstop F1 MCP Server",
  "version": "1.0.0",
  "status": "operational",
  "environment": "production",
  "tools_count": 25,
  "data_sources": {
    "fastf1": "operational (2018-present)",
    "openf1": "operational (2023-present)",
    "ergast": "operational (1950-2024)",
    "rss_feeds": "operational (25+ sources)"
  }
}
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

# Test race control
python tools/control/messages.py
```

---

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
