# Pitstop 🏎️

Your one-stop shop for Formula 1 data and insights via the Model Context Protocol (MCP).

![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)
![MCP](https://img.shields.io/badge/MCP-1.16.0%2B-green)
![FastF1](https://img.shields.io/badge/FastF1-3.6.1%2B-red)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

Pitstop is an MCP server that provides comprehensive Formula 1 data access through a simple, unified interface. Built on top of the FastF1 library, it offers real-time and historical F1 statistics, standings, and more.

## Features

- 📊 Driver Championship Standings
- 🏆 Historical Season Data (1950-present)
- ⚡ Fast caching for improved performance
- 🔌 Easy integration with MCP-compatible clients
- 🎯 Type-safe responses with Pydantic models

## Available Tools

### Championship Data

| Tool Name            | Description                                                                                                                                                                        | Parameters                                 | Returns                                                                                                                                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `driver_standings` | Get complete Formula 1 driver championship standings for a specific season. Returns the final standings table showing each driver's position, points, wins, team, and driver code. | `year` (int): Season year (1950-present) | Championship standings with a list of all drivers, each containing: position, driver name, driver code (3-letter abbreviation), team/constructor name, total championship points, and number of race wins |

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. Clone the repository:

```bash
git clone https://github.com/praneethravuri/pitstop.git
cd pitstop
```

2. Install dependencies using uv:

```bash
uv sync
```

This will create a virtual environment and install all required dependencies including:

- FastF1 (Formula 1 data access)
- MCP (Model Context Protocol)
- Pydantic (Data validation)
- httpx (HTTP client)

## Configuration

### For Windows Users

Add the following configuration to your MCP client settings (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "Pitstop": {
      "command": "C:\\Users\\<YOUR_USERNAME>\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--directory",
        "[ABSOLUTE PATH TO PROJECT]\\pitstop",
        "mcp",
        "run",
        "[ABSOLUTE PATH TO PROJECT]\\pitstop\\server.py"
      ]
    }
  }
}
```

**Important Notes:**

- Replace `<YOUR_USERNAME>` with your Windows username
- Replace `C:\\projects\\pitstop` with the actual path to your Pitstop installation
- The `--directory` flag is crucial - it ensures uv uses the project's virtual environment with all dependencies
- Make sure to use double backslashes (`\\`) in Windows paths

## Usage

Once configured, you can use Pitstop tools through your MCP client:

### Example Queries

**Get Current Season Standings:**

```
What are the 2024 F1 driver championship standings?
```

**Get Historical Standings:**

```
What were the F1 driver standings in 2021?
```

**Compare Seasons:**

```
Show me the top 3 drivers from the 2024 and 2021 F1 seasons
```

### Response Data

The server returns structured data including:

- **Position**: Championship position (1st, 2nd, 3rd, etc.)
- **Driver Name**: Full name of the driver
- **Driver Code**: 3-letter driver abbreviation (e.g., VER, HAM, LEC)
- **Team**: Constructor/team name
- **Points**: Total championship points
- **Wins**: Number of race wins

### Example Response

**2024 Season:**

```json
{
  "year": 2024,
  "standings": [
    {
      "position": 1,
      "driver_name": "Max Verstappen",
      "driver_code": "VER",
      "team": "Red Bull",
      "points": 437.0,
      "wins": 9
    },
    {
      "position": 2,
      "driver_name": "Lando Norris",
      "driver_code": "NOR",
      "team": "McLaren",
      "points": 374.0,
      "wins": 4
    }
  ]
}
```

**2021 Season (Historic Championship Battle):**

```json
{
  "year": 2021,
  "standings": [
    {
      "position": 1,
      "driver_name": "Max Verstappen",
      "driver_code": "VER",
      "team": "Red Bull",
      "points": 395.5,
      "wins": 10
    },
    {
      "position": 2,
      "driver_name": "Lewis Hamilton",
      "driver_code": "HAM",
      "team": "Mercedes",
      "points": 387.5,
      "wins": 8
    }
  ]
}
```

## Project Structure

```
pitstop/
├── server.py              # MCP server entry point
├── tools/                 # Tool implementations
│   ├── driver_standings.py
│   └── __init__.py
├── clients/               # API clients
│   ├── fastf1_client.py
│   └── __init__.py
├── models/                # Pydantic data models
│   ├── driver_standings.py
│   └── __init__.py
├── utils/                 # Utility functions
├── cache/                 # FastF1 cache directory
├── pyproject.toml         # Project dependencies
└── README.md
```

## Development

### Running Locally

You can test the server locally using the MCP CLI:

```bash
uv run mcp run server.py
```

### Testing Tools Directly

Test tools directly without running the MCP server:

```bash
# Test driver standings for 2024
uv run python -c "from tools import driver_standings; result = driver_standings(2024); print(f'Champion: {result.standings[0].driver_name} - {result.standings[0].points} points')"

# Test driver standings for 2021
uv run python -c "from tools import driver_standings; result = driver_standings(2021); print(f'Champion: {result.standings[0].driver_name} - {result.standings[0].points} points')"
```

### Adding New Tools

1. Create a new tool function in `tools/`
2. Define corresponding Pydantic models in `models/`
3. Register the tool in `server.py`:

```python
from tools import your_new_tool

mcp.tool()(your_new_tool)
```

4. Test your tool:

```bash
uv run python -c "from tools import your_new_tool; print(your_new_tool(...))"
```

## Troubleshooting

### Common Issues

**Module Not Found Error**

- Ensure you've run `uv sync` to install dependencies
- Verify your MCP configuration uses `--directory` flag to point to the project root
- Make sure you're NOT using `--with mcp[cli]` as this creates a temporary environment without your dependencies

**Server Connection Issues**

- Check that the paths in your MCP configuration are correct
- Ensure Python 3.13+ is installed
- Verify uv is installed and accessible from the specified path

**Tool Execution Errors**

If a tool returns an error:

1. Test the tool directly using the command line (see "Testing Tools Directly" section)
2. Check that the year is valid (1950 to present)
3. Clear the cache if data seems corrupted
4. Check the MCP server logs for detailed error messages

### Data Source

Pitstop uses the [Ergast F1 API](http://ergast.com/mrd/) (via FastF1) for historical data. The data includes:

- Final championship standings for each season
- Official FIA data from 1950 to present
- Data is cached locally for faster subsequent requests

**Note**: For the current season, data may not be final until the season concludes. Mid-season standings reflect results up to the most recent race.

### Cache Management

FastF1 caches data in the `cache/` directory to improve performance. To clear the cache:

```bash
rm -rf cache/
```

Or on Windows:

```bash
rmdir /s cache
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) - For providing the excellent Formula 1 data library
- [Model Context Protocol](https://modelcontextprotocol.io/) - For the MCP specification
- Formula 1 community for their continued support of open data

## Roadmap

- [ ] Constructor/Team standings
- [ ] Race results and session data
- [ ] Driver and team statistics
- [ ] Lap time analysis
- [ ] Circuit information
- [ ] Live timing data
- [ ] Weather data
- [ ] Telemetry data access

---

Built with ❤️ for F1 fans and data enthusiasts
