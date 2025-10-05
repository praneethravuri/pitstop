from clients.fastf1_client import FastF1Client
from typing import Union, Optional

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_tire_strategy(year: int, gp: Union[str, int], session: str, driver: Optional[Union[str, int]] = None):
    """
    Get tire strategy and compound usage for a session.

    Analyzes tire compounds used throughout a session, including compound types,
    tire life, and stint information. Essential for understanding race strategy
    and tire management.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Optional driver identifier (3-letter code or number).
               If None, returns data for all drivers

    Returns:
        pandas.DataFrame: Tire data per lap with columns:
        - Driver: Driver abbreviation
        - LapNumber: Lap number
        - Compound: Tire compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)
        - TyreLife: Age of tire in laps
        - FreshTyre: Whether it's a new tire

    Examples:
        >>> # Get tire strategy for all drivers in 2024 Monza race
        >>> strategy = get_tire_strategy(2024, "Monza", "R")

        >>> # Get Verstappen's tire strategy
        >>> ver_strategy = get_tire_strategy(2024, "Monza", "R", "VER")

        >>> # Analyze tire usage in qualifying
        >>> quali_tires = get_tire_strategy(2024, "Monaco", "Q")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    if driver:
        laps = session_obj.laps.pick_drivers(driver)
    else:
        laps = session_obj.laps

    return laps[['Driver', 'LapNumber', 'Compound', 'TyreLife', 'FreshTyre']]
