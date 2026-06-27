import logging
from typing import Literal

from pydantic import BaseModel

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.models.common import PageMeta, PartialErrors
from pitstop.tools.session.models import (
    LapInfo,
    SessionDetailsResponse,
    SessionDriversResponse,
    SessionInfo,
    SessionResult,
    SessionResultsResponse,
    SessionWeather,
    SessionWeatherDataResponse,
    WeatherDataPoint,
)
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.session")

# ponytail: module-level singleton; swap for shared factory when clients/__init__ ships it
fastf1_client = FastF1Client()


class SessionDataResponse(BaseModel):
    details: SessionDetailsResponse | None = None
    results: SessionResultsResponse | None = None
    drivers: SessionDriversResponse | None = None
    weather: SessionWeatherDataResponse | None = None
    pagination: PageMeta | None = None
    partial_errors: PartialErrors | None = None


def get_session_data(
    year: int,
    gp: str | int,
    session: str,
    includes: list[Literal["details", "results", "drivers", "weather"]] = ["details", "results"],
    page: int = 1,
    page_size: int = 50,
) -> SessionDataResponse:
    """
    Get comprehensive data for a Formula 1 session.

    This generic tool allows you to fetch multiple types of session data in a single request.

    Args:
        year: Season year (e.g., 2024)
        gp: Grand Prix name (e.g., "Monaco") or round number
        session: Session identifier (e.g., "R", "Q", "FP1")
        includes: List of data to include. Options: "details", "results", "drivers", "weather".
                 Default: ["details", "results"]
        page: Page number (1-indexed)
        page_size: Items per page
    """
    try:
        session_obj = fastf1_client.get_session(year, gp, session)
        session_obj.load()
    except Exception as exc:
        raise to_tool_error("get_session_data", "fastf1", exc)

    response = SessionDataResponse()

    if "details" in includes:
        fastest_lap = session_obj.laps.pick_fastest() if len(session_obj.laps) > 0 else None

        rainfall = False
        if session_obj.weather_data is not None and not session_obj.weather_data.empty:
            rainfall = session_obj.weather_data["Rainfall"].any()

        response.details = SessionDetailsResponse(
            session_info=SessionInfo(
                name=session_obj.name,
                session_type=session,
                event_name=session_obj.event.EventName,
                location=session_obj.event.Location,
                country=session_obj.event.Country,
                circuit_name=session_obj.event.EventName,
                year=year,
                round=session_obj.event.RoundNumber,
                session_date=session_obj.date,
            ),
            results=[],
            weather=SessionWeather(
                air_temp=session_obj.weather_data["AirTemp"].mean()
                if len(session_obj.weather_data) > 0
                else None,
                track_temp=session_obj.weather_data["TrackTemp"].mean()
                if len(session_obj.weather_data) > 0
                else None,
                humidity=session_obj.weather_data["Humidity"].mean()
                if len(session_obj.weather_data) > 0
                else None,
                rainfall=bool(rainfall),
            ),
            fastest_lap=LapInfo(
                driver=fastest_lap["Driver"],
                lap_time=str(fastest_lap["LapTime"]),
                lap_number=int(fastest_lap["LapNumber"]),
                compound=fastest_lap.get("Compound"),
            )
            if fastest_lap is not None
            else None,
            total_laps=session_obj.total_laps
            if hasattr(session_obj, "total_laps")
            else len(session_obj.laps),
        )

    if "results" in includes:
        res_list = []
        partial = PartialErrors()
        for driver in session_obj.drivers:
            try:
                d_info = session_obj.get_driver(driver)
                res_list.append(
                    SessionResult(
                        position=d_info.get("Position"),
                        driver_number=str(d_info["DriverNumber"]),
                        broadcast_name=d_info.get("BroadcastName", str(d_info["Abbreviation"])),
                        abbreviation=str(d_info["Abbreviation"]),
                        team_name=d_info.get("TeamName", ""),
                        team_color=f"#{d_info.get('TeamColor', '')}",
                        first_name=d_info.get("FirstName"),
                        last_name=d_info.get("LastName"),
                        full_name=d_info.get("FullName"),
                        status=str(d_info.get("Status", "")),
                        points=d_info.get("Points"),
                    )
                )
            except Exception as exc:
                logger.warning("Driver %s result fetch failed: %s", driver, exc)
                partial.add(str(driver), "fastf1", exc)

        paged, meta = paginate(res_list, page, page_size)
        response.results = SessionResultsResponse(
            session_name=session_obj.name,
            event_name=session_obj.event.EventName,
            results=paged,
            total_drivers=meta.total_items,
        )
        response.pagination = meta
        if partial.has_errors:
            response.partial_errors = partial

    if "drivers" in includes:
        drv_list = list(session_obj.drivers)
        paged, meta = paginate(drv_list, page, page_size)
        response.drivers = SessionDriversResponse(
            session_name=session_obj.name,
            event_name=session_obj.event.EventName,
            year=year,
            drivers=paged,
            total_drivers=meta.total_items,
        )
        if response.pagination is None:
            response.pagination = meta

    if "weather" in includes:
        w_points = []
        if session_obj.weather_data is not None:
            for _idx, row in session_obj.weather_data.iterrows():
                w_points.append(
                    WeatherDataPoint(
                        time=str(row["Time"]),
                        air_temp=float(row["AirTemp"]),
                        track_temp=float(row["TrackTemp"]),
                        humidity=float(row["Humidity"]),
                        pressure=float(row["Pressure"]),
                        wind_speed=float(row["WindSpeed"]),
                        rainfall=bool(row["Rainfall"]),
                    )
                )

        response.weather = SessionWeatherDataResponse(
            session_name=session_obj.name,
            event_name=session_obj.event.EventName,
            weather_data=w_points,
            total_points=len(w_points),
        )

    return response
