from pydantic import BaseModel, Field


class RacePaceData(BaseModel):
    """Race pace analysis data."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    average_lap_time: str | None = Field(None, description="Average lap time (excluding pit laps)")
    median_lap_time: str | None = Field(None, description="Median lap time")
    fastest_lap_time: str | None = Field(None, description="Fastest lap time")
    total_laps: int = Field(..., description="Total number of laps")
    clean_laps: int = Field(..., description="Number of clean laps (no pit stops, accurate timing)")


class TireDegradationData(BaseModel):
    """Tire degradation analysis data."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    stint: int = Field(..., description="Stint number")
    compound: str | None = Field(None, description="Tire compound")
    first_lap_time: str | None = Field(None, description="First lap time on this stint")
    last_lap_time: str | None = Field(None, description="Last lap time on this stint")
    average_lap_time: str | None = Field(None, description="Average lap time for stint")
    degradation: str | None = Field(None, description="Estimated degradation (last - first lap)")
    stint_length: int = Field(..., description="Number of laps in stint")


class StintSummary(BaseModel):
    """Summary of a tire stint."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    stint: int = Field(..., description="Stint number")
    compound: str | None = Field(None, description="Tire compound")
    stint_length: int = Field(..., description="Number of laps in stint")
    average_lap_time: str | None = Field(None, description="Average lap time")
    fastest_lap_time: str | None = Field(None, description="Fastest lap in stint")


class ConsistencyData(BaseModel):
    """Driver consistency analysis."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    average_lap_time: str | None = Field(None, description="Average lap time")
    std_deviation: float | None = Field(
        None, description="Standard deviation of lap times (seconds)"
    )
    coefficient_of_variation: float | None = Field(
        None, description="Consistency score (lower is better)"
    )
    total_laps: int = Field(..., description="Total laps analyzed")


class AnalysisResponse(BaseModel):
    """Response containing advanced race analysis."""

    session_name: str = Field(..., description="Session name")
    event_name: str = Field(..., description="Event name")
    year: int = Field(..., description="Season year")
    analysis_type: str = Field(
        ..., description="Type: 'race_pace', 'tire_degradation', 'stint_summary', 'consistency'"
    )

    # Optional data based on type
    race_pace: list[RacePaceData] | None = Field(None, description="Race pace data")
    tire_degradation: list[TireDegradationData] | None = Field(
        None, description="Tire degradation data"
    )
    stint_summaries: list[StintSummary] | None = Field(None, description="Stint summary data")
    consistency: list[ConsistencyData] | None = Field(None, description="Consistency data")

    # Metadata
    total_records: int = Field(..., description="Total number of records")
    driver_filter: str | None = Field(None, description="Driver filter (if any)")
