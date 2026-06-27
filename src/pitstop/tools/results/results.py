"""
PRIMARY tool for historical race results (1950–present via Jolpica).
Supports race results, qualifying, sprint, lap times, pit stops, and status codes.
Coverage: 1950–present; lap-timing detail is sparser before ~1994.
"""

import logging
import math
from typing import Literal

from fastmcp.exceptions import ToolError

from pitstop.clients import jolpica_client
from pitstop.exceptions import DataSourceError
from pitstop.models.common import PageMeta
from pitstop.tools.results.models import (
    FinishStatus,
    LapTiming,
    PitStopRecord,
    QualifyingResult,
    RaceResult,
    ResultsResponse,
    SprintResult,
)
from pitstop.utils import to_tool_error

logger = logging.getLogger("pitstop.results")


# ponytail: returns None for strict Pydantic optional fields; safe_int/safe_float exist but default to 0
def _int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _float(v) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _page_meta(total: int, page: int, page_size: int) -> PageMeta:
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PageMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


def get_results(
    year: int,
    round: int | str,
    result_type: Literal["race", "qualifying", "sprint", "laps", "pitstops", "status"] = "race",
    driver: str | None = None,
    page: int = 1,
    page_size: int = 30,
) -> ResultsResponse:
    """
    PRIMARY tool for historical race results (1950–present via Jolpica).
    Supports race results, qualifying, sprint, lap times, pit stops, and status codes.
    Coverage: 1950–present; lap-timing detail is sparser before ~1994.

    Args:
        year: Season year (1950-present)
        round: Round number or "last" / "next"
        result_type: Type of results to retrieve
        driver: Filter by driver id (e.g. "hamilton")
        page: Page number (1-indexed)
        page_size: Items per page
    """
    try:
        offset = (page - 1) * page_size
        extra: dict = {"limit": page_size, "offset": offset}

        if driver:
            if result_type == "status":
                raise ToolError("driver filter is not supported for result_type='status'")
            # Jolpica filters by driver via URL path, not query params
            _endpoint = {
                "race": "results",
                "qualifying": "qualifying",
                "sprint": "sprint",
                "laps": "laps",
                "pitstops": "pitstops",
            }[result_type]
            path = f"{year}/{round}/drivers/{driver}/{_endpoint}"
        else:
            path = f"{year}/{round}/{result_type}"

        data = jolpica_client.query(path, **extra)
        mr = data.get("MRData") or {}
        total = _int(mr.get("total", 0)) or 0
        pagination = _page_meta(total, page, page_size)

        race_name: str | None = None
        races = mr.get("RaceTable", {}).get("Races", [])
        if races:
            race_name = races[0].get("raceName")

        race_results = None
        qualifying_results = None
        sprint_results = None
        laps_list = None
        pit_stops = None
        statuses = None

        if result_type == "race":
            raw = races[0].get("Results", []) if races else []
            race_results = [_parse_race_result(r) for r in raw]

        elif result_type == "qualifying":
            raw = races[0].get("QualifyingResults", []) if races else []
            qualifying_results = [_parse_qualifying(r) for r in raw]

        elif result_type == "sprint":
            raw = races[0].get("SprintResults", []) if races else []
            sprint_results = [_parse_sprint(r) for r in raw]

        elif result_type == "laps":
            raw_laps = races[0].get("Laps", []) if races else []
            laps_list = []
            for lap in raw_laps:
                lap_num = _int(lap.get("number")) or 0
                for timing in lap.get("Timings", []):
                    laps_list.append(
                        LapTiming(
                            lap_number=lap_num,
                            driver_id=str(timing.get("driverId", "")),
                            position=_int(timing.get("position")),
                            time=timing.get("time"),
                        )
                    )

        elif result_type == "pitstops":
            raw = races[0].get("PitStops", []) if races else []
            pit_stops = [
                PitStopRecord(
                    lap=_int(r.get("lap")) or 0,
                    driver_id=str(r.get("driverId", "")),
                    stop=_int(r.get("stop")) or 0,
                    time_of_day=r.get("time"),
                    duration=r.get("duration"),
                )
                for r in raw
            ]

        elif result_type == "status":
            raw = mr.get("StatusTable", {}).get("Status", [])
            statuses = [
                FinishStatus(
                    status_id=str(r.get("statusId", "")),
                    count=_int(r.get("count")) or 0,
                    status=str(r.get("status", "")),
                )
                for r in raw
            ]

        return ResultsResponse(
            year=year,
            round=round,
            race_name=race_name,
            result_type=result_type,
            race_results=race_results,
            qualifying_results=qualifying_results,
            sprint_results=sprint_results,
            laps=laps_list,
            pit_stops=pit_stops,
            statuses=statuses,
            total_records=total,
            pagination=pagination,
        )

    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("get_results", "jolpica", exc)
    except Exception as exc:
        raise to_tool_error("get_results", "jolpica", exc)


def _parse_race_result(r: dict) -> RaceResult:
    driver = r.get("Driver", {})
    constructor = r.get("Constructor", {})
    fl = r.get("FastestLap", {})
    return RaceResult(
        position=_int(r.get("position")),
        driver_id=str(driver.get("driverId", "")),
        driver_name=f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
        constructor=str(constructor.get("name", "")),
        laps=_int(r.get("laps")),
        time=r.get("Time", {}).get("time") if r.get("Time") else None,
        status=r.get("status"),
        points=_float(r.get("points")),
        grid=_int(r.get("grid")),
        fastest_lap_rank=_int(fl.get("rank")) if fl else None,
        fastest_lap_time=fl.get("Time", {}).get("time") if fl and fl.get("Time") else None,
    )


def _parse_qualifying(r: dict) -> QualifyingResult:
    driver = r.get("Driver", {})
    constructor = r.get("Constructor", {})
    return QualifyingResult(
        position=_int(r.get("position")),
        driver_id=str(driver.get("driverId", "")),
        driver_name=f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
        constructor=str(constructor.get("name", "")),
        q1=r.get("Q1"),
        q2=r.get("Q2"),
        q3=r.get("Q3"),
    )


def _parse_sprint(r: dict) -> SprintResult:
    driver = r.get("Driver", {})
    constructor = r.get("Constructor", {})
    return SprintResult(
        position=_int(r.get("position")),
        driver_id=str(driver.get("driverId", "")),
        driver_name=f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
        constructor=str(constructor.get("name", "")),
        laps=_int(r.get("laps")),
        time=r.get("Time", {}).get("time") if r.get("Time") else None,
        status=r.get("status"),
        points=_float(r.get("points")),
    )
