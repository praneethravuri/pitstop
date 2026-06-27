# Pitstop — F1 MCP Server

An HTTP-first Model Context Protocol (MCP) server for Formula 1 data. Aggregates real-time, historical, and news data from multiple authoritative sources into 10 tools ready for any MCP client.

**v0.3.0** | Author: [Praneeth Ravuri](https://github.com/praneethravuri)

---

## Overview

Pitstop exposes F1 data as 10 MCP tools over HTTP (default) or stdio. It pulls from FastF1, Jolpica, OpenF1, Wikidata, and RSS feeds, handles pagination, retries, caching, and rate limiting transparently.

---

## Data Sources

| Source | Coverage | Type |
|--------|----------|------|
| [FastF1](https://github.com/theOehrly/Fast-F1) | 2018–present | Historical / timing / telemetry |
| [Jolpica-F1](https://github.com/jolpica/jolpica-f1) | 1950–present | Historical (Ergast-compatible) |
| [OpenF1](https://openf1.org/) | 2023–present | Real-time |
| RSS Feeds (Autosport, BBC, etc.) | Live | News |

---

## Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_session_data` | Race/qualifying results, lap times, weather, driver details (2018–present) | `year`, `event`, `session`, `includes`, `page`, `page_size` |
| `get_telemetry_data` | Lap-by-lap car telemetry (speed, throttle, brake, gears) (2018–present) | `year`, `event`, `session`, `driver`, `page`, `page_size` |
| `get_live_data` | Live intervals, pit stops, team radio, stints, race control (2023–present) | `category`, `session_key`, `page`, `page_size` |
| `get_standings` | Driver and constructor championship standings (1950–present) | `year`, `type`, `page`, `page_size` |
| `get_schedule` | Race calendar and session schedule | `year`, `event`, `page`, `page_size` |
| `get_reference_data` | Circuits, drivers, constructors encyclopedia (1950–present) | `category`, `query`, `page`, `page_size` |
| `get_f1_news` | F1 headlines from 30+ RSS sources | `query`, `page`, `page_size` |
| `get_results` | Race/qualifying/sprint results, lap times, pit stops (1950–present) | `year`, `round`, `result_type`, `driver`, `page` |
| `get_race_analysis` | Pace, tire degradation, stint summaries, consistency (2018–present) | `year`, `gp`, `session`, `drivers`, `analysis_type`, `page` |
| `query_wikidata` | SPARQL queries to Wikidata for F1 biography, career records, history | `sparql`, `page`, `page_size` |

---

## Transport

### HTTP (default)

```bash
uv sync
uv run pitstop
# → http://localhost:8000
```

MCP client config:

```json
{
  "mcpServers": {
    "pitstop": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### stdio (opt-in)

```bash
PITSTOP_TRANSPORT=stdio uv run pitstop
```

MCP client config:

```json
{
  "mcpServers": {
    "pitstop": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/pitstop", "pitstop"],
      "env": { "PITSTOP_TRANSPORT": "stdio" }
    }
  }
}
```

---

## Health API

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Per-source status (FastF1, Jolpica, OpenF1, RSS) |
| `GET /live` | Liveness probe |
| `GET /ready` | Readiness probe |

Example `/health` response:

```json
{
  "version": "0.3.0",
  "overall": "ok",
  "sources": [
    { "name": "fastf1",  "status": "ok", "latency_ms": 2,   "detail": "cache writable" },
    { "name": "jolpica", "status": "ok", "latency_ms": 134, "detail": "" },
    { "name": "openf1",  "status": "ok", "latency_ms": 98,  "detail": "" },
    { "name": "rss",     "status": "ok", "latency_ms": 210, "detail": "" }
  ]
}
```

`overall` is `"ok"` / `"degraded"` / `"down"`. HTTP 200 / 207 / 503.

---

## Wikidata SPARQL

`query_wikidata` runs SPARQL queries against [Wikidata](https://query.wikidata.org/) for biographical and historical F1 facts not covered by race APIs.

Only `SELECT` and `ASK` queries are accepted (read-only). Always include `LIMIT` in your query.

Example — find F1 drivers with their birthdate:

```sparql
SELECT ?driver ?driverLabel ?birthDate WHERE {
  ?driver wdt:P31 wd:Q5 ;
          wdt:P641 wd:Q1968 ;
          wdt:P569 ?birthDate .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} ORDER BY DESC(?birthDate) LIMIT 10
```

---

## Pagination

All list-returning tools accept `page` (1-based, default 1) and `page_size` (default 20). Responses include a `pagination` block:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 47,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PITSTOP_TRANSPORT` | `http` | `http` or `stdio` |
| `PITSTOP_HOST` | `0.0.0.0` | Bind address (HTTP only) |
| `PITSTOP_PORT` | `8000` | Listen port (HTTP only) |
| `PITSTOP_LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `PITSTOP_LOG_FORMAT` | `json` | `json` or `text` |
| `PITSTOP_ENV` | `development` | `development` or `production` |
| `PITSTOP_RATE_LIMIT_ENABLED` | `false` | Enable rate limiting |
| `PITSTOP_RATE_LIMIT_PER_HOUR` | `3600` | Requests allowed per hour |
| `PITSTOP_CACHE_TTL_SECONDS` | `300` | HTTP response cache TTL |
| `FASTF1_CACHE` | `cache` | FastF1 cache directory path |

---

## Docker

```bash
docker compose up
```

Server starts on port 8000 with health check at `/health`.

---

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check src/
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Credits / Acknowledgements

| Source | Description | License |
|--------|-------------|---------|
| [FastF1](https://github.com/theOehrly/Fast-F1) | Python library for F1 timing, telemetry, and session data | MIT |
| [Jolpica-F1](https://github.com/jolpica/jolpica-f1) | Ergast-compatible F1 data API, 1950–present | — |
| [OpenF1](https://openf1.org/) | Free open-source API for real-time F1 data | MIT |
| [Wikidata](https://www.wikidata.org/) | Open knowledge graph with SPARQL query service | CC0 |
| [Ergast Motor Racing API](https://ergast.com/mrd/) | Historical F1 data 1950–2024 (now served via Jolpica) | — |

Not affiliated with Formula 1 or the FIA. Data provided by third-party sources under their respective terms.
