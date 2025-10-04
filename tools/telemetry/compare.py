from clients.fastf1_client import FastF1Client
from typing import Union, Optional

# Initialize FastF1 client
fastf1_client = FastF1Client()


def compare_driver_telemetry(
    year: int,
    gp: Union[str, int],
    session: str,
    driver1: Union[str, int],
    driver2: Union[str, int],
    lap1: Optional[int] = None,
    lap2: Optional[int] = None
):
    """
    Compare telemetry data between two drivers.

    Retrieves and returns telemetry data for two drivers side-by-side, enabling
    detailed performance comparison. Useful for analyzing racing lines, braking
    points, and overall driving style differences.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver1: First driver identifier (3-letter code or number)
        driver2: Second driver identifier (3-letter code or number)
        lap1: Lap number for driver1 (uses fastest lap if None)
        lap2: Lap number for driver2 (uses fastest lap if None)

    Returns:
        tuple: (driver1_telemetry, driver2_telemetry) as pandas DataFrames
        Each DataFrame contains telemetry data with speed, throttle, brake,
        gear, RPM, DRS, and position information

    Examples:
        >>> # Compare fastest laps between Verstappen and Hamilton
        >>> ver_tel, ham_tel = compare_driver_telemetry(2024, "Monza", "Q", "VER", "HAM")

        >>> # Compare specific laps
        >>> ver_tel, ham_tel = compare_driver_telemetry(2024, "Monza", "R", "VER", "HAM", lap1=15, lap2=15)

        >>> # Compare drivers using driver numbers
        >>> tel1, tel2 = compare_driver_telemetry(2024, "Monaco", "Q", 1, 44)
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=True, weather=False, messages=False)

    # Get driver 1 lap
    driver1_laps = session_obj.laps.pick_drivers(driver1)
    if lap1 is None:
        lap1_data = driver1_laps.pick_fastest()
    else:
        lap1_data = driver1_laps[driver1_laps['LapNumber'] == lap1].iloc[0]

    # Get driver 2 lap
    driver2_laps = session_obj.laps.pick_drivers(driver2)
    if lap2 is None:
        lap2_data = driver2_laps.pick_fastest()
    else:
        lap2_data = driver2_laps[driver2_laps['LapNumber'] == lap2].iloc[0]

    return lap1_data.get_telemetry(), lap2_data.get_telemetry()
