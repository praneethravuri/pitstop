"""Analysis tool models."""

from pydantic import BaseModel, ConfigDict

from pitstop.models.common import PageMeta, PartialErrors


class RacePaceData(BaseModel):
    model_config = ConfigDict(strict=True)

    driver: str
    mean_lap_time_s: float | None
    median_lap_time_s: float | None
    best_lap_time_s: float | None
    total_laps: int


class TireDegradationData(BaseModel):
    model_config = ConfigDict(strict=True)

    driver: str
    compound: str | None
    stint_number: int
    lap_start: int
    lap_end: int
    degradation_rate_s_per_lap: float | None
    laps_on_compound: int


class StintSummary(BaseModel):
    model_config = ConfigDict(strict=True)

    driver: str
    stint_number: int
    compound: str | None
    lap_start: int
    lap_end: int
    laps: int
    avg_lap_time_s: float | None
    best_lap_time_s: float | None


class ConsistencyData(BaseModel):
    model_config = ConfigDict(strict=True)

    driver: str
    stddev_s: float | None
    total_laps: int
    consistency_rank: int | None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    year: int
    gp: str | int
    session: str
    analysis_type: str
    drivers_analyzed: list[str]
    pace: list[RacePaceData] | None = None
    tire_degradation: list[TireDegradationData] | None = None
    stints: list[StintSummary] | None = None
    consistency: list[ConsistencyData] | None = None
    total_records: int
    pagination: PageMeta | None = None
    partial_errors: PartialErrors | None = None
