import logging

import pandas as pd
from pydantic import BaseModel

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.models.common import PageMeta, PartialErrors
from pitstop.tools.telemetry.models import LapTelemetryResponse, TelemetryPoint
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.telemetry")

# ponytail: module-level singleton; swap for shared factory when clients/__init__ ships it
fastf1_client = FastF1Client()


class TelemetryDataResponse(BaseModel):
    drivers_telemetry: list[LapTelemetryResponse]
    pagination: PageMeta | None = None
    partial_errors: PartialErrors | None = None


def get_telemetry_data(
    year: int,
    gp: str | int,
    session: str,
    drivers: list[str | int],
    lap_numbers: list[int] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TelemetryDataResponse:
    """
    Get telemetry data for one or more drivers.

    Args:
        year: Season year
        gp: Grand Prix name or round
        session: Session identifier
        drivers: List of driver identifiers (e.g. ["VER", "HAM"])
        lap_numbers: Optional list of lap numbers corresponding to drivers.
                     If None or matching index is None, fetches fastest lap.
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
                continue

            if lap_num is None:
                selected_lap = driver_laps.pick_fastest()
            else:
                laps = driver_laps[driver_laps["LapNumber"] == lap_num]
                selected_lap = laps.iloc[0] if not laps.empty else None

            if selected_lap is None:
                continue

            tel_data = selected_lap.get_telemetry()

            points = []
            for _, row in tel_data.iterrows():
                points.append(
                    TelemetryPoint(
                        session_time=str(row["SessionTime"]),
                        rpm=int(row["RPM"]) if pd.notna(row.get("RPM")) else 0,
                        speed=float(row["Speed"]) if pd.notna(row.get("Speed")) else 0.0,
                        throttle=float(row["Throttle"]) if pd.notna(row.get("Throttle")) else 0.0,
                        brake=bool(row["Brake"]) if pd.notna(row.get("Brake")) else False,
                        n_gear=int(row["nGear"]) if pd.notna(row.get("nGear")) else 0,
                        drs=int(row["DRS"]) if pd.notna(row.get("DRS")) else 0,
                        distance=float(row["Distance"]) if pd.notna(row.get("Distance")) else 0.0,
                        x=float(row["X"]) if pd.notna(row.get("X")) else 0.0,
                        y=float(row["Y"]) if pd.notna(row.get("Y")) else 0.0,
                        z=float(row["Z"]) if pd.notna(row.get("Z")) else 0.0,
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

    paged, meta = paginate(telemetry_list, page, page_size)
    return TelemetryDataResponse(
        drivers_telemetry=paged,
        pagination=meta,
        partial_errors=partial if partial.has_errors else None,
    )
