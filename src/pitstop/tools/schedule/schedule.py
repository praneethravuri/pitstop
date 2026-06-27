import logging
from datetime import datetime

import pandas as pd
from fastmcp.exceptions import ToolError

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.exceptions import DataSourceError
from pitstop.tools.schedule.models import EventInfo, ScheduleResponse
from pitstop.utils import filter_by_name, paginate, to_tool_error

logger = logging.getLogger("pitstop.schedule")
fastf1_client = FastF1Client()


def _row_to_event_info(row) -> EventInfo:
    """Convert a DataFrame row to EventInfo pydantic model."""
    return EventInfo(
        round_number=int(row["RoundNumber"]) if pd.notna(row.get("RoundNumber")) else None,
        event_name=str(row["EventName"]) if pd.notna(row.get("EventName")) else "",
        country=str(row["Country"]) if pd.notna(row.get("Country")) else "",
        location=str(row["Location"]) if pd.notna(row.get("Location")) else "",
        official_event_name=str(row["OfficialEventName"])
        if pd.notna(row.get("OfficialEventName"))
        else None,
        event_date=str(row["EventDate"]) if pd.notna(row.get("EventDate")) else None,
        event_format=str(row["EventFormat"]) if pd.notna(row.get("EventFormat")) else None,
        session_1_date=str(row["Session1Date"]) if pd.notna(row.get("Session1Date")) else None,
        session_2_date=str(row["Session2Date"]) if pd.notna(row.get("Session2Date")) else None,
        session_3_date=str(row["Session3Date"]) if pd.notna(row.get("Session3Date")) else None,
        session_4_date=str(row["Session4Date"]) if pd.notna(row.get("Session4Date")) else None,
        session_5_date=str(row["Session5Date"]) if pd.notna(row.get("Session5Date")) else None,
        session_1_name=str(row["Session1"]) if pd.notna(row.get("Session1")) else None,
        session_2_name=str(row["Session2"]) if pd.notna(row.get("Session2")) else None,
        session_3_name=str(row["Session3"]) if pd.notna(row.get("Session3")) else None,
        session_4_name=str(row["Session4"]) if pd.notna(row.get("Session4")) else None,
        session_5_name=str(row["Session5"]) if pd.notna(row.get("Session5")) else None,
        is_testing=row.get("EventFormat") == "testing",
    )


def get_schedule(
    year: int,
    include_testing: bool = True,
    round: int | None = None,
    event_name: str | None = None,
    only_remaining: bool = False,
    page: int = 1,
    page_size: int = 30,
) -> ScheduleResponse:
    """
    **PRIMARY TOOL** for ALL Formula 1 calendar and schedule queries. Coverage: current and recent seasons (FastF1).

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
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 30)

    Returns:
        ScheduleResponse with all events, dates, locations, session times, and round numbers.

    Examples:
        get_schedule(2024, only_remaining=True) → All upcoming 2024 races
        get_schedule(2024, event_name="Monaco") → Monaco GP dates and session times
        get_schedule(2024, round=15) → Details for round 15
        get_schedule(2024, include_testing=False) → Race calendar without testing
    """
    try:
        if only_remaining:
            if year != datetime.now().year:
                raise ToolError(
                    f"only_remaining=True only works for the current season ({datetime.now().year}). "
                    f"For {year}, use only_remaining=False."
                )
            schedule_df = fastf1_client.get_events_remaining(
                dt=datetime.now(), include_testing=include_testing
            )
        else:
            schedule_df = fastf1_client.get_event_schedule(
                year=year, include_testing=include_testing
            )

        events_data = schedule_df.to_dict("records")

        if round is not None:
            events_data = [e for e in events_data if e.get("RoundNumber") == round]

        if event_name is not None:
            events_data = filter_by_name(
                events_data, event_name, ["EventName", "Country", "Location"]
            )

        events_list = [_row_to_event_info(row) for row in events_data]
        paged, meta = paginate(events_list, page, page_size)

        return ScheduleResponse(
            year=year,
            total_events=meta.total_items,
            include_testing=include_testing,
            events=paged,
            round_filter=round,
            event_name_filter=event_name,
            only_remaining=only_remaining,
            pagination=meta,
        )

    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("get_schedule", exc.source, exc)
    except Exception as exc:
        raise to_tool_error("get_schedule", "fastf1", exc)
