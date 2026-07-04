import logging
import math

import pandas as pd
from pydantic import BaseModel

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.models.common import PageMeta, PartialErrors
from pitstop.tools.telemetry.models import (
    LapTelemetryResponse,
    TelemetryComparisonResponse,
    TelemetryPoint,
)
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.telemetry")

# ponytail: module-level singleton; swap for shared factory when clients/__init__ ships it
fastf1_client = FastF1Client()


class TelemetryDataResponse(BaseModel):
    drivers_telemetry: list[LapTelemetryResponse]
    comparison: TelemetryComparisonResponse | None = None
    pagination: PageMeta | None = None
    partial_errors: PartialErrors | None = None


def get_telemetry_data(
    year: int,
    gp: str | int,
    session: str,
    drivers: list[str | int],
    lap_numbers: list[int] | None = None,
    max_points: int = 100,
    page: int = 1,
    page_size: int = 20,
) -> TelemetryDataResponse:
    """
    Get telemetry data for one or more drivers. Coverage: 2018–present (FastF1).

    Args:
        year: Season year
        gp: Grand Prix name or round
        session: Session identifier
        drivers: List of driver identifiers (e.g. ["VER", "HAM"])
        lap_numbers: Optional list of lap numbers corresponding to drivers.
                     If None or matching index is None, fetches fastest lap.
        max_points: Cap telemetry points per lap via uniform downsampling
                    (default 100 ≈ one point per 40-70 m of track). Raise for
                    finer resolution, 0 to disable.
        page: Page number (1-indexed)
        page_size: Items per page
    """
    try:
        session_obj = fastf1_client.get_session(year, gp, session)
        session_obj.load()
    except Exception as exc:
        raise to_tool_error("get_telemetry_data", "fastf1", exc)

    telemetry_list = []
    partial = PartialErrors()

    for i, driver in enumerate(drivers):
        lap_num = lap_numbers[i] if lap_numbers and i < len(lap_numbers) else None

        try:
            driver_laps = session_obj.laps.pick_driver(driver)
            if len(driver_laps) == 0:
                partial.add(str(driver), "fastf1", Exception("no laps found"))
                continue

            if lap_num is None:
                selected_lap = driver_laps.pick_fastest()
            else:
                laps = driver_laps[driver_laps["LapNumber"] == lap_num]
                selected_lap = laps.iloc[0] if not laps.empty else None

            if selected_lap is None:
                partial.add(str(driver), "fastf1", Exception("no laps found"))
                continue

            tel_data = selected_lap.get_telemetry()
            if max_points and len(tel_data) > max_points:
                step = math.ceil(len(tel_data) / max_points)
                tel_data = tel_data.iloc[::step]

            points = []
            for _, row in tel_data.iterrows():
                points.append(
                    TelemetryPoint(
                        session_time=str(row["SessionTime"]),
                        rpm=int(row["RPM"]) if pd.notna(row.get("RPM")) else None,
                        speed=float(row["Speed"]) if pd.notna(row.get("Speed")) else None,
                        throttle=float(row["Throttle"]) if pd.notna(row.get("Throttle")) else None,
                        brake=float(row["Brake"]) if pd.notna(row.get("Brake")) else None,
                        n_gear=int(row["nGear"]) if pd.notna(row.get("nGear")) else None,
                        drs=int(row["DRS"]) if pd.notna(row.get("DRS")) else None,
                        distance=float(row["Distance"]) if pd.notna(row.get("Distance")) else None,
                        x=float(row["X"]) if pd.notna(row.get("X")) else None,
                        y=float(row["Y"]) if pd.notna(row.get("Y")) else None,
                        z=float(row["Z"]) if pd.notna(row.get("Z")) else None,
                    )
                )

            telemetry_list.append(
                LapTelemetryResponse(
                    session_name=session_obj.name,
                    event_name=session_obj.event.EventName,
                    driver=str(driver),
                    lap_number=int(selected_lap["LapNumber"]),
                    telemetry=points,
                    total_points=len(points),
                    lap_time=str(selected_lap["LapTime"]),
                )
            )
        except Exception as exc:
            logger.warning("Driver %s telemetry failed: %s", driver, exc)
            partial.add(str(driver), "fastf1", exc)

    comparison = None
    if len(telemetry_list) == 2:
        d1, d2 = telemetry_list[0], telemetry_list[1]
        comparison = TelemetryComparisonResponse(
            session_name=d1.session_name,
            event_name=d1.event_name,
            driver1=d1.driver,
            driver1_lap=d1.lap_number,
            driver1_telemetry=d1.telemetry,
            driver1_lap_time=d1.lap_time,
            driver2=d2.driver,
            driver2_lap=d2.lap_number,
            driver2_telemetry=d2.telemetry,
            driver2_lap_time=d2.lap_time,
        )

    paged, meta = paginate(telemetry_list, page, page_size)
    return TelemetryDataResponse(
        drivers_telemetry=paged,
        comparison=comparison,
        pagination=meta,
        partial_errors=partial if partial.has_errors else None,
    )
