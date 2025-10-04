from pydantic import BaseModel, Field


class DriverResult(BaseModel):
    """Individual driver result in a race or session."""

    position: int | None = Field(None, description="Finishing position (None if DNF/DNS)")
    driver_name: str = Field(..., description="Driver full name")
    driver_code: str = Field(..., description="3-letter driver code")
    team: str = Field(..., description="Team/constructor name")
    time: str | None = Field(None, description="Finishing time or gap to leader")
    status: str = Field(..., description="Result status (Finished, DNF, +1 Lap, etc.)")
    points: float | None = Field(None, description="Points awarded (if applicable)")


class RaceResultResponse(BaseModel):
    """Complete race results for a Grand Prix."""

    year: int = Field(..., description="Season year")
    race_name: str = Field(..., description="Race name")
    round_number: int = Field(..., description="Round number")
    date: str = Field(..., description="Race date")
    circuit: str = Field(..., description="Circuit name")
    results: list[DriverResult] = Field(..., description="List of driver results")


class QualifyingTime(BaseModel):
    """Qualifying lap time for a driver."""

    driver_name: str = Field(..., description="Driver full name")
    driver_code: str = Field(..., description="3-letter driver code")
    team: str = Field(..., description="Team/constructor name")
    position: int = Field(..., description="Qualifying position")
    q1_time: str | None = Field(None, description="Q1 lap time")
    q2_time: str | None = Field(None, description="Q2 lap time (if reached)")
    q3_time: str | None = Field(None, description="Q3 lap time (if reached)")


class QualifyingResultResponse(BaseModel):
    """Complete qualifying results for a Grand Prix."""

    year: int = Field(..., description="Season year")
    race_name: str = Field(..., description="Race name")
    round_number: int = Field(..., description="Round number")
    date: str = Field(..., description="Qualifying date")
    circuit: str = Field(..., description="Circuit name")
    results: list[QualifyingTime] = Field(..., description="List of qualifying results")


class FastestLap(BaseModel):
    """Fastest lap information for a driver."""

    position: int = Field(..., description="Position by lap time")
    driver_name: str = Field(..., description="Driver full name")
    driver_code: str = Field(..., description="3-letter driver code")
    team: str = Field(..., description="Team/constructor name")
    lap_time: str = Field(..., description="Lap time")
    lap_number: int | None = Field(None, description="Lap number when set (if available)")


class FastestLapsResponse(BaseModel):
    """Fastest laps from a session."""

    year: int = Field(..., description="Season year")
    race_name: str = Field(..., description="Race name")
    session: str = Field(..., description="Session name (Race, Qualifying, Practice 1, etc.)")
    circuit: str = Field(..., description="Circuit name")
    fastest_laps: list[FastestLap] = Field(..., description="List of fastest laps sorted by time")


class PitStop(BaseModel):
    """Pit stop information."""

    lap: int = Field(..., description="Lap number of pit stop")
    stop_number: int = Field(..., description="Stop number (1st, 2nd, 3rd, etc.)")
    duration: str = Field(..., description="Pit stop duration")


class DriverPerformance(BaseModel):
    """Detailed performance data for a driver in a race."""

    driver_name: str = Field(..., description="Driver full name")
    driver_code: str = Field(..., description="3-letter driver code")
    team: str = Field(..., description="Team/constructor name")
    position: int | None = Field(None, description="Finishing position")
    grid_position: int | None = Field(None, description="Starting grid position")
    status: str = Field(..., description="Result status")
    points: float | None = Field(None, description="Points earned")
    fastest_lap: str | None = Field(None, description="Driver's fastest lap time")
    pit_stops: list[PitStop] | None = Field(None, description="List of pit stops made")


class DriverPerformanceResponse(BaseModel):
    """Driver performance in a specific race."""

    year: int = Field(..., description="Season year")
    race_name: str = Field(..., description="Race name")
    driver: str = Field(..., description="Driver searched for")
    performance: DriverPerformance = Field(..., description="Driver performance data")


class WeatherData(BaseModel):
    """Weather conditions during a session."""

    air_temp: float | None = Field(None, description="Air temperature in Celsius")
    track_temp: float | None = Field(None, description="Track temperature in Celsius")
    humidity: float | None = Field(None, description="Humidity percentage")
    pressure: float | None = Field(None, description="Air pressure in mbar")
    wind_speed: float | None = Field(None, description="Wind speed in km/h")
    wind_direction: int | None = Field(None, description="Wind direction in degrees")
    rainfall: bool | None = Field(None, description="Whether it was raining")


class SessionWeatherResponse(BaseModel):
    """Weather data for a session."""

    year: int = Field(..., description="Season year")
    race_name: str = Field(..., description="Race name")
    session: str = Field(..., description="Session name")
    weather: WeatherData = Field(..., description="Weather conditions")
