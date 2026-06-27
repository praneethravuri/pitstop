import logging
from typing import Literal

from pitstop.clients import openf1_client
from pitstop.exceptions import DataSourceError
from pitstop.models.common import PartialErrors
from pitstop.tools.live.models import (
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
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.live")

# ponytail: dispatch eliminates 5 near-identical fetch+map blocks
DISPATCH: dict[str, tuple[str, type]] = {
    "intervals": ("/intervals", IntervalData),
    "pit_stops": ("/pit", PitStopData),
    "radio": ("/team_radio", TeamRadioMessage),
    "stints": ("/stints", StintData),
    "race_control": ("/race_control", RaceControlMessage),
}


def get_live_data(
    data_types: list[Literal["intervals", "pit_stops", "radio", "stints", "race_control"]],
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: int | None = None,
    compound: str | None = None,  # stints only
    flag: str | None = None,  # race_control only
    category: str | None = None,  # race_control only
    page: int = 1,
    page_size: int = 50,
) -> LiveDataResponse:
    """
    **PRIMARY TOOL** for Real-Time/Live Formula 1 Data (2023-Present). Coverage: 2023–present (OpenF1).

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
        page: Page number for paginated results (default: 1)
        page_size: Items per page (default: 50)

    Returns:
        LiveDataResponse containing requested data.
    """
    try:
        sessions = openf1_client.query(
            "/sessions", year=year, country_name=country, session_name=session_name
        )
    except DataSourceError as e:
        raise to_tool_error("get_live_data", "openf1", e)

    if not sessions:
        return LiveDataResponse(year=year, country=country, session_name=session_name)

    session_key = sessions[0]["session_key"]
    response = LiveDataResponse(year=year, country=country, session_name=session_name)
    partial_errors = PartialErrors()

    for dtype in data_types:
        if dtype not in DISPATCH:
            logger.warning("Unknown data_type %r — skipped", dtype)
            continue

        endpoint, Model = DISPATCH[dtype]
        filters: dict = {"session_key": session_key, "driver_number": driver_number}
        if dtype == "stints":
            filters["compound"] = compound
        if dtype == "race_control":
            filters["flag"] = flag
            filters["category"] = category

        try:
            raw = openf1_client.query(endpoint, **filters)
            all_items = [Model.model_validate(d) for d in raw]
        except (DataSourceError, Exception) as e:
            partial_errors.add(dtype, "openf1", e)
            continue
        items, _ = paginate(all_items, page, page_size)

        if dtype == "intervals":
            response.intervals = IntervalsResponse(
                year=year,
                country=country,
                session_name=session_name,
                intervals=items,
                total_data_points=len(all_items),
            )
        elif dtype == "pit_stops":
            fastest = min(p.pit_duration for p in all_items) if all_items else None
            slowest = max(p.pit_duration for p in all_items) if all_items else None
            avg = sum(p.pit_duration for p in all_items) / len(all_items) if all_items else None
            response.pit_stops = PitStopsResponse(
                year=year,
                country=country,
                session_name=session_name,
                pit_stops=items,
                total_pit_stops=len(all_items),
                fastest_stop=fastest,
                slowest_stop=slowest,
                average_duration=avg,
            )
        elif dtype == "radio":
            response.radio = TeamRadioResponse(
                year=year,
                country=country,
                session_name=session_name,
                messages=items,
                total_messages=len(all_items),
            )
        elif dtype == "stints":
            response.stints = StintsResponse(
                year=year,
                country=country,
                session_name=session_name,
                stints=items,
                total_stints=len(all_items),
            )
        elif dtype == "race_control":
            response.race_control = RaceControlResponse(
                year=year,
                country=country,
                session_name=session_name,
                messages=items,
                total_messages=len(all_items),
            )

    if partial_errors.has_errors:
        response.partial_errors = partial_errors

    return response
