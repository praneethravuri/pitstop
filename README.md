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
- 📰 Latest F1 News from Multiple Sources
- 🔄 Silly Season & Transfer Rumors
- 💼 Team Management Changes & Contract News
- 🎯 Smart filtering by driver, team, or year
- ⚡ Fast caching for improved performance
- 🔌 Easy integration with MCP-compatible clients
- 🎯 Type-safe responses with Pydantic models

## Available Tools

### Championship Data

| Tool Name          | Description                                                                                                                                                                        | Parameters                               | Returns                                                                                                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `driver_standings` | Get complete Formula 1 driver championship standings for a specific season. Returns the final standings table showing each driver's position, points, wins, team, and driver code. | `year` (int): Season year (1950-present) | Championship standings with a list of all drivers, each containing: position, driver name, driver code (3-letter abbreviation), team/constructor name, total championship points, and number of race wins |

### News & Updates

| Tool Name  | Description                                                                                                                              | Parameters                                                                                                                                            | Returns                                                                                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `f1_news`  | Get latest Formula 1 news from trusted RSS feeds. Aggregates news from official F1 site, FIA press releases, Autosport, The Race, RaceFans, and more sources. | `source` (str): News source - "formula1", "fia", "autosport", "the-race", "racefans", "planetf1", "motorsport", "all" (default: "formula1")<br>`limit` (int): Max articles 1-50 (default: 10) | News articles with title, link, published date, summary, source name, and author (if available) |
| `latest_f1_news` | Get latest F1 news from all sources (driver announcements, team changes, rule updates, race reports). | `source` (str): News source (default: "all")<br>`limit` (int): Max articles 1-50 (default: 15) | Latest news articles with titles, links, dates, summaries, and sources |

### Silly Season & Transfer News

| Tool Name  | Description                                                                                                                              | Parameters                                                                                                                                            | Returns                                                                                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `silly_season_news` | Get F1 silly season news including driver transfers, team changes, and rumors. Filter by year, driver, or constructor. | `year` (int, optional): Filter by year<br>`driver` (str, optional): Filter by driver name<br>`constructor` (str, optional): Filter by team name<br>`limit` (int): Max articles 1-50 (default: 20) | Silly season articles with titles, links, dates, summaries, categories, and relevance scores |
| `driver_transfer_rumors` | Get latest driver transfer rumors and speculation. Can be filtered by specific driver. | `driver` (str, optional): Filter by driver name<br>`limit` (int): Max articles 1-50 (default: 15) | Transfer-related news with rumored moves, confirmed signings, and negotiations |
| `team_management_changes` | Get news about team management changes (team principals, technical directors, appointments, departures). | `constructor` (str, optional): Filter by team name<br>`limit` (int): Max articles 1-50 (default: 15) | Management news including appointments, resignations, and restructuring |
| `contract_news` | Get contract-related news (renewals, extensions, expirations). Filter by driver or team. | `driver` (str, optional): Filter by driver name<br>`constructor` (str, optional): Filter by team name<br>`limit` (int): Max articles 1-50 (default: 15) | Contract news including extensions, renewals, and multi-year deals |

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
- feedparser (RSS feed parsing)
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

#### Championship Standings

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

#### News & Updates

**Get Latest F1 News:**

```
What's the latest F1 news?
```

**Get News from Specific Source:**

```
Show me the top 5 F1 articles from Autosport
```

**Get News from All Sources:**

```
Get me 20 F1 news articles from all sources
```

**Stay Updated:**

```
Any breaking F1 news today?
What happened in F1 this week?
```

#### Silly Season & Transfer News

**Get General Silly Season News:**

```
What's the latest silly season news?
Show me driver transfer rumors for 2025
```

**Get Driver-Specific Transfer Rumors:**

```
Are there any transfer rumors about Lewis Hamilton?
What are the latest rumors about Carlos Sainz?
Show me transfer news for Max Verstappen
```

**Get Team Management Changes:**

```
Any management changes at Ferrari?
Show me recent team principal appointments
What management changes happened at Red Bull?
```

**Get Contract News:**

```
Which driver contracts are expiring soon?
Show me contract extension news for Lando Norris
Any contract news for McLaren?
```

**Filter by Year:**

```
Show me silly season news from 2024
What were the driver transfers in 2023?
```

### Response Data

#### Championship Standings

The server returns structured data including:

- **Position**: Championship position (1st, 2nd, 3rd, etc.)
- **Driver Name**: Full name of the driver
- **Driver Code**: 3-letter driver abbreviation (e.g., VER, HAM, LEC)
- **Team**: Constructor/team name
- **Points**: Total championship points
- **Wins**: Number of race wins

#### News Articles

The server returns structured news data including:

- **Title**: Article headline
- **Link**: URL to full article
- **Published**: Publication date and time
- **Summary**: Article excerpt or description
- **Source**: News source name (formula1, autosport, etc.)
- **Author**: Article author (if available)

### Example Responses

#### Championship Standings

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

#### News Articles

**Latest F1 News from Autosport:**

```json
{
  "source": "autosport",
  "fetched_at": "2024-10-04T18:30:00",
  "article_count": 5,
  "articles": [
    {
      "title": "How Russell nailed Singapore GP pole as Verstappen's dirty air complaint is examined",
      "link": "https://www.autosport.com/f1/news/...",
      "published": "Sat, 21 Sep 2024 19:45:00 GMT",
      "summary": "George Russell claimed a stunning pole position for the Singapore Grand Prix...",
      "source": "autosport",
      "author": "Jonathan Noble"
    },
    {
      "title": "What has happened to McLaren's 2025 F1 advantage?",
      "link": "https://www.autosport.com/f1/news/...",
      "published": "Sat, 21 Sep 2024 16:30:00 GMT",
      "summary": "McLaren's dominant form in the second half of 2024 has raised questions...",
      "source": "autosport",
      "author": null
    }
  ]
}
```

**Aggregated News from All Sources:**

```json
{
  "source": "all",
  "fetched_at": "2024-10-04T18:30:00",
  "article_count": 12,
  "articles": [
    {
      "title": "What are the tactical options for the Singapore GP?",
      "link": "https://www.formula1.com/...",
      "published": "2024-09-21T10:00:00Z",
      "summary": "With Singapore's unique characteristics...",
      "source": "formula1",
      "author": null
    },
    {
      "title": "Verstappen eyes redemption in Singapore",
      "link": "https://www.racefans.net/...",
      "published": "2024-09-21T09:30:00Z",
      "summary": "Max Verstappen is looking to bounce back...",
      "source": "racefans",
      "author": "Keith Collantine"
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
│   ├── news.py            # F1 news tool
│   ├── news_and_updates/  # News and updates directory
│   │   ├── silly_season.py    # Silly season tools
│   │   ├── latest_news.py     # Latest F1 news tool
│   │   └── __init__.py
│   └── __init__.py
├── clients/               # API clients
│   ├── fastf1_client.py
│   ├── rss_client.py      # RSS feed client
│   └── __init__.py
├── models/                # Pydantic data models
│   ├── driver_standings.py
│   ├── news.py            # News models
│   ├── silly_season.py    # Silly season models
│   └── __init__.py
├── utils/                 # Utility functions
│   ├── date_validator.py
│   ├── text_cleaner.py
│   └── __init__.py
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

# Test F1 news from official F1 site
uv run python -c "from tools import f1_news; result = f1_news('formula1', 3); print(f'Found {result.article_count} articles from {result.source}'); print(f'Latest: {result.articles[0].title}')"

# Test F1 news from Autosport
uv run python -c "from tools import f1_news; result = f1_news('autosport', 5); print(f'Found {result.article_count} articles'); [print(f'  - {article.title}') for article in result.articles[:3]]"

# Test aggregated news from all sources
uv run python -c "from tools import f1_news; result = f1_news('all', 3); print(f'Total articles: {result.article_count}'); sources = set([a.source for a in result.articles]); print(f'Sources: {sources}')"

# Test silly season news
uv run python -c "from tools import silly_season_news; result = silly_season_news(limit=5); print(f'Found {result.article_count} silly season articles'); print(f'Top article: {result.articles[0].title}')"

# Test driver transfer rumors for specific driver
uv run python -c "from tools import driver_transfer_rumors; result = driver_transfer_rumors(driver='Hamilton', limit=5); print(f'Transfer rumors for Hamilton: {result.article_count} articles')"

# Test team management changes
uv run python -c "from tools import team_management_changes; result = team_management_changes(constructor='Ferrari', limit=5); print(f'Management changes at Ferrari: {result.article_count} articles')"

# Test contract news
uv run python -c "from tools import contract_news; result = contract_news(driver='Verstappen', limit=5); print(f'Contract news for Verstappen: {result.article_count} articles')"

# Test latest F1 news
uv run python -c "from tools import latest_f1_news; result = latest_f1_news(limit=5); print(f'Latest F1 news: {result.article_count} articles from {result.source}')"
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
