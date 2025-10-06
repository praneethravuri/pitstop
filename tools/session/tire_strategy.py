from clients.fastf1_client import FastF1Client
from typing import Union, Optional
from models.sessions import TireStrategyResponse, TireStint
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_tire_strategy(year: int, gp: Union[str, int], session: str, driver: Optional[Union[str, int]] = None) -> TireStrategyResponse:
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
        TireStrategyResponse: Tire data per lap in JSON-serializable format

    Examples:
        >>> # Get tire strategy for all drivers in 2024 Monza race
        >>> strategy = get_tire_strategy(2024, "Monza", "R")

        >>> # Get Verstappen's tire strategy
        >>> ver_strategy = get_tire_strategy(2024, "Monza", "R", "VER")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    event = session_obj.event

    if driver:
        laps = session_obj.laps.pick_drivers(driver)
    else:
        laps = session_obj.laps

    tire_data = laps[['Driver', 'LapNumber', 'Compound', 'TyreLife', 'FreshTyre']]

    # Convert to Pydantic models
    tire_stints = []
    for idx, row in tire_data.iterrows():
        stint = TireStint(
            driver=str(row['Driver']) if pd.notna(row.get('Driver')) else "",
            lap_number=int(row['LapNumber']) if pd.notna(row.get('LapNumber')) else 0,
            compound=str(row['Compound']) if pd.notna(row.get('Compound')) else None,
            tyre_life=float(row['TyreLife']) if pd.notna(row.get('TyreLife')) else None,
            fresh_tyre=bool(row['FreshTyre']) if pd.notna(row.get('FreshTyre')) else None,
        )
        tire_stints.append(stint)

    return TireStrategyResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        driver=str(driver) if driver else None,
        tire_data=tire_stints,
        total_laps=len(tire_stints)
    )


if __name__ == "__main__":
    # Test with 2024 Monza Grand Prix Race
    print("Testing get_tire_strategy...")

    # Test 1: Get tire strategy for a specific driver
    print("\n1. Verstappen's tire strategy in 2024 Monza Race:")
    ver_strategy = get_tire_strategy(2024, "Monza", "R", driver="VER")
    print(f"   Session: {ver_strategy.session_name}")
    print(f"   Total laps: {ver_strategy.total_laps}")
    if ver_strategy.tire_data:
        print(f"\n   First lap: Compound={ver_strategy.tire_data[0].compound}, TyreLife={ver_strategy.tire_data[0].tyre_life}")

    # Test JSON serialization
    print(f"\n   JSON: {ver_strategy.model_dump_json()[:100]}...")
