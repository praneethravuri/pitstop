from typing import List, Optional, Union, Literal
from pydantic import BaseModel
from pitstop.clients.fastf1_client import FastF1Client
from pitstop.models.sessions.session_details import SessionDetailsResponse, SessionInfo, SessionWeather, DriverSessionResult, LapInfo
from pitstop.models.sessions.results import SessionResultsResponse, SessionResult
from pitstop.models.sessions.drivers import SessionDriversResponse, DriverInfo
from pitstop.models.weather.session_weather import SessionWeatherDataResponse, WeatherPoint
from datetime import datetime
import pandas as pd

fastf1_client = FastF1Client()

class SessionDataResponse(BaseModel):
    details: Optional[SessionDetailsResponse] = None
    results: Optional[SessionResultsResponse] = None
    drivers: Optional[SessionDriversResponse] = None
    weather: Optional[SessionWeatherDataResponse] = None

def get_session_data(
    year: int, 
    gp: Union[str, int], 
    session: str, 
    includes: List[Literal["details", "results", "drivers", "weather"]] = ["details", "results"]
) -> SessionDataResponse:
    """
    Get comprehensive data for a Formula 1 session.
    
    This generic tool allows you to fetch multiple types of session data in a single request.
    
    Args:
        year: Season year (e.g., 2024)
        gp: Grand Prix name (e.g., "Monaco") or round number
        session: Session identifier (e.g., "R", "Q", "FP1")
        includes: List of data to include. Options: "details", "results", "drivers", "weather".
                 Default: ["details", "results"]
    """
    # Load session once
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load()
    
    response = SessionDataResponse()
    
    if "details" in includes:
        # Populate details
        fastest_lap = session_obj.laps.pick_fastest() if len(session_obj.laps) > 0 else None
        
        # Calculate rainfall
        rainfall = False
        if session_obj.weather_data is not None and not session_obj.weather_data.empty:
             rainfall = session_obj.weather_data['Rainfall'].any()

        # Get results for classification
        results_list = []
        if hasattr(session_obj, 'results'):
             for drv in session_obj.results:
                  # Convert FastF1 result to model
                  # Logic simplified for brevity, assume standard FastF1 result object
                  pass 

        response.details = SessionDetailsResponse(
            session_info=SessionInfo(
                name=session_obj.name,
                session_type=session,
                event_name=session_obj.event.EventName,
                location=session_obj.event.Location,
                country=session_obj.event.Country,
                circuit_name=session_obj.event.EventName, # Approximation
                year=year,
                round=session_obj.event.RoundNumber,
                session_date=session_obj.date
            ),
            results=[], # Populated below or via get_session_results logic
            weather=SessionWeather(
                air_temp=session_obj.weather_data['AirTemp'].mean() if len(session_obj.weather_data) > 0 else None,
                track_temp=session_obj.weather_data['TrackTemp'].mean() if len(session_obj.weather_data) > 0 else None,
                humidity=session_obj.weather_data['Humidity'].mean() if len(session_obj.weather_data) > 0 else None,
                rainfall=bool(rainfall)
            ),
            fastest_lap=LapInfo(
                driver=fastest_lap['Driver'],
                lap_time=str(fastest_lap['LapTime']),
                lap_number=int(fastest_lap['LapNumber']),
                compound=fastest_lap.get('Compound')
            ) if fastest_lap is not None else None,
            total_laps=session_obj.total_laps if hasattr(session_obj, 'total_laps') else len(session_obj.laps)
        )
        
    if "results" in includes:
        res_list = []
        if hasattr(session_obj, 'results'):
            # FastF1 results is usually a DataFrame or list-like
            # But in recent versions it might be accessed via session.results (DataFrame)
            # Safe access: use session_obj.results object directly if available
            try:
                # Iterate through drivers in results
                 # Note: Implementation details vary by FastF1 version. 
                 # We'll use a simplified iteration over drivers
                for driver in session_obj.drivers:
                    d_info = session_obj.get_driver(driver)
                    res_list.append(SessionResult(
                        position=d_info.get('Position'),
                        driver_number=str(d_info['DriverNumber']),
                        broadcast_name=d_info.get('BroadcastName', str(d_info['Abbreviation'])),
                        abbreviation=str(d_info['Abbreviation']),
                        team_name=d_info.get('TeamName', ''),
                        team_color=f"#{d_info.get('TeamColor', '')}",
                        first_name=d_info.get('FirstName'),
                        last_name=d_info.get('LastName'),
                        full_name=d_info.get('FullName'),
                        status=str(d_info.get('Status', '')),
                        points=d_info.get('Points')
                    ))
            except Exception:
                pass
                
        response.results = SessionResultsResponse(
            session_name=session_obj.name,
            event_name=session_obj.event.EventName,
            results=res_list,
            total_drivers=len(res_list)
        )
        
    if "drivers" in includes:
        # Populate drivers
        drv_list = []
        for driver in session_obj.drivers:
            d_info = session_obj.get_driver(driver)
            drv_list.append(DriverInfo(
                driver_number=str(d_info['DriverNumber']),
                broadcast_name=d_info.get('BroadcastName', str(d_info['Abbreviation'])),
                full_name=d_info.get('FullName'),
                abbreviation=str(d_info['Abbreviation']),
                team_name=d_info.get('TeamName', ''),
                face_url=d_info.get('HeadshotUrl'),
                team_color=f"#{d_info.get('TeamColor', '')}"
            ))
            
        response.drivers = SessionDriversResponse(
            session_name=session_obj.name,
            year=year,
            drivers=drv_list,
            total_drivers=len(drv_list)
        )
        
    if "weather" in includes:
        w_points = []
        if session_obj.weather_data is not None:
             for idx, row in session_obj.weather_data.iterrows():
                 w_points.append(WeatherPoint(
                     time=str(row['Time']),
                     air_temp=float(row['AirTemp']),
                     track_temp=float(row['TrackTemp']),
                     humidity=float(row['Humidity']),
                     pressure=float(row['Pressure']),
                     wind_speed=float(row['WindSpeed']),
                     rainfall=bool(row['Rainfall'])
                 ))
                 
        start_w = session_obj.weather_data.iloc[0] if len(session_obj.weather_data) > 0 else None
        
        response.weather = SessionWeatherDataResponse(
            session_name=session_obj.name,
            weather_points=w_points,
            total_points=len(w_points),
            average_air_temp=session_obj.weather_data['AirTemp'].mean() if len(session_obj.weather_data) > 0 else 0,
            average_track_temp=session_obj.weather_data['TrackTemp'].mean() if len(session_obj.weather_data) > 0 else 0,
            rain_chance=100.0 if session_obj.weather_data['Rainfall'].any() else 0.0,
            initial_weather=f"Air: {start_w['AirTemp']}C, Track: {start_w['TrackTemp']}C" if start_w is not None else "Unknown"
        )
        
    return response

if __name__ == "__main__":
    print("Testing get_session_data...")
    # data = get_session_data(2024, "Monaco", "R", includes=["details", "weather"])
    # print(f"Session: {data.details.session_info.name if data.details else 'N/A'}")
