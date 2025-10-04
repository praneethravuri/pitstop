from clients.fastf1_client import FastF1Client
from typing import Union, Optional

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_laps(year: int, gp: Union[str, int], session: str):
    """
    Get all laps from a specific F1 session.

    Retrieves complete lap data for all drivers in a session, including lap times,
    sectors, tire compounds, and lap-by-lap information.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        pandas.DataFrame: All laps with columns including:
        - LapTime: Total lap time
        - LapNumber: Lap number
        - Driver: Driver abbreviation
        - Sector1Time, Sector2Time, Sector3Time: Sector times
        - Compound: Tire compound used
        - TyreLife: Age of tires in laps
        - TrackStatus: Track status during lap
        - IsPersonalBest: Whether it's driver's fastest lap

    Examples:
        >>> # Get all laps from 2024 Monza race
        >>> laps = get_session_laps(2024, "Monza", "R")

        >>> # Get qualifying laps
        >>> quali_laps = get_session_laps(2024, "Monaco", "Q")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)
    return session_obj.laps


def get_driver_laps(year: int, gp: Union[str, int], session: str, driver: Union[str, int]):
    """
    Get all laps for a specific driver in a session.

    Retrieves lap data for a single driver, useful for analyzing individual
    driver performance and lap-by-lap progression.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Driver identifier - 3-letter code (e.g., 'VER', 'HAM') or number (e.g., 1, 44)

    Returns:
        pandas.DataFrame: Driver's laps with timing data, sectors, compounds, etc.

    Examples:
        >>> # Get all laps for Verstappen in 2024 Monza race
        >>> ver_laps = get_driver_laps(2024, "Monza", "R", "VER")

        >>> # Get Hamilton's qualifying laps
        >>> ham_laps = get_driver_laps(2024, "Monaco", "Q", 44)
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)
    return session_obj.laps.pick_drivers(driver)


def get_fastest_lap(year: int, gp: Union[str, int], session: str, driver: Optional[Union[str, int]] = None):
    """
    Get the fastest lap from a session, optionally for a specific driver.

    Retrieves the fastest lap time set during a session, either overall or
    for a specific driver.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Optional driver identifier (3-letter code or number).
               If None, returns overall fastest lap

    Returns:
        pandas.Series: Fastest lap data including:
        - LapTime: The lap time
        - Driver: Driver who set the lap
        - LapNumber: When it was set
        - Compound: Tire compound used
        - Sector times and speeds

    Examples:
        >>> # Get overall fastest lap from 2024 Monza qualifying
        >>> fastest = get_fastest_lap(2024, "Monza", "Q")

        >>> # Get Verstappen's fastest lap
        >>> ver_fastest = get_fastest_lap(2024, "Monza", "R", "VER")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    if driver:
        driver_laps = session_obj.laps.pick_drivers(driver)
        return driver_laps.pick_fastest()
    else:
        return session_obj.laps.pick_fastest()
