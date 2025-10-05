from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_laps(
    year: int,
    gp: Union[str, int],
    session: str,
    driver: Optional[Union[str, int]] = None,
    lap_type: Optional[Literal["all", "fastest"]] = "all"
):
    """
    Get lap data from an F1 session with flexible filtering.

    A composable function to retrieve lap data - all laps, specific driver's laps,
    or fastest laps. Use this single tool for all lap-related queries instead of
    multiple separate tools.

    Use this tool to:
    - Get all laps from a session (default behavior)
    - Get a specific driver's laps (provide driver parameter)
    - Get the fastest lap overall or for a driver (set lap_type='fastest')
    - Analyze lap times, sectors, tire compounds, and lap progression

    Args:
        year: The season year (2018 onwards for detailed data)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1' (Free Practice 1), 'FP2', 'FP3',
                'Q' (Qualifying), 'S' (Sprint), 'R' (Race)
        driver: Optional - Driver identifier as 3-letter code (e.g., 'VER', 'HAM')
                or number (e.g., 1, 44). If None, returns data for all drivers.
        lap_type: Optional - 'all' returns all laps (default), 'fastest' returns
                 only the fastest lap(s)

    Returns:
        pandas.DataFrame or pandas.Series: Lap data with columns including:
        - LapTime: Total lap time
        - LapNumber: Lap number
        - Driver: Driver abbreviation
        - Sector1Time, Sector2Time, Sector3Time: Sector times
        - Compound: Tire compound used (SOFT, MEDIUM, HARD, etc.)
        - TyreLife: Age of tires in laps
        - TrackStatus: Track status during lap
        - IsPersonalBest: Whether it's driver's fastest lap
        - Speed data (SpeedI1, SpeedI2, SpeedFL, SpeedST)

    Examples:
        >>> # Get all laps from 2024 Monza race (all drivers)
        >>> all_laps = get_laps(2024, "Monza", "R")

        >>> # Get all laps for Verstappen in 2024 Monza race
        >>> ver_laps = get_laps(2024, "Monza", "R", driver="VER")

        >>> # Get fastest lap overall from 2024 Monaco qualifying
        >>> fastest = get_laps(2024, "Monaco", "Q", lap_type="fastest")

        >>> # Get Verstappen's fastest lap from the race
        >>> ver_fastest = get_laps(2024, "Monza", "R", driver="VER", lap_type="fastest")

        >>> # Get Hamilton's qualifying laps
        >>> ham_quali = get_laps(2024, "Monaco", "Q", driver=44)

        >>> # Get all FP1 laps
        >>> fp1_laps = get_laps(2024, "Silverstone", "FP1")
    """
    # Load session with lap data
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    # Get laps based on driver filter
    if driver:
        laps = session_obj.laps.pick_drivers(driver)
    else:
        laps = session_obj.laps

    # Return based on lap_type
    if lap_type == "fastest":
        return laps.pick_fastest()
    else:
        return laps
