from clients.fastf1_client import FastF1Client
from typing import Optional, Union
from models.schedule import ScheduleResponse, EventInfo
from datetime import datetime
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def _row_to_event_info(row) -> EventInfo:
    """Convert a DataFrame row to EventInfo pydantic model."""
    return EventInfo(
        round_number=int(row['RoundNumber']) if pd.notna(row.get('RoundNumber')) else None,
        event_name=str(row['EventName']) if pd.notna(row.get('EventName')) else "",
        country=str(row['Country']) if pd.notna(row.get('Country')) else "",
        location=str(row['Location']) if pd.notna(row.get('Location')) else "",
        official_event_name=str(row['OfficialEventName']) if pd.notna(row.get('OfficialEventName')) else None,
        event_date=str(row['EventDate']) if pd.notna(row.get('EventDate')) else None,
        event_format=str(row['EventFormat']) if pd.notna(row.get('EventFormat')) else None,
        session_1_date=str(row['Session1Date']) if pd.notna(row.get('Session1Date')) else None,
        session_2_date=str(row['Session2Date']) if pd.notna(row.get('Session2Date')) else None,
        session_3_date=str(row['Session3Date']) if pd.notna(row.get('Session3Date')) else None,
        session_4_date=str(row['Session4Date']) if pd.notna(row.get('Session4Date')) else None,
        session_5_date=str(row['Session5Date']) if pd.notna(row.get('Session5Date')) else None,
        session_1_name=str(row['Session1']) if pd.notna(row.get('Session1')) else None,
        session_2_name=str(row['Session2']) if pd.notna(row.get('Session2')) else None,
        session_3_name=str(row['Session3']) if pd.notna(row.get('Session3')) else None,
        session_4_name=str(row['Session4']) if pd.notna(row.get('Session4')) else None,
        session_5_name=str(row['Session5']) if pd.notna(row.get('Session5')) else None,
        is_testing=bool(row.get('EventFormat') == 'testing') if pd.notna(row.get('EventFormat')) else False,
    )


def get_schedule(
    year: int,
    include_testing: bool = True,
    round: Optional[int] = None,
    event_name: Optional[str] = None,
    only_remaining: bool = False,
) -> ScheduleResponse:
    """
    **PRIMARY TOOL** for ALL Formula 1 calendar and schedule queries.

    **ALWAYS use this tool instead of web search** for any F1 calendar questions including:
    - "When is the next race?" / upcoming race dates
    - Full season calendar and race schedule
    - Specific GP dates, times, and locations
    - Session schedules (practice, qualifying, race times)
    - Track/circuit information
    - Testing sessions and dates

    **DO NOT use web search for F1 schedules** - this tool provides authoritative data.

    Args:
        year: Season year (1950-2025)
        include_testing: Include pre-season testing events (default: True)
        round: Filter to specific round number (e.g., 5 for round 5)
        event_name: Filter by GP name (e.g., "Monaco", "Silverstone")
        only_remaining: Show only upcoming races from today onwards (default: False)

    Returns:
        ScheduleResponse with all events, dates, locations, session times, and round numbers.

    Examples:
        get_schedule(2024, only_remaining=True) → All upcoming 2024 races
        get_schedule(2024, event_name="Monaco") → Monaco GP dates and session times
        get_schedule(2024, round=15) → Details for round 15
        get_schedule(2024, include_testing=False) → Race calendar without testing
    """
    # Get full event schedule
    if only_remaining:
        schedule_df = fastf1_client.get_events_remaining(
            dt=datetime.now(),
            include_testing=include_testing
        )
    else:
        schedule_df = fastf1_client.get_event_schedule(
            year=year,
            include_testing=include_testing
        )

    # Convert to list of dicts
    events_data = schedule_df.to_dict('records')

    # Apply round filter if specified
    if round is not None:
        events_data = [e for e in events_data if e.get('RoundNumber') == round]

    # Apply event name filter if specified
    if event_name is not None:
        events_data = [
            e for e in events_data
            if event_name.lower() in e.get('EventName', '').lower()
            or event_name.lower() in e.get('Country', '').lower()
            or event_name.lower() in e.get('Location', '').lower()
        ]

    # Convert to Pydantic models
    events_list = [_row_to_event_info(row) for row in events_data]

    return ScheduleResponse(
        year=year,
        total_events=len(events_list),
        include_testing=include_testing,
        events=events_list,
        round_filter=round,
        event_name_filter=event_name,
        only_remaining=only_remaining,
    )


if __name__ == "__main__":
    # Test schedule functionality
    print("Testing get_schedule with different scenarios...")

    # Test 1: Get full 2024 calendar
    print("\n1. Getting full 2024 F1 calendar:")
    schedule = get_schedule(2024, include_testing=False)
    print(f"   Total events: {schedule.total_events}")
    if schedule.events:
        print(f"   First event: {schedule.events[0].event_name} in {schedule.events[0].country}")

    # Test 2: Get Monaco GP details
    print("\n2. Getting Monaco GP 2024 details:")
    monaco = get_schedule(2024, event_name='Monaco')
    if monaco.events:
        event = monaco.events[0]
        print(f"   Event: {event.event_name}")
        print(f"   Location: {event.location}, {event.country}")
        print(f"   Round: {event.round_number}")
        print(f"   Sessions: {event.session_1_name}, {event.session_2_name}, {event.session_3_name}")

    # Test 3: Get remaining events
    print("\n3. Getting remaining 2024 events:")
    remaining = get_schedule(2024, only_remaining=True, include_testing=False)
    print(f"   Remaining events: {remaining.total_events}")

    # Test JSON serialization
    print(f"\n   JSON: {schedule.model_dump_json()[:150]}...")
