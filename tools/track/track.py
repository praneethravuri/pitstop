from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.track import (
    CircuitDataResponse,
    CircuitDetails,
    CornerInfo,
    TrackStatusInfo,
)
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_circuit(
    year: int,
    gp: Union[str, int],
    data_type: Literal["circuit_info", "track_status"] = "circuit_info",
    session: Optional[str] = None,
) -> CircuitDataResponse:
    """
    Get circuit layout, corners, or track status (flags, safety car).

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        data_type: 'circuit_info' (layout/corners) or 'track_status' (flags)
        session: Required for track_status ('FP1', 'FP2', 'FP3', 'Q', 'S', 'R')

    Returns:
        CircuitDataResponse with circuit details or track status changes

    Examples:
        get_circuit(2024, "Monaco", "circuit_info") → Circuit layout and corners
        get_circuit(2024, "Monaco", "track_status", session="R") → Flag periods
    """
    # Get event information
    event = fastf1_client.get_event(year, gp)

    if data_type == "circuit_info":
        # Load a session to get circuit info (use Race or first available session)
        if session:
            session_obj = fastf1_client.get_session(year, gp, session)
        else:
            # Try to get race session, fallback to any available
            try:
                session_obj = fastf1_client.get_session(year, gp, 'R')
            except Exception:
                try:
                    session_obj = fastf1_client.get_session(year, gp, 'Q')
                except Exception:
                    session_obj = fastf1_client.get_session(year, gp, 1)

        session_obj.load()

        # Get circuit information
        try:
            circuit_info = session_obj.get_circuit_info()

            # Extract corner information
            corners_list = []
            if circuit_info.corners is not None and len(circuit_info.corners) > 0:
                for idx, corner in circuit_info.corners.iterrows():
                    corners_list.append(
                        CornerInfo(
                            number=int(corner['Number']) if pd.notna(corner.get('Number')) else idx,
                            letter=str(corner['Letter']) if pd.notna(corner.get('Letter')) else None,
                            distance=float(corner['Distance']) if pd.notna(corner.get('Distance')) else None,
                            x=float(corner['X']) if pd.notna(corner.get('X')) else None,
                            y=float(corner['Y']) if pd.notna(corner.get('Y')) else None,
                        )
                    )

            circuit_details = CircuitDetails(
                circuit_key=int(circuit_info.circuit_key) if hasattr(circuit_info, 'circuit_key') and circuit_info.circuit_key else None,
                circuit_name=str(event['EventName']) if event is not None else None,
                location=str(event['Location']) if event is not None else None,
                country=str(event['Country']) if event is not None else None,
                rotation=float(circuit_info.rotation) if hasattr(circuit_info, 'rotation') and circuit_info.rotation else None,
                corners=corners_list if corners_list else None,
            )
        except Exception as e:
            # If circuit info not available, provide basic event info
            circuit_details = CircuitDetails(
                circuit_name=str(event['EventName']) if event is not None else None,
                location=str(event['Location']) if event is not None else None,
                country=str(event['Country']) if event is not None else None,
            )

        return CircuitDataResponse(
            year=year,
            event_name=str(event['EventName']) if event is not None else "",
            session_name=None,
            circuit_details=circuit_details,
            data_type=data_type,
        )

    elif data_type == "track_status":
        if not session:
            raise ValueError("session parameter is required for track_status data type")

        # Load session with track status data
        session_obj = fastf1_client.get_session(year, gp, session)
        session_obj.load()

        # Get track status data
        track_status_df = session_obj.track_status
        track_status_list = []

        if track_status_df is not None and len(track_status_df) > 0:
            for idx, row in track_status_df.iterrows():
                # Map status codes to messages
                status_code = str(row['Status'])
                status_messages = {
                    '1': 'Green Flag / Track Clear',
                    '2': 'Yellow Flag / Caution',
                    '3': 'Green Flag (after SC)',
                    '4': 'Safety Car',
                    '5': 'Red Flag / Session Stopped',
                    '6': 'Virtual Safety Car (VSC)',
                    '7': 'VSC Ending',
                }
                message = status_messages.get(status_code, f'Status Code {status_code}')

                track_status_list.append(
                    TrackStatusInfo(
                        time=str(row['Time']) if pd.notna(row.get('Time')) else "",
                        status=status_code,
                        message=message,
                    )
                )

        return CircuitDataResponse(
            year=year,
            event_name=str(event['EventName']) if event is not None else "",
            session_name=session_obj.name if hasattr(session_obj, 'name') else session,
            track_status=track_status_list,
            data_type=data_type,
        )


if __name__ == "__main__":
    # Test circuit functionality
    print("Testing get_circuit...")

    # Test 1: Get Monaco circuit info
    print("\n1. Getting Monaco 2024 circuit information:")
    monaco = get_circuit(2024, "Monaco", "circuit_info")
    print(f"   Circuit: {monaco.circuit_details.circuit_name}")
    print(f"   Location: {monaco.circuit_details.location}, {monaco.circuit_details.country}")
    if monaco.circuit_details.corners:
        print(f"   Number of corners: {len(monaco.circuit_details.corners)}")
        print(f"   First corner: #{monaco.circuit_details.corners[0].number}")

    # Test 2: Get track status for Monaco race
    print("\n2. Getting Monaco 2024 Race track status:")
    status = get_circuit(2024, "Monaco", "track_status", session="R")
    print(f"   Session: {status.session_name}")
    if status.track_status:
        print(f"   Status changes: {len(status.track_status)}")
        print(f"   First status: {status.track_status[0].message}")

    # Test 3: Get Silverstone circuit
    print("\n3. Getting Silverstone 2024 circuit information:")
    silverstone = get_circuit(2024, "Silverstone", "circuit_info")
    print(f"   Circuit: {silverstone.circuit_details.circuit_name}")

    # Test JSON serialization
    print(f"\n   JSON: {monaco.model_dump_json()[:150]}...")
