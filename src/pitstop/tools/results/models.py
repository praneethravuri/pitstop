"""Results tool models."""

from pydantic import BaseModel, ConfigDict

from pitstop.models.common import PageMeta


class RaceResult(BaseModel):
    model_config = ConfigDict(strict=True)

    position: int | None
    driver_id: str
    driver_name: str  # "{givenName} {familyName}"
    constructor: str
    laps: int | None
    time: str | None
    status: str | None
    points: float | None
    grid: int | None
    fastest_lap_rank: int | None = None
    fastest_lap_time: str | None = None


class QualifyingResult(BaseModel):
    model_config = ConfigDict(strict=True)

    position: int | None
    driver_id: str
    driver_name: str
    constructor: str
    q1: str | None
    q2: str | None
    q3: str | None


class SprintResult(BaseModel):
    model_config = ConfigDict(strict=True)

    position: int | None
    driver_id: str
    driver_name: str
    constructor: str
    laps: int | None
    time: str | None
    status: str | None
    points: float | None


class LapTiming(BaseModel):
    model_config = ConfigDict(strict=True)

    lap_number: int
    driver_id: str
    position: int | None
    time: str | None


class PitStopRecord(BaseModel):
    model_config = ConfigDict(strict=True)

    lap: int
    driver_id: str
    stop: int
    time_of_day: str | None
    duration: str | None


class FinishStatus(BaseModel):
    model_config = ConfigDict(strict=True)

    status_id: str
    count: int
    status: str


class ResultsResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    year: int
    round: int | str
    race_name: str | None
    result_type: str
    race_results: list[RaceResult] | None = None
    qualifying_results: list[QualifyingResult] | None = None
    sprint_results: list[SprintResult] | None = None
    laps: list[LapTiming] | None = None
    pit_stops: list[PitStopRecord] | None = None
    statuses: list[FinishStatus] | None = None
    total_records: int
    pagination: PageMeta | None = None
