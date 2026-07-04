"""Live data tool models."""

from pydantic import BaseModel, Field

from pitstop.models.common import PartialErrors


class SessionScope(BaseModel):
    """Session context (session_name/year/country) shared by every live-data section."""

    session_name: str | None = Field(None, description="Session name")
    year: int | None = Field(None, description="Year")
    country: str | None = Field(None, description="Country name")


class TeamRadioMessage(BaseModel):
    """Team radio message data."""

    date: str = Field(..., description="Timestamp of radio message")
    driver_number: int = Field(..., description="Driver number (1-99)")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")
    recording_url: str | None = Field(None, description="URL to audio recording")


class TeamRadioResponse(SessionScope):
    """Response for team radio messages."""

    messages: list[TeamRadioMessage] = Field(..., description="List of radio messages")
    total_messages: int = Field(..., description="Total number of messages")


class PitStopData(BaseModel):
    """Pit stop data."""

    date: str = Field(..., description="Timestamp of pit stop")
    driver_number: int = Field(..., description="Driver number (1-99)")
    lap_number: int = Field(..., description="Lap number of pit stop")
    pit_duration: float = Field(..., description="Duration of pit stop in seconds")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")


class PitStopsResponse(SessionScope):
    """Response for pit stop data."""

    pit_stops: list[PitStopData] = Field(..., description="List of pit stops")
    total_pit_stops: int = Field(..., description="Total number of pit stops")
    fastest_stop: float | None = Field(None, description="Fastest pit stop duration")
    slowest_stop: float | None = Field(None, description="Slowest pit stop duration")
    average_duration: float | None = Field(None, description="Average pit stop duration")


class IntervalData(BaseModel):
    """Interval and gap data."""

    date: str = Field(..., description="Timestamp")
    driver_number: int = Field(..., description="Driver number (1-99)")
    gap_to_leader: str | float | None = Field(None, description="Gap to race leader")
    interval: str | float | None = Field(None, description="Interval to car ahead")
    session_key: int = Field(..., description="Session identifier")
    meeting_key: int = Field(..., description="Meeting identifier")


class IntervalsResponse(SessionScope):
    """Response for intervals data."""

    intervals: list[IntervalData] = Field(..., description="List of interval data points")
    total_data_points: int = Field(..., description="Total number of data points")


class StintData(BaseModel):
    """Tire stint data."""

    stint_number: int = Field(..., description="Stint number")
    driver_number: int = Field(..., description="Driver number (1-99)")
    compound: str = Field(..., description="Tire compound (SOFT, MEDIUM, HARD, etc.)")
    lap_start: int | None = Field(None, description="Starting lap number")
    lap_end: int | None = Field(None, description="Ending lap number")
    tyre_age_at_start: int | None = Field(None, description="Tyre age at start of stint")


class StintsResponse(SessionScope):
    """Response for tire stint data."""

    stints: list[StintData] = Field(..., description="List of tire stints")
    total_stints: int = Field(..., description="Total number of stints")


class RaceControlMessage(BaseModel):
    """Race control message data."""

    date: str = Field(..., description="Timestamp of message")
    category: str = Field(..., description="Category (Flag, SafetyCar, Other)")
    message: str = Field(..., description="Message text")
    driver_number: int | None = Field(None, description="Driver number (if applicable)")
    flag: str | None = Field(None, description="Flag type (if applicable)")
    lap_number: int | None = Field(None, description="Lap number")
    scope: str | None = Field(None, description="Scope (Track, Sector, etc.)")
    sector: int | None = Field(None, description="Sector number")


class RaceControlResponse(SessionScope):
    """Response for race control messages."""

    messages: list[RaceControlMessage] = Field(..., description="List of messages")
    total_messages: int = Field(..., description="Total number of messages")


class WeatherData(BaseModel):
    """Weather data."""

    date: str | None = Field(None, description="Timestamp of weather reading")
    air_temperature: float | None = Field(None, description="Air temperature in Celsius")
    track_temperature: float | None = Field(None, description="Track temperature in Celsius")
    humidity: float | None = Field(None, description="Relative humidity (%)")
    pressure: float | None = Field(None, description="Air pressure (mbar)")
    rainfall: float | None = Field(None, description="Rainfall indicator")
    wind_direction: float | None = Field(None, description="Wind direction (degrees)")
    wind_speed: float | None = Field(None, description="Wind speed (m/s)")
    session_key: int | None = Field(None, description="Session identifier")
    meeting_key: int | None = Field(None, description="Meeting identifier")


class WeatherResponse(SessionScope):
    """Response for weather data."""

    weather: list[WeatherData] = Field(..., description="List of weather readings")
    total_data_points: int = Field(..., description="Total number of data points")


class PositionData(BaseModel):
    """Position data."""

    date: str | None = Field(None, description="Timestamp of position change")
    driver_number: int | None = Field(None, description="Driver number (1-99)")
    position: int | None = Field(None, description="Position on track")
    session_key: int | None = Field(None, description="Session identifier")
    meeting_key: int | None = Field(None, description="Meeting identifier")


class PositionResponse(SessionScope):
    """Response for position data."""

    positions: list[PositionData] = Field(..., description="List of position changes")
    total_data_points: int = Field(..., description="Total number of data points")


class LapData(BaseModel):
    """Lap timing data."""

    driver_number: int | None = Field(None, description="Driver number (1-99)")
    lap_number: int | None = Field(None, description="Lap number")
    lap_duration: float | None = Field(None, description="Lap duration in seconds")
    duration_sector_1: float | None = Field(None, description="Sector 1 duration in seconds")
    duration_sector_2: float | None = Field(None, description="Sector 2 duration in seconds")
    duration_sector_3: float | None = Field(None, description="Sector 3 duration in seconds")
    i1_speed: float | None = Field(None, description="Speed trap 1 speed (km/h)")
    i2_speed: float | None = Field(None, description="Speed trap 2 speed (km/h)")
    st_speed: float | None = Field(None, description="Speed trap (straight) speed (km/h)")
    is_pit_out_lap: bool | None = Field(None, description="Whether lap is a pit-out lap")
    date_start: str | None = Field(None, description="Timestamp of lap start")
    session_key: int | None = Field(None, description="Session identifier")
    meeting_key: int | None = Field(None, description="Meeting identifier")


class LapsResponse(SessionScope):
    """Response for lap data."""

    laps: list[LapData] = Field(..., description="List of laps")
    total_laps: int = Field(..., description="Total number of laps")


class OvertakeData(BaseModel):
    """Overtake data (beta endpoint)."""

    date: str | None = Field(None, description="Timestamp of overtake")
    overtaking_driver_number: int | None = Field(None, description="Overtaking driver number")
    overtaken_driver_number: int | None = Field(None, description="Overtaken driver number")
    position: int | None = Field(None, description="Position at overtake")
    session_key: int | None = Field(None, description="Session identifier")
    meeting_key: int | None = Field(None, description="Meeting identifier")


class OvertakesResponse(SessionScope):
    """Response for overtake data."""

    overtakes: list[OvertakeData] = Field(..., description="List of overtakes")
    total_overtakes: int = Field(..., description="Total number of overtakes")


class LiveDataResponse(SessionScope):
    """Comprehensive live session data."""

    # Optional components based on requested data_types
    intervals: IntervalsResponse | None = Field(None, description="Intervals and gaps")
    pit_stops: PitStopsResponse | None = Field(None, description="Pit stop analysis")
    radio: TeamRadioResponse | None = Field(None, description="Team radio messages")
    stints: StintsResponse | None = Field(None, description="Tire stint history")
    race_control: RaceControlResponse | None = Field(None, description="Race control messages")
    weather: WeatherResponse | None = Field(None, description="Weather conditions")
    position: PositionResponse | None = Field(None, description="Position changes over time")
    laps: LapsResponse | None = Field(None, description="Per-lap sector times and speeds")
    overtakes: OvertakesResponse | None = Field(None, description="On-track overtakes (beta)")
    partial_errors: PartialErrors | None = Field(
        None, description="Partial fetch errors per data type"
    )
