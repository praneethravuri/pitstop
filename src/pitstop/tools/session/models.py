"""Session tool models."""

from datetime import datetime

from pydantic import BaseModel, Field


class SessionInfo(BaseModel):
    """Basic information about a session."""

    name: str = Field(description="Session name (e.g., 'Free Practice 1', 'Qualifying', 'Race')")
    session_type: str = Field(description="Session type identifier (FP1, FP2, FP3, Q, S, R)")
    event_name: str = Field(description="Grand Prix name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")
    circuit_name: str = Field(description="Official circuit name")
    year: int = Field(description="Season year")
    round: int = Field(description="Round number in the season")
    session_date: datetime | None = Field(None, description="Session start date and time")


class DriverSessionResult(BaseModel):
    """Individual driver result in a session."""

    position: int | None = Field(None, description="Final position")
    driver_number: str = Field(description="Driver number")
    driver_name: str = Field(description="Full driver name")
    abbreviation: str = Field(description="3-letter driver abbreviation")
    team: str = Field(description="Team name")
    time: str | None = Field(None, description="Session time (for race/qualifying)")
    gap_to_leader: str | None = Field(None, description="Gap to session leader")
    laps_completed: int | None = Field(None, description="Number of laps completed")
    points: float | None = Field(None, description="Points earned (for race)")
    status: str | None = Field(None, description="Finishing status")


class SessionWeather(BaseModel):
    """Weather information for the session."""

    air_temp: float | None = Field(None, description="Air temperature (°C)")
    track_temp: float | None = Field(None, description="Track temperature (°C)")
    humidity: float | None = Field(None, description="Humidity percentage")
    pressure: float | None = Field(None, description="Atmospheric pressure")
    wind_speed: float | None = Field(None, description="Wind speed (m/s)")
    rainfall: bool | None = Field(None, description="Whether it rained during session")


class LapInfo(BaseModel):
    """Information about the fastest lap."""

    driver: str = Field(description="Driver who set the lap")
    lap_time: str = Field(description="Lap time")
    lap_number: int = Field(description="Lap number")
    compound: str | None = Field(None, description="Tire compound used")


class SessionDetailsResponse(BaseModel):
    """Complete session details response."""

    session_info: SessionInfo = Field(description="Basic session information")
    results: list[DriverSessionResult] = Field(description="Driver results/classification")
    weather: SessionWeather | None = Field(None, description="Weather conditions")
    fastest_lap: LapInfo | None = Field(None, description="Fastest lap of the session")
    total_laps: int | None = Field(None, description="Total laps in session")
    session_duration: str | None = Field(None, description="Session duration")


class SessionResult(BaseModel):
    """Individual driver result in a session."""

    position: float | None = Field(None, description="Final position/classification")
    driver_number: str = Field(description="Driver's racing number")
    broadcast_name: str = Field(description="Driver name for broadcast")
    abbreviation: str = Field(description="3-letter driver code")
    driver_id: str | None = Field(None, description="Unique driver identifier")
    team_name: str = Field(description="Constructor/team name")
    team_color: str | None = Field(None, description="Team color hex code")
    first_name: str | None = Field(None, description="Driver first name")
    last_name: str | None = Field(None, description="Driver last name")
    full_name: str | None = Field(None, description="Driver full name")
    time: str | None = Field(None, description="Session time or gap")
    status: str | None = Field(None, description="Finishing status")
    points: float | None = Field(None, description="Points earned (for race)")
    grid_position: float | None = Field(None, description="Starting grid position")
    position_gained: float | None = Field(None, description="Positions gained/lost")


class SessionResultsResponse(BaseModel):
    """Session results/classification response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    results: list[SessionResult] = Field(description="List of driver results")
    total_drivers: int = Field(description="Total number of drivers")


class SessionDriversResponse(BaseModel):
    """Session drivers response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    year: int = Field(description="Season year")
    drivers: list[str] = Field(description="List of driver abbreviations")
    total_drivers: int = Field(description="Total number of drivers")


class LapData(BaseModel):
    """Individual lap data."""

    time: str | None = Field(None, description="Time when lap started")
    driver: str = Field(description="Driver abbreviation")
    driver_number: str = Field(description="Driver number")
    lap_time: str | None = Field(None, description="Total lap time")
    lap_number: int = Field(description="Lap number")
    stint: int | None = Field(None, description="Stint number")
    pit_out_time: str | None = Field(None, description="Pit out time")
    pit_in_time: str | None = Field(None, description="Pit in time")
    sector_1_time: str | None = Field(None, description="Sector 1 time")
    sector_2_time: str | None = Field(None, description="Sector 2 time")
    sector_3_time: str | None = Field(None, description="Sector 3 time")
    sector_1_session_time: str | None = Field(None, description="Sector 1 session time")
    sector_2_session_time: str | None = Field(None, description="Sector 2 session time")
    sector_3_session_time: str | None = Field(None, description="Sector 3 session time")
    speed_i1: float | None = Field(None, description="Speed at intermediate 1 (km/h)")
    speed_i2: float | None = Field(None, description="Speed at intermediate 2 (km/h)")
    speed_fl: float | None = Field(None, description="Speed at finish line (km/h)")
    speed_st: float | None = Field(None, description="Speed at speed trap (km/h)")
    is_personal_best: bool | None = Field(None, description="Is driver's personal best")
    compound: str | None = Field(None, description="Tire compound (SOFT, MEDIUM, HARD, etc.)")
    tyre_life: float | None = Field(None, description="Tire age in laps")
    fresh_tyre: bool | None = Field(None, description="Is fresh tire")
    team: str | None = Field(None, description="Team name")
    lap_start_time: str | None = Field(None, description="Lap start time")
    lap_start_date: str | None = Field(None, description="Lap start date")
    track_status: str | None = Field(None, description="Track status during lap")
    position: float | None = Field(None, description="Position during lap")
    deleted: bool | None = Field(None, description="Was lap time deleted")
    deleted_reason: str | None = Field(None, description="Reason for deletion")
    fast_f1_generated: bool | None = Field(None, description="Was generated by FastF1")
    is_accurate: bool | None = Field(None, description="Is lap time accurate")


class LapsResponse(BaseModel):
    """Laps data response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver: str | None = Field(None, description="Driver filter (if applied)")
    lap_type: str = Field(description="Type of laps returned (all/fastest)")
    laps: list[LapData] = Field(description="List of lap data")
    total_laps: int = Field(description="Total number of laps")


class FastestLapResponse(BaseModel):
    """Fastest lap response (single lap)."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver: str = Field(description="Driver abbreviation")
    lap_data: LapData = Field(description="Fastest lap data")


class TireStint(BaseModel):
    """Tire data for a single lap."""

    driver: str = Field(description="Driver abbreviation")
    lap_number: int = Field(description="Lap number")
    compound: str | None = Field(
        None, description="Tire compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)"
    )
    tyre_life: float | None = Field(None, description="Age of tire in laps")
    fresh_tyre: bool | None = Field(None, description="Whether it's a new tire")


class TireStrategyResponse(BaseModel):
    """Tire strategy response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver: str | None = Field(None, description="Driver filter (if applied)")
    tire_data: list[TireStint] = Field(description="Tire data per lap")
    total_laps: int = Field(description="Total number of laps")


class WeatherDataPoint(BaseModel):
    """Single weather data point."""

    time: str | None = Field(None, description="Timestamp")
    air_temp: float | None = Field(None, description="Air temperature (°C)")
    track_temp: float | None = Field(None, description="Track surface temperature (°C)")
    humidity: float | None = Field(None, description="Relative humidity (%)")
    pressure: float | None = Field(None, description="Atmospheric pressure (mbar)")
    wind_speed: float | None = Field(None, description="Wind speed (m/s)")
    wind_direction: float | None = Field(None, description="Wind direction (degrees)")
    rainfall: bool | None = Field(None, description="Whether it's raining")


class SessionWeatherDataResponse(BaseModel):
    """Session weather data response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    weather_data: list[WeatherDataPoint] = Field(
        description="Weather data points throughout session"
    )
    total_points: int = Field(description="Total number of weather data points")
