# PITSTOP F1 MCP SERVER - COMPREHENSIVE TOOL ROADMAP

## Overview
This document provides a complete roadmap of all tools (implemented and planned) for the Pitstop F1 MCP Server, organized by category with implementation requirements and composability notes.

---

## TABLE OF CONTENTS
1. [Schedule & Events](#1-schedule--events)
2. [Session Data](#2-session-data)
3. [Telemetry](#3-telemetry)
4. [Track & Circuit](#4-track--circuit)
5. [Weather](#5-weather)
6. [Race Control](#6-race-control)
7. [Standings](#7-standings)
8. [Historical Data](#8-historical-data)
9. [Reference & Metadata](#9-reference--metadata)
10. [Live Timing](#10-live-timing)
11. [News & Media](#11-news--media)
12. [Advanced Analysis](#12-advanced-analysis)

---

## 1. SCHEDULE & EVENTS

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_schedule` | Schedule | ✅ Implemented | FastF1: `get_event_schedule()`, `get_events_remaining()` | **Comprehensive tool** - Get F1 calendar, upcoming races, testing sessions, and event details with flexible filtering |

---

## 2. SESSION DATA

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_session_details` | Session | ✅ Implemented | FastF1: `get_session()`, `Session.event`, Pydantic models | Get session info (date, type, name, track, weather, fastest lap) |
| `get_session_results` | Session | ✅ Implemented | FastF1: `Session.load()`, `Session.results` | Get final classification/results for any session |
| `get_laps` | Session | ✅ Implemented | FastF1: `Session.laps`, `Laps.pick_driver()`, `Laps.pick_fastest()` | Get lap-by-lap data with flexible filtering (all laps, driver-specific, fastest) |
| `get_session_drivers` | Session | ✅ Implemented | FastF1: `Session.drivers`, `Session.get_driver()` | Get list of drivers participating in a session |
| `get_tire_strategy` | Session | ✅ Implemented | FastF1: `Laps.pick_driver()`, `Laps.Compound` column | Get tire compound usage and stint data per driver |
| `get_advanced_session_data` | Session | ✅ Implemented | FastF1: `Laps`, Sector columns, PitInTime/PitOutTime | **Comprehensive tool** - Get fastest laps, sector times, and pit stops with flexible filtering |
| `get_qualifying_sessions` | Session | 🔴 Not Implemented | FastF1: `Laps.split_qualifying_sessions()` | Split qualifying into Q1, Q2, Q3 segments |
| `get_track_evolution` | Session | 🔴 Not Implemented | FastF1: `Laps` with `Time`, `LapStartTime` | Track how lap times improved during session |

---

## 3. TELEMETRY

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_lap_telemetry` | Telemetry | ✅ Implemented | FastF1: `Lap.get_telemetry()`, all telemetry channels | Get detailed high-frequency telemetry for specific lap (speed, throttle, brake, gear, RPM, DRS) |
| `compare_driver_telemetry` | Telemetry | ✅ Implemented | FastF1: `Lap.get_telemetry()`, `Telemetry.merge_channels()` | Compare telemetry data between two drivers side-by-side |
| `get_car_data` | Telemetry | 🔴 Not Implemented | FastF1: `Session.car_data`, `Lap.get_car_data()` | Get raw car data stream for analysis |
| `get_position_data` | Telemetry | 🔴 Not Implemented | FastF1: `Session.pos_data`, `Lap.get_pos_data()`, X/Y columns | Get X/Y track position coordinates for racing line analysis |
| `get_speed_trace` | Telemetry | 🔴 Not Implemented | FastF1: `Telemetry.Speed` channel | Get speed throughout a lap with sector breakdowns |
| `get_gear_usage` | Telemetry | 🔴 Not Implemented | FastF1: `Telemetry.Gear`, `Telemetry.nGear` channels | Analyze gear usage around the track |
| `get_drs_usage` | Telemetry | 🔴 Not Implemented | FastF1: `Telemetry.DRS` channel | Track DRS activation zones and times |
| `get_brake_points` | Telemetry | 🔴 Not Implemented | FastF1: `Telemetry.Brake` channel | Analyze braking zones and compare braking points |
| `get_throttle_trace` | Telemetry | 🔴 Not Implemented | FastF1: `Telemetry.Throttle` channel | Throttle application throughout lap |
| `get_delta_time` | Telemetry | 🔴 Not Implemented | FastF1: `fastf1.utils.delta_time()` | Calculate time delta between two laps |

---

## 4. TRACK & CIRCUIT

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_circuit` | Track | ✅ Implemented | FastF1: `Session.get_circuit_info()`, `Session.track_status` | **Comprehensive tool** - Get circuit layout, corners, track status, and flag periods |
| `get_session_status` | Track | 🔴 Not Implemented | FastF1: `Session.session_status`, `api.session_status_data()` | Get session start/end/red flag times |

---

## 5. WEATHER

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_session_weather` | Weather | ✅ Implemented | FastF1: `Session.weather_data`, `api.weather_data()` | Get weather data throughout session (temp, humidity, rain, wind) |
| `get_lap_weather` | Weather | 🔴 Not Implemented | FastF1: `Lap.get_weather_data()`, Weather columns | Get weather conditions for specific lap/time |
| `get_weather_evolution` | Weather | 🔴 Not Implemented | FastF1: `Session.weather_data` time series | Track weather changes during session |

---

## 6. RACE CONTROL

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_race_control_messages` | Control | ✅ Implemented | FastF1: `Session.race_control_messages`, `api.race_control_messages()` | Get all race control messages, flags, investigations |
| `get_penalties` | Control | 🔴 Not Implemented | FastF1: `Session.race_control_messages` with filtering | Filter for penalty decisions only |
| `get_investigations` | Control | 🔴 Not Implemented | FastF1: `Session.race_control_messages` with filtering | Filter for investigation notices |
| `get_flag_history` | Control | 🔴 Not Implemented | FastF1: `Session.track_status`, `Session.race_control_messages` | Get all flag periods (yellow, red, safety car) |

---

## 7. STANDINGS

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_driver_standings` | Standings | ✅ Implemented | Ergast: `Ergast().get_driver_standings()` | Get driver championship standings by year/round |
| `get_constructor_standings` | Standings | ✅ Implemented | Ergast: `Ergast().get_constructor_standings()` | Get constructor championship standings by year/round |
| `get_points_progression` | Standings | 🔴 Not Implemented | Ergast: `get_driver_standings()` for each round | Track points earned across season for driver/constructor |

---

## 8. HISTORICAL DATA

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_historical_results` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_race_results()` | Get race results from past seasons |
| `get_historical_qualifying` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_qualifying_results()` | Get qualifying results from past seasons |
| `get_historical_sprint` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_sprint_results()` | Get sprint race results from past seasons |
| `get_historical_lap_times` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_lap_times()` | Get lap times from past races |
| `get_historical_pit_stops` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_pit_stops()` | Get pit stop data from past races |
| `get_seasons` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_seasons()` | Get list of all F1 seasons available |
| `get_historical_schedule` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_race_schedule()` | Get race calendar from past season |
| `get_finishing_status` | Historical | 🔴 Not Implemented | Ergast: `Ergast().get_finishing_status()` | Get DNF reasons and finishing classifications |

---

## 9. REFERENCE & METADATA

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_reference_data` | Reference | ✅ Implemented | Ergast: `get_driver_info()`, `get_constructor_info()`, `get_circuits()` | **Comprehensive tool** - Get driver info, team details, circuit metadata, and tire compounds with filtering |

---

## 10. LIVE TIMING

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `record_live_timing` | Live | 🔴 Not Implemented | FastF1: `livetiming.SignalRClient()`, Python 3.8-3.9 | Record live timing data during a session |
| `load_live_timing` | Live | 🔴 Not Implemented | FastF1: `livetiming.LiveTimingData()` | Load previously recorded live timing data |
| `get_live_timing_categories` | Live | 🔴 Not Implemented | FastF1: `LiveTimingData.list_categories()` | List available data categories in recording |

---

## 11. NEWS & MEDIA

### 11.1 Implemented News Tools

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_f1_news` | News | ✅ Implemented | RSS feeds, BeautifulSoup | Get F1 news with filtering by source, category, driver, team |
| `get_practice_reports` | News | ✅ Implemented | RSS feeds | Retrieve practice session reports and analysis |
| `get_qualifying_reports` | News | ✅ Implemented | RSS feeds | Fetch qualifying session coverage and grid penalties |
| `get_race_reports` | News | ✅ Implemented | RSS feeds | Pull race day reports, results, and analysis |
| `get_race_highlights` | News | ✅ Implemented | RSS feeds | Compile key moments, overtakes, and incidents |
| `get_race_weekend_news` | News | ✅ Implemented | RSS feeds | Aggregate all news for specific race weekend |
| `driver_transfer_rumors` | News | ✅ Implemented | RSS feeds | Collect driver transfer rumors and speculation |
| `team_management_changes` | News | ✅ Implemented | RSS feeds | Track changes in team management |
| `contract_news` | News | ✅ Implemented | RSS feeds | Handle news on contract renewals and extensions |

### 11.2 Silly Season & Rumors

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_silly_season_year` | News | 🟡 Next Up | RSS: RaceFans, Autosport, Motorsport.com | Fetch silly season news for specific year |
| `get_silly_season_driver` | News | 🟡 Next Up | NewsAPI free tier, Reddit r/formula1 | Retrieve silly season news for specific driver |
| `get_silly_season_constructor` | News | 🟡 Next Up | RSS: The-Race.com, F1.com | Gather silly season news for specific constructor |
| `get_silly_season_historical` | News | 🟡 Next Up | Ergast API, Wikipedia, Wayback Machine | Pull historical silly season details and outcomes |
| `potential_new_teams_sponsors` | News | 🟡 Next Up | RSS: GPBlog, PlanetF1 | Monitor news on new teams and sponsor deals |
| `supplier_switches` | News | 🟡 Next Up | FIA site scraping, Autosport RSS | Report on supplier changes (tire, engine providers) |

### 11.3 Race Weekend Coverage

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_sprint_reports` | News | 🔴 Not Implemented | FastF1 + F1.com RSS | Gather sprint race reports and analysis |
| `get_driver_team_radio` | News | 🔴 Not Implemented | YouTube API, Reddit scraping | Collect highlights from radio communications |
| `get_post_race_performance` | News | 🔴 Not Implemented | Ergast API, FastF1 | Analyze post-race performance metrics |

### 11.4 Technical & Car Development

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_car_launches` | News | 🔴 Not Implemented | RSS: Motorsport.com, team sites | Fetch news on car launches and livery reveals |
| `get_upgrades_aero` | News | 🔴 Not Implemented | The-Race.com RSS, Reddit r/F1Technical | Retrieve details on upgrades and aero packages |
| `get_power_unit_news` | News | 🔴 Not Implemented | FIA technical reports, Autosport | Cover power unit developments and reliability |
| `get_regulation_changes` | News | 🔴 Not Implemented | FIA site RSS, Wikipedia | Summarize regulation changes for specific year |

### 11.5 Latest News & Announcements

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_driver_announcements` | News | 🔴 Not Implemented | F1.com RSS, Google News | Aggregate driver-related announcements |
| `get_rule_schedule_changes` | News | 🔴 Not Implemented | FIA press releases, F1 calendar API | Fetch rule or schedule modifications |
| `get_fia_statements` | News | 🔴 Not Implemented | FIA website RSS | Collect official FIA statements |
| `get_calendar_updates` | News | 🔴 Not Implemented | Ergast API, RaceFans RSS | Provide calendar changes and new races |

### 11.6 Driver & Team News

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_injuries_recoveries` | News | 🔴 Not Implemented | PlanetF1 RSS, Reddit | Report on driver injuries and recoveries |
| `get_interviews_statements` | News | 🔴 Not Implemented | YouTube API, MotorsportWeek scraping | Aggregate driver/team interviews |
| `get_team_restructuring` | News | 🔴 Not Implemented | Autosport RSS | Cover team restructuring and partnerships |
| `get_sponsorships_deals` | News | 🔴 Not Implemented | GPBlog RSS | Track sponsorships and brand deals |

### 11.7 Opinions & Editorials

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_expert_analysis` | News | 🔴 Not Implemented | The-Race.com RSS, Reddit | Collect expert opinions and analysis |
| `get_predictions_rankings` | News | 🔴 Not Implemented | ESPN F1 scraping, PlanetF1 RSS | Fetch predictions and power rankings |
| `get_fan_polls_commentary` | News | 🔴 Not Implemented | Reddit API | Aggregate fan polls and reactions |
| `get_ethical_discussions` | News | 🔴 Not Implemented | Guardian Sports RSS, Google Scholar | Cover ethical/political issues in F1 |

### 11.8 Stats, Records & Historical News

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_race_statistics` | News | 🔴 Not Implemented | Ergast API, FastF1 | Provide detailed race stats and milestones |
| `get_historic_anniversaries` | News | 🔴 Not Implemented | Wikipedia, F1.com heritage | Highlight historic anniversaries |
| `get_era_comparisons` | News | 🔴 Not Implemented | Ergast, custom scripts | Compare stats between eras |
| `get_championship_recaps` | News | 🔴 Not Implemented | Ergast, RaceFans archives | Recap past championships |

### 11.9 Business & Financial News

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_sponsorships_investments` | News | 🔴 Not Implemented | BusinessF1 scraping, Forbes RSS | Track F1 sponsorships and investments |
| `get_team_budgets` | News | 🔴 Not Implemented | FIA financial reports, Autosport | Report on team budgets and cost caps |
| `get_f1_revenue_updates` | News | 🔴 Not Implemented | Reuters/Bloomberg RSS, NewsAPI | Cover Liberty Media and F1 revenue |
| `get_venue_contracts` | News | 🔴 Not Implemented | GPUpdate RSS, F1 press releases | Detail venue contracts and broadcasting rights |

### 11.10 Regulatory / FIA Updates

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_penalties_investigations` | News | 🔴 Not Implemented | FIA decisions database, RaceFans | Aggregate penalties and rulings |
| `get_appeals_rulings` | News | 🔴 Not Implemented | Official FIA documents | Cover appeals and stewards' decisions |
| `get_safety_regulations` | News | 🔴 Not Implemented | FIA safety reports | Summarize safety rule updates |
| `get_rulebook_changes` | News | 🔴 Not Implemented | FIA sporting regulations | Track F1 rulebook changes |

### 11.11 Fan & Social Media

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_meme_trends` | News | 🔴 Not Implemented | Reddit API, X search API | Collect viral F1 memes and trends |
| `get_fan_reactions` | News | 🔴 Not Implemented | Reddit, Pushshift.io | Aggregate fan reactions to events |
| `get_driver_social_posts` | News | 🔴 Not Implemented | X API, Instagram scraping | Fetch recent driver social media posts |
| `get_community_discussions` | News | 🔴 Not Implemented | Reddit API, Discord webhooks | Summarize F1 community discussions |
| `get_behind_scenes` | News | 🔴 Not Implemented | YouTube API | Collect behind-the-scenes content |

### 11.12 Esports & F1 Academy

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_esports_news` | News | 🔴 Not Implemented | F1 Esports site RSS, YouTube | Fetch F1 Esports Series news |
| `get_f1_academy_updates` | News | 🔴 Not Implemented | F1 Academy site, Motorsport.com | Provide F1 Academy updates |
| `get_virtual_gp` | News | 🔴 Not Implemented | F1.com archives, Reddit | Cover virtual GP events |

---

## 12. ADVANCED ANALYSIS

| Tool Name | Category | Status | Requirements | Description |
|-----------|----------|--------|--------------|-------------|
| `get_analysis` | Analysis | ✅ Implemented | FastF1: `Laps.pick_wo_box()`, `pick_accurate()`, statistical analysis | **Comprehensive tool** - Race pace, tire degradation, stint summaries, and consistency analysis |
| `compare_laps` | Analysis | 🔴 Not Implemented | FastF1: Multiple `Lap.get_telemetry()`, `merge_channels()` | Side-by-side comparison of multiple laps |
| `get_fuel_corrected_pace` | Analysis | 🔴 Not Implemented | FastF1: Laps data with stint analysis | Estimate pace adjusted for fuel load |
| `get_qualifying_analysis` | Analysis | 🔴 Not Implemented | FastF1: `Laps.split_qualifying_sessions()` | Detailed Q1/Q2/Q3 progression analysis |
| `get_position_changes` | Analysis | 🔴 Not Implemented | FastF1: `Laps.Position` column over time | Track position changes throughout race |
| `get_gap_analysis` | Analysis | 🔴 Not Implemented | FastF1: Laps with `LapTime`, `Position` | Analyze gaps between drivers over race |
| `get_overtakes` | Analysis | 🔴 Not Implemented | FastF1: `Laps.Position` changes + race control | Detect overtaking maneuvers |

---

## IMPLEMENTATION PRIORITY

### 🔥 HIGH PRIORITY (Core Functionality Extensions)
1. `get_penalties` - Race control filtering
2. `get_investigations` - Race control filtering
3. `get_qualifying_sessions` - Q1/Q2/Q3 split
4. `get_session_status` - Session timing data

### 🟡 MEDIUM PRIORITY (Valuable New Features)
1. `get_car_data` - Telemetry extension
2. `get_position_data` - Racing line analysis
3. `get_lap_weather` - Conditions analysis
4. `get_speed_trace` - Speed analysis
5. `get_gear_usage` - Gear shifting analysis
6. `get_drs_usage` - DRS tracking
7. `get_brake_points` - Braking analysis
8. `get_throttle_trace` - Throttle application

### 🔵 LOW PRIORITY (Archive & Specialized)
1. All Historical category (8.x) - Ergast API
2. All Live category (10.x) - Python version constraints
3. Advanced analysis (A4-A10) - Complex calculations
4. Social media tools - External dependencies

### 🟢 ONGOING (News & Media Expansion)
1. Silly season tools (11.2) - **Next to implement**
2. Technical news (11.4)
3. Business news (11.9)
4. Fan engagement (11.11)

---

## COMPOSABILITY PRINCIPLES

### Tool Design Guidelines
1. **Comprehensive & Multipurpose** - Each tool handles multiple related use cases with flexible parameters
2. **Single Responsibility with Multiple Modes** - Tools do one category of things well, with modes for different data types
3. **Flexible Parameters** - Support optional filtering and customization with sensible defaults
4. **Consistent Returns** - All tools return Pydantic models for type safety
5. **Error Handling** - Graceful degradation with clear error messages
6. **Generic Patterns** - Tools should adapt to future F1 API changes

### Composable Patterns
- **Session + Driver + Lap** filtering cascade
- **Time-based** data retrieval (lap, stint, session, race, season)
- **Comparison** tools (driver vs driver, lap vs lap, stint vs stint)
- **Aggregation** tools (summaries, statistics, trends)
- **Mode-based selection** using `data_type` or `analysis_type` parameters

### Multi-Purpose Tool Strategy
Rather than creating dozens of single-purpose tools, we create comprehensive tools that:
- Accept a `type` or `mode` parameter to switch behavior
- Share common parameters (year, gp, session, driver)
- Return consistent response structures with optional fields
- Reduce total API surface while expanding functionality

### Data Flow
```
FastF1/Ergast API
    ↓
pandas DataFrame (from library)
    ↓
Pydantic Models (type-safe conversion)
    ↓
JSON Response (MCP protocol)
```

---

## NOTES

1. **Pandas Necessity**: All current tools use pandas because FastF1 returns pandas DataFrames. The pandas dependency cannot be removed but is only used for:
   - Iterating over DataFrames (`.iterrows()`)
   - Null checking (`pd.notna()`)
   - No complex data transformations or statistical operations

2. **Pydantic Models**: All responses use Pydantic models for:
   - Type safety
   - Validation
   - JSON serialization
   - Clear API contracts

3. **No Nested Functions**: All helper functions are module-level to reduce complexity

4. **Rate Limiting**: Consider implementing rate limiting for:
   - Ergast API calls
   - News RSS feeds
   - External scraping

5. **Caching**: Implement caching strategies for:
   - FastF1 session data (already built-in)
   - News feeds (TTL-based)
   - Static reference data (long TTL)

6. **Live Timing**: Requires Python 3.8-3.9 constraint (SignalR dependency)

---

## TOTAL TOOL COUNT

- ✅ **Implemented**: 22 tools (16 unique tools, 6 are comprehensive multi-purpose tools)
- 🟡 **Next Up**: 6 tools
- 🔴 **Planned**: 90+ tools
- **Total**: 118+ tools

### Recently Implemented (2025-10-15)
- `get_schedule` - Consolidates 4 schedule tools into one comprehensive tool
- `get_advanced_session_data` - Consolidates 3 session analysis tools
- `get_reference_data` - Consolidates 8 reference/metadata tools
- `get_circuit` - Consolidates 3 track/circuit tools
- `get_analysis` - Consolidates 4 advanced analysis tools

**Note**: The shift to comprehensive, multi-purpose tools reduces total tool count while significantly expanding functionality.

---

**Last Updated**: 2025-10-15
**Version**: 1.1
