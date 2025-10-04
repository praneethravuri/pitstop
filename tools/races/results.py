from clients.fastf1_client import FastF1Client
from models import (
    RaceResultResponse,
    QualifyingResultResponse,
    FastestLapsResponse,
    DriverPerformanceResponse,
    SessionWeatherResponse,
)

# Initialize FastF1 client with caching enabled
f1_client = FastF1Client(cache_dir="cache", enable_cache=True)


def get_race_results(year: int, race_name: str) -> RaceResultResponse:
    """
    Get complete race results for a specific Formula 1 Grand Prix.

    Returns final race classification with positions, times, status (Finished/DNF/DSQ),
    and points awarded. Includes all drivers who started the race.

    Args:
        year: The season year (2018+ for detailed data, 1950+ for basic results via Ergast)
        race_name: The race name (e.g., 'Bahrain', 'Monaco', 'Silverstone')

    Returns:
        RaceResultResponse: Complete race results including positions, driver names,
        teams, finishing times, status, and points for all drivers.
    """
    return f1_client.get_race_results(year, race_name)


def get_qualifying_results(year: int, race_name: str) -> QualifyingResultResponse:
    """
    Get qualifying results for a specific Grand Prix.

    Returns complete qualifying classification with Q1, Q2, and Q3 lap times.
    Shows which drivers advanced through each qualifying session.

    Args:
        year: The season year (2018+ for detailed data)
        race_name: The race name (e.g., 'Bahrain', 'Monaco')

    Returns:
        QualifyingResultResponse: Qualifying results with Q1, Q2, Q3 times for each driver,
        sorted by final qualifying position. Q2 and Q3 times only shown if driver advanced.
    """
    return f1_client.get_qualifying_results(year, race_name)


def get_sprint_results(year: int, race_name: str) -> RaceResultResponse:
    """
    Get sprint race results for a specific Grand Prix (if sprint format was used).

    Returns sprint race classification. Sprint races are shorter races held on Saturday
    that determine part of the starting grid and award points.

    Args:
        year: The season year (Sprint races introduced in 2021)
        race_name: The race name that had a sprint race

    Returns:
        RaceResultResponse: Sprint race results with positions, times, and points.

    Raises:
        RuntimeError: If the specified race did not have a sprint race
    """
    return f1_client.get_sprint_results(year, race_name)


def get_fastest_laps(year: int, race_name: str, session: str = "R") -> FastestLapsResponse:
    """
    Get fastest lap times from any session.

    Returns the fastest lap for each driver in a session, sorted by lap time.
    Useful for analyzing session pace and comparing driver/team performance.

    Args:
        year: The season year (2018+ for detailed timing data)
        race_name: The race name
        session: Session type - "FP1", "FP2", "FP3", "Q", "S", "R" (default: "R" for Race)
                 FP = Free Practice, Q = Qualifying, S = Sprint, R = Race

    Returns:
        FastestLapsResponse: List of fastest laps per driver, sorted by lap time,
        including position, driver name, team, and lap time.
    """
    return f1_client.get_session_fastest_laps(year, race_name, session)


def get_session_results(year: int, race_name: str, session: str) -> FastestLapsResponse:
    """
    Get session results for any practice, qualifying, sprint, or race session.

    Returns fastest laps from the session, which serves as a proxy for session results
    showing driver/team pace. For official race classification, use get_race_results().

    Args:
        year: The season year (2018+ for detailed timing data)
        race_name: The race name
        session: Session type - "FP1", "FP2", "FP3", "Q", "S", "R"

    Returns:
        FastestLapsResponse: Session results sorted by fastest lap time
    """
    return f1_client.get_session_fastest_laps(year, race_name, session)


def get_driver_race_performance(year: int, race_name: str, driver: str) -> DriverPerformanceResponse:
    """
    Get detailed performance data for a specific driver in a race.

    Returns comprehensive race performance including grid position, finishing position,
    fastest lap, pit stops, and status. Useful for analyzing individual driver races.

    Args:
        year: The season year (2018+ for detailed data including pit stops)
        race_name: The race name
        driver: Driver code (e.g., 'VER', 'HAM', 'LEC') or driver name (e.g., 'Verstappen')

    Returns:
        DriverPerformanceResponse: Detailed driver performance including starting position,
        finishing position, status, points, fastest lap, and pit stop information.

    Raises:
        ValueError: If the specified driver did not participate in the race
    """
    return f1_client.get_driver_race_performance(year, race_name, driver)


def get_session_weather(year: int, race_name: str, session: str = "R") -> SessionWeatherResponse:
    """
    Get weather conditions during a session.

    Returns average weather data for the session including air/track temperature,
    humidity, pressure, wind speed/direction, and rainfall status. Weather data
    available from 2018 onwards.

    Args:
        year: The season year (2018+ for weather data)
        race_name: The race name
        session: Session type - "FP1", "FP2", "FP3", "Q", "S", "R" (default: "R" for Race)

    Returns:
        SessionWeatherResponse: Weather conditions including temperatures, humidity,
        pressure, wind data, and rainfall information.

    Raises:
        RuntimeError: If weather data is not available for the session
    """
    return f1_client.get_session_weather(year, race_name, session)
