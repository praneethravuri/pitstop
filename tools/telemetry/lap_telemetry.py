from clients.fastf1_client import FastF1Client
from typing import Union

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_lap_telemetry(year: int, gp: Union[str, int], session: str, driver: Union[str, int], lap_number: int):
    """
    Get detailed telemetry data for a specific lap.

    Retrieves high-frequency telemetry data including speed, throttle, brake,
    gear, RPM, and DRS usage throughout a lap. Essential for detailed performance
    analysis and driver comparison.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Driver identifier - 3-letter code (e.g., 'VER') or number (e.g., 1)
        lap_number: The specific lap number to analyze

    Returns:
        pandas.DataFrame: Telemetry data with columns:
        - Time: Time delta from session start
        - SessionTime: Absolute session time
        - DriverAhead: Driver ahead
        - DistanceToDriverAhead: Gap in meters
        - Speed: Speed in km/h
        - RPM: Engine RPM
        - nGear: Current gear (1-8)
        - Throttle: Throttle position (0-100%)
        - Brake: Brake application (boolean or 0-100%)
        - DRS: DRS status
        - X, Y, Z: Position coordinates
        - Status: Session status

    Examples:
        >>> # Get telemetry for Verstappen's lap 15 in 2024 Monza race
        >>> telemetry = get_lap_telemetry(2024, "Monza", "R", "VER", 15)

        >>> # Analyze Hamilton's fastest qualifying lap
        >>> # First find the lap number, then get telemetry
        >>> ham_telemetry = get_lap_telemetry(2024, "Monaco", "Q", 44, 8)
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=True, weather=False, messages=False)

    driver_laps = session_obj.laps.pick_drivers(driver)
    lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
    return lap.get_telemetry()
