# 🏎️ Pitstop: The All-in-One F1 MCP Server

Pitstop is a comprehensive Model Context Protocol (MCP) server for Formula 1 data. It aggregates data from multiple authoritative sources to answer any F1-related question, from historical stats to real-time race telemetry.

<div align="center">
  <img src="https://media.formula1.com/image/upload/f_auto,c_limit,w_1440,q_auto/f_auto/q_auto/content/dam/fom-website/manual/Misc/2021-Master-Folder/F1%20Logo%202021%20-%20Red" width="200" alt="F1 Logo" />
</div>

## 🌟 Capabilities

Pitstop consolidates specialized functions into **7 powerful tools**:

1.  **`get_live_data`**: Real-time access to telemetry, pit stops, team radio, race control messages, and intervals.
2.  **`get_session_data`**: Comprehensive session analysis including results, weather, fastest laps, and driver details.
3.  **`get_telemetry_data`**: Deep dive into car performance with lap-by-lap telemetry (speed, throttle, brake, gears).
4.  **`get_reference_data`**: Static encyclopedia for drivers, teams, circuits, and tire compounds.
5.  **`get_standings`**: Current and historical championship standings.
6.  **`get_schedule`**: Full calendar awareness including testing and future races.
7.  **`get_f1_news`**: Latest headlines from 25+ trusted global sources.

## 🔌 Data Sources

-   **OpenF1 API**: Real-time timing & telemetry (2023-Present)
-   **FastF1 / Ergast**: Historical data & deep analysis (1950-Present)
-   **RSS Feeds**: Aggregated news from official and major media outlets.

## 🚀 Installation & Usage

### Prerequisites
-   Python 3.13+
-   `uv` (recommended) or `pip`

### 1. Install via Smithery (Recommended)

To install Pitstop for Claude Desktop automatically:

```bash
npx -y @smithery/cli install pitstop --client claude
```

### 2. Manual Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
uv sync
```

### 3. Running the Server

Run the MCP server directly using `uv`:

```bash
uv run pitstop
```

### 4. Docker Deployment

To run with Docker Compose:

```bash
docker-compose up -d
```

Or manually using python:

```bash
# Add src to PYTHONPATH if running manually
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python -m pitstop
```

## 🛠️ Tool Usage Guide

| Tool | Purpose | Example Query |
| :--- | :--- | :--- |
| **`get_live_data`** | Live race monitoring | "Check the gap between VER and HAM", "Any specialized pit stops?" |
| **`get_session_data`** | Post-session analysis | "Get full results for Monaco 2024", "What was the weather during Q3?" |
| **`get_standings`** | Championship tracker | "Who is leading the constructor standings?", "2021 driver points" |
| **`get_schedule`** | Calendar & Events | "When is the next race?", "Monaco GP start times" |
| **`get_reference_data`** | Encyclopedia | "How many corners does Spa have?", "Max Verstappen stats" |
| **`get_f1_news`** | News Aggregator | "Latest Ferrari news", "Updates on Newey" |
| **`get_telemetry_data`** | Deep Tech Analysis | "Compare telemetry for VER and LEC in Q3" |

## 📦 Project Structure

```
src/
  pitstop/
    __main__.py       # Entry point
    clients/          # API Clients (OpenF1, FastF1, RSS)
    models/           # Pydantic Data Models
    tools/            # Tool Implementations
      live/           # Live Data Tools
      general/        # Session & Telemetry
      reference/      # Static Data
      ...
```

## 📜 License

MIT License. Data provided by FastF1, OpenF1, and Ergast. Not affiliated with Formula 1 or FIA.
