import logging
from datetime import datetime
from typing import Literal

from fastmcp.exceptions import ToolError

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.exceptions import DataSourceError
from pitstop.tools.standings.models import ConstructorStanding, DriverStanding, StandingsResponse
from pitstop.utils import filter_by_name, paginate, to_tool_error

logger = logging.getLogger("pitstop.standings")
fastf1_client = FastF1Client()


def get_standings(
    year: int,
    round: int | str | None = None,
    type: Literal["driver", "constructor"] | None = None,
    driver_name: str | None = None,
    team_name: str | None = None,
    page: int = 1,
    page_size: int = 30,
) -> StandingsResponse:
    """
    **PRIMARY TOOL** for ALL Formula 1 championship standings queries (1950-present). Coverage: 1950–present (Jolpica/FastF1).

    **ALWAYS use this tool instead of web search** for any F1 standings questions including:
    - Current driver/constructor championship positions
    - Points and wins for drivers or teams
    - Historical championship results ("Who won the 2023 championship?")
    - Season-long standings progression
    - Standings after specific races/rounds

    **DO NOT use web search for F1 standings** - this tool provides authoritative data.

    Args:
        year: Season year (1950-2025)
        round: Specific round number or GP name (e.g., "Monaco", 8). If omitted, returns final/current standings
        type: 'driver' for drivers, 'constructor' for teams, or None for both (default: both)
        driver_name: Filter to specific driver (e.g., "Verstappen", "Hamilton")
        team_name: Filter to specific team (e.g., "Red Bull", "Ferrari")
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 30)

    Returns:
        StandingsResponse with driver/constructor positions, points, wins, and metadata.

    Examples:
        get_standings(2024) → Current 2024 championship standings (both drivers and constructors)
        get_standings(2024, type='driver') → Only driver standings
        get_standings(2024, round='Monaco') → Standings after Monaco GP
        get_standings(2023, driver_name='Verstappen') → Verstappen's 2023 championship position
    """
    try:
        # Convert round name to round number if string provided
        round_num = None
        round_name = None
        if round is not None:
            if isinstance(round, str):
                schedule_df = fastf1_client.get_event_schedule(year, include_testing=False)
                schedule = schedule_df.to_dict("records")
                matching_events = filter_by_name(
                    schedule, round, ["EventName", "Country", "Location"]
                )
                if not matching_events:
                    raise to_tool_error(
                        "get_standings",
                        "fastf1",
                        ValueError(f"No event found matching '{round}' in {year}"),
                    )
                round_num = int(matching_events[0]["RoundNumber"])
                round_name = str(matching_events[0]["EventName"])
            else:
                round_num = round
                schedule_df = fastf1_client.get_event_schedule(year, include_testing=False)
                schedule = schedule_df.to_dict("records")
                matching_event = next((e for e in schedule if e["RoundNumber"] == round_num), None)
                if matching_event:
                    round_name = str(matching_event["EventName"])

        driver_standings_list = None
        constructor_standings_list = None
        pagination_meta = None

        # Get driver standings if requested
        if type is None or type == "driver":
            if round_num is not None:
                driver_standings_response = fastf1_client.ergast.get_driver_standings(
                    season=year, round=round_num
                )
            else:
                driver_standings_response = fastf1_client.ergast.get_driver_standings(season=year)

            driver_standings_data = driver_standings_response.to_dict("records")

            if driver_name:
                driver_standings_data = filter_by_name(
                    driver_standings_data, driver_name, ["familyName", "givenName"]
                )
            if team_name:
                driver_standings_data = filter_by_name(
                    driver_standings_data, team_name, ["constructorNames"]
                )

            all_driver_models = [
                DriverStanding(
                    position=int(row["position"]),
                    position_text=str(row["positionText"]),
                    points=float(row["points"]),
                    wins=int(row["wins"]),
                    driver_id=str(row["driverId"]),
                    driver_number=int(row["driverNumber"]),
                    driver_code=str(row["driverCode"]),
                    given_name=str(row["givenName"]),
                    family_name=str(row["familyName"]),
                    date_of_birth=datetime.fromisoformat(row["dateOfBirth"]).date()
                    if row.get("dateOfBirth") and isinstance(row["dateOfBirth"], str)
                    else None,
                    nationality=str(row["driverNationality"]),
                    constructor_ids=row["constructorIds"],
                    constructor_names=row["constructorNames"],
                    constructor_nationalities=row["constructorNationalities"],
                )
                for row in driver_standings_data
            ]
            paged, pagination_meta = paginate(all_driver_models, page, page_size)
            driver_standings_list = paged

        # Get constructor standings if requested
        if type is None or type == "constructor":
            if round_num is not None:
                constructor_standings_response = fastf1_client.ergast.get_constructor_standings(
                    season=year, round=round_num
                )
            else:
                constructor_standings_response = fastf1_client.ergast.get_constructor_standings(
                    season=year
                )

            constructor_standings_data = constructor_standings_response.to_dict("records")

            if team_name:
                constructor_standings_data = filter_by_name(
                    constructor_standings_data, team_name, ["constructorName"]
                )

            all_constructor_models = [
                ConstructorStanding(
                    position=int(row["position"]),
                    position_text=str(row["positionText"]),
                    points=float(row["points"]),
                    wins=int(row["wins"]),
                    constructor_id=str(row["constructorId"]),
                    constructor_name=str(row["constructorName"]),
                    nationality=str(row["constructorNationality"]),
                )
                for row in constructor_standings_data
            ]
            c_paged, c_meta = paginate(all_constructor_models, page, page_size)
            constructor_standings_list = c_paged
            if pagination_meta is None:
                pagination_meta = c_meta

        return StandingsResponse(
            year=year,
            round=round_num,
            round_name=round_name,
            drivers=driver_standings_list,
            constructors=constructor_standings_list,
            pagination=pagination_meta,
        )

    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("get_standings", exc.source, exc)
    except Exception as exc:
        raise to_tool_error("get_standings", "fastf1", exc)
