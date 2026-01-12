from typing import List, Optional, Union
from pydantic import BaseModel
from pitstop.clients.fastf1_client import FastF1Client
from pitstop.models.telemetry.lap_telemetry import LapTelemetryResponse, TelemetryPoint
import pandas as pd

fastf1_client = FastF1Client()

class TelemetryDataResponse(BaseModel):
    drivers_telemetry: List[LapTelemetryResponse]

def get_telemetry_data(
    year: int,
    gp: Union[str, int],
    session: str,
    drivers: List[Union[str, int]],
    lap_numbers: Optional[List[int]] = None
) -> TelemetryDataResponse:
    """
    Get telemetry data for one or more drivers.
    
    Args:
        year: Season year
        gp: Grand Prix name or round
        session: Session identifier
        drivers: List of driver identifiers (e.g. ["VER", "HAM"])
        lap_numbers: Optional list of lap numbers corresponding to drivers. 
                     If None or matching index is None, fetches fastest lap.
    """
    # Load session
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load()
    
    telemetry_list = []
    
    for i, driver in enumerate(drivers):
        lap_num = None
        if lap_numbers and i < len(lap_numbers):
            lap_num = lap_numbers[i]
            
        selected_lap = None
        
        # Determine which lap data to get
        driver_laps = session_obj.laps.pick_driver(driver)
        if len(driver_laps) == 0:
            continue
            
        if lap_num is None:
            # Pick fastest lap
            selected_lap = driver_laps.pick_fastest()
        else:
            # Pick specific lap
            laps = driver_laps[driver_laps['LapNumber'] == lap_num]
            if not laps.empty:
                selected_lap = laps.iloc[0]
                
        if selected_lap is not None:
            try:
                # Get telemetry for the lap
                tel_data = selected_lap.get_telemetry()
                
                # Convert to points
                points = []
                # Use a subsample to avoid sending too much data if needed, or full data
                # For MCP, 500-1000 points is usually okay.
                # FastF1 telemetry is usually high freq.
                for _, row in tel_data.iterrows():
                    points.append(TelemetryPoint(
                        date=str(row['Date']),
                        session_time=str(row['SessionTime']),
                        driver=str(driver),
                        rpm=int(row['RPM']) if pd.notna(row.get('RPM')) else 0,
                        speed=float(row['Speed']) if pd.notna(row.get('Speed')) else 0.0,
                        throttle=float(row['Throttle']) if pd.notna(row.get('Throttle')) else 0.0,
                        brake=bool(row['Brake']) if pd.notna(row.get('Brake')) else False,
                        n_gear=int(row['nGear']) if pd.notna(row.get('nGear')) else 0,
                        drs=int(row['DRS']) if pd.notna(row.get('DRS')) else 0,
                        distance=float(row['Distance']) if pd.notna(row.get('Distance')) else 0.0,
                        relative_distance=float(row['RelativeDistance']) if pd.notna(row.get('RelativeDistance')) else 0.0,
                        x=float(row['X']) if pd.notna(row.get('X')) else 0.0,
                        y=float(row['Y']) if pd.notna(row.get('Y')) else 0.0,
                        z=float(row['Z']) if pd.notna(row.get('Z')) else 0.0,
                    ))

                telemetry_list.append(LapTelemetryResponse(
                    session_name=session_obj.name,
                    driver=str(driver),
                    lap_number=int(selected_lap['LapNumber']),
                    telemetry_points=points,
                    total_points=len(points),
                    lap_time=str(selected_lap['LapTime'])
                ))
            except Exception as e:
                pass
                
    return TelemetryDataResponse(drivers_telemetry=telemetry_list)

if __name__ == "__main__":
    print("Testing get_telemetry_data...")
    # 2024 Monaco Q
    res = get_telemetry_data(2024, "Monaco", "Q", ["VER", "LEC"])
    print(f"Got telemetry for {len(res.drivers_telemetry)} drivers")
    for tel in res.drivers_telemetry:
        print(f"Driver: {tel.driver}, Lap: {tel.lap_number}, Points: {tel.total_points}")
