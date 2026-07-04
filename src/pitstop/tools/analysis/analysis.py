"""Race analysis tool — pace, tire degradation, stints, consistency."""

import logging
from typing import Literal

import numpy as np

from pitstop.clients import get_fastf1_client
from pitstop.models.common import PartialErrors
from pitstop.tools.analysis.models import (
    AnalysisResponse,
    ConsistencyData,
    RacePaceData,
    StintSummary,
    TireDegradationData,
)
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.analysis")

fastf1_client = get_fastf1_client()


def get_race_analysis(
    year: int,
    gp: str | int,
    session: str,
    drivers: list[str],
    analysis_type: Literal["pace", "tire_degradation", "stints", "consistency"] = "pace",
    page: int = 1,
    page_size: int = 30,
) -> AnalysisResponse:
    """
    PRIMARY tool for race performance analytics (2018–present via FastF1).
    Computes pace, tire degradation, stint summaries, and consistency from session lap data.
    Coverage: 2018–present (FastF1 timing data).
    analysis_type options: pace, tire_degradation, stints, consistency
    """
    try:
        session_obj = fastf1_client.get_session(year, gp, session)
        session_obj.load()
    except Exception as exc:
        raise to_tool_error("get_race_analysis", "fastf1", exc)

    partial = PartialErrors()
    pace_list: list[RacePaceData] = []
    degradation_list: list[TireDegradationData] = []
    stint_list: list[StintSummary] = []
    consistency_raw: list[tuple[str, float | None, int]] = []

    for driver in drivers:
        try:
            driver_laps = session_obj.laps.pick_driver(driver)
            valid_laps = driver_laps[driver_laps["LapTime"].notna()]

            if analysis_type == "pace":
                times_s = valid_laps["LapTime"].apply(lambda x: x.total_seconds())
                n = len(times_s)
                pace_list.append(
                    RacePaceData(
                        driver=str(driver),
                        mean_lap_time_s=float(times_s.mean()) if n > 0 else None,
                        median_lap_time_s=float(times_s.median()) if n > 0 else None,
                        best_lap_time_s=float(times_s.min()) if n > 0 else None,
                        total_laps=int(len(valid_laps)),
                    )
                )

            elif analysis_type == "tire_degradation":
                for (compound, stint_num), group in valid_laps.groupby(["Compound", "Stint"]):
                    n = len(group)
                    times_s = group["LapTime"].apply(lambda x: x.total_seconds()).values
                    lap_nums = group["LapNumber"].values
                    deg_rate = None
                    if n >= 3:
                        slope, _ = np.polyfit(range(n), times_s, 1)
                        deg_rate = float(slope)
                    degradation_list.append(
                        TireDegradationData(
                            driver=str(driver),
                            compound=str(compound) if compound == compound else None,
                            stint_number=int(stint_num),
                            lap_start=int(lap_nums.min()),
                            lap_end=int(lap_nums.max()),
                            degradation_rate_s_per_lap=deg_rate,
                            laps_on_compound=int(n),
                        )
                    )

            elif analysis_type == "stints":
                for stint_num, group in valid_laps.groupby("Stint"):
                    compound = group["Compound"].iloc[0] if "Compound" in group.columns else None
                    times_s = group["LapTime"].apply(lambda x: x.total_seconds())
                    lap_nums = group["LapNumber"].values
                    n = len(group)
                    stint_list.append(
                        StintSummary(
                            driver=str(driver),
                            stint_number=int(stint_num),
                            compound=str(compound) if compound == compound else None,
                            lap_start=int(lap_nums.min()),
                            lap_end=int(lap_nums.max()),
                            laps=int(n),
                            avg_lap_time_s=float(times_s.mean()) if n > 0 else None,
                            best_lap_time_s=float(times_s.min()) if n > 0 else None,
                        )
                    )

            elif analysis_type == "consistency":
                times_s = valid_laps["LapTime"].apply(lambda x: x.total_seconds())
                n = len(times_s)
                stddev = float(times_s.std()) if n >= 2 else None
                consistency_raw.append((str(driver), stddev, int(n)))

        except Exception as exc:
            logger.warning("Driver %s analysis failed: %s", driver, exc)
            partial.add(str(driver), "fastf1", exc)

    consistency_list: list[ConsistencyData] = []
    if analysis_type == "consistency":
        ranked = sorted(consistency_raw, key=lambda x: (x[1] is None, x[1] or 0.0))
        for rank, (drv, stddev, total_laps) in enumerate(ranked, 1):
            consistency_list.append(
                ConsistencyData(
                    driver=drv,
                    stddev_s=stddev,
                    total_laps=total_laps,
                    consistency_rank=rank,
                )
            )

    result_map = {
        "pace": pace_list,
        "tire_degradation": degradation_list,
        "stints": stint_list,
        "consistency": consistency_list,
    }
    records = result_map.get(analysis_type, [])
    paged, meta = paginate(records, page, page_size)

    return AnalysisResponse(
        year=year,
        gp=gp,
        session=session,
        analysis_type=analysis_type,
        drivers_analyzed=list(drivers),
        pace=paged if analysis_type == "pace" else None,
        tire_degradation=paged if analysis_type == "tire_degradation" else None,
        stints=paged if analysis_type == "stints" else None,
        consistency=paged if analysis_type == "consistency" else None,
        total_records=len(records),
        pagination=meta if records else None,
        partial_errors=partial if partial.has_errors else None,
    )
