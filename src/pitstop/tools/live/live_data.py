from typing import Literal

from pitstop.clients.openf1_client import (
    get_intervals,
    get_pit_stops,
    get_race_control,
    get_sessions,
    get_stints,
    get_team_radio,
)
from pitstop.models.live.openf1 import (
    IntervalData,
    IntervalsResponse,
    LiveDataResponse,
    PitStopData,
    PitStopsResponse,
    RaceControlMessage,
    RaceControlResponse,
    StintData,
    StintsResponse,
    TeamRadioMessage,
    TeamRadioResponse,
)


def get_live_data(
    data_types: list[Literal["intervals", "pit_stops", "radio", "stints", "race_control"]],
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: int | None = None,
    # Specific filters
    compound: str | None = None, # For stints
    flag: str | None = None, # For race control
    category: str | None = None, # For race control
) -> LiveDataResponse:
    """
    **PRIMARY TOOL** for Real-Time/Live Formula 1 Data (2023-Present).
    
    Consolidates multiple live data streams into a single request.
    
    Args:
        data_types: List of data types to fetch. Options:
                   - 'intervals': Live gaps to leader and car ahead
                   - 'pit_stops': Pit stop timing and history
                   - 'radio': Team radio audio and transcripts
                   - 'stints': Tire usage and stint history
                   - 'race_control': Race control messages (flags, penalties, SC)
        year: Season year (e.g., 2024)
        country: Country name (e.g., "Monaco")
        session_name: Session name (default: "Race")
        driver_number: Filter all data by driver number (e.g., 1, 44, 16)
        compound: (Stints only) Filter by tire compound (e.g., 'SOFT')
        flag: (Race Control only) Filter by flag type
        category: (Race Control only) Filter by message category
        
    Returns:
        LiveDataResponse containing requested data.
    """
    
    # 1. Resolve Session Key
    # We always need to resolve the session unless we want to support passing session_key directly,
    # but for simplicity/consistency with other tools, we stick to year/country/session_name lookup.
    
    sessions = get_sessions(year=year, country_name=country, session_name=session_name)
    if not sessions:
        # Return empty response with metadata we have
        return LiveDataResponse(
            year=year,
            country=country,
            session_name=session_name
        )
        
    session = sessions[0]
    session_key = session['session_key']
    
    response = LiveDataResponse(
        year=year,
        country=country,
        session_name=session_name
    )
    
    # 2. Fetch Requested Data Types
    
    # Intervals
    if "intervals" in data_types:
        data = get_intervals(session_key=session_key, driver_number=driver_number)
        response.intervals = IntervalsResponse(
            year=year,
            country=country,
            session_name=session_name,
            intervals=[
                IntervalData(
                    date=d['date'],
                    driver_number=d['driver_number'],
                    gap_to_leader=d.get('gap_to_leader'),
                    interval=d.get('interval'),
                    session_key=d['session_key'],
                    meeting_key=d['meeting_key']
                ) for d in data
            ],
            total_data_points=len(data)
        )
        
    # Pit Stops
    if "pit_stops" in data_types:
        data = get_pit_stops(session_key=session_key, driver_number=driver_number)
        
        pit_stops = [
            PitStopData(
                date=d['date'],
                driver_number=d['driver_number'],
                lap_number=d['lap_number'],
                pit_duration=d['pit_duration'],
                session_key=d['session_key'],
                meeting_key=d['meeting_key']
            ) for d in data
        ]
        
        # Calculate stats
        fastest = min([p.pit_duration for p in pit_stops]) if pit_stops else None
        slowest = max([p.pit_duration for p in pit_stops]) if pit_stops else None
        avg = sum([p.pit_duration for p in pit_stops]) / len(pit_stops) if pit_stops else None

        response.pit_stops = PitStopsResponse(
            year=year,
            country=country,
            session_name=session_name,
            pit_stops=pit_stops,
            total_pit_stops=len(pit_stops),
            fastest_stop=fastest,
            slowest_stop=slowest,
            average_duration=avg
        )

    # Radio
    if "radio" in data_types:
        data = get_team_radio(session_key=session_key, driver_number=driver_number)
        response.radio = TeamRadioResponse(
            year=year,
            country=country,
            session_name=session_name,
            messages=[
                TeamRadioMessage(
                    date=d['date'],
                    driver_number=d['driver_number'],
                    session_key=d['session_key'],
                    meeting_key=d['meeting_key'],
                    recording_url=d.get('recording_url')
                ) for d in data
            ],
            total_messages=len(data)
        )
        
    # Stints
    if "stints" in data_types:
        data = get_stints(session_key=session_key, driver_number=driver_number, compound=compound)
        response.stints = StintsResponse(
            year=year,
            country=country,
            session_name=session_name,
            stints=[
                StintData(
                    stint_number=d['stint_number'],
                    driver_number=d['driver_number'],
                    compound=d['compound'],
                    lap_start=d.get('lap_start'),
                    lap_end=d.get('lap_end'),
                    tyre_age_at_start=d.get('tyre_age_at_start')
                ) for d in data
            ],
            total_stints=len(data)
        )

    # Race Control
    if "race_control" in data_types:
        # Calls the method we verified/added to OpenF1Client
        data = get_race_control(
            session_key=session_key,
            driver_number=driver_number,
            flag=flag,
            category=category,
        )
        response.race_control = RaceControlResponse(
            year=year,
            country=country,
            session_name=session_name,
            messages=[
                RaceControlMessage(
                    date=d['date'],
                    category=d['category'],
                    message=d['message'],
                    driver_number=d.get('driver_number'),
                    flag=d.get('flag'),
                    lap_number=d.get('lap_number'),
                    scope=d.get('scope'),
                    sector=d.get('sector')
                ) for d in data
            ],
            total_messages=len(data)
        )
        
    return response
