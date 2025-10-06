from clients.fastf1_client import FastF1Client
from typing import Union
from models.control import RaceControlMessagesResponse, RaceControlMessage
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_race_control_messages(year: int, gp: Union[str, int], session: str) -> RaceControlMessagesResponse:
    """
    Get official race control messages for a session.

    Retrieves all race control messages issued during a session, including
    flags, safety car periods, investigations, penalties, and track status changes.
    Essential for understanding session events and incidents.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        RaceControlMessagesResponse: Race control messages in JSON-serializable format

    Examples:
        >>> # Get all race control messages from 2024 Monaco race
        >>> messages = get_race_control_messages(2024, "Monaco", "R")

        >>> # Check safety car deployments and flags
        >>> race_msgs = get_race_control_messages(2024, "Spa", "R")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)

    event = session_obj.event
    messages_df = session_obj.race_control_messages

    # Convert to Pydantic models
    messages_list = []
    for idx, row in messages_df.iterrows():
        message = RaceControlMessage(
            time=str(row['Time']) if pd.notna(row.get('Time')) else None,
            category=str(row['Category']) if pd.notna(row.get('Category')) else None,
            message=str(row['Message']) if pd.notna(row.get('Message')) else None,
            status=str(row['Status']) if pd.notna(row.get('Status')) else None,
            flag=str(row['Flag']) if pd.notna(row.get('Flag')) else None,
            scope=str(row['Scope']) if pd.notna(row.get('Scope')) else None,
            sector=float(row['Sector']) if pd.notna(row.get('Sector')) else None,
            racing_number=str(row['RacingNumber']) if pd.notna(row.get('RacingNumber')) else None,
        )
        messages_list.append(message)

    return RaceControlMessagesResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        messages=messages_list,
        total_messages=len(messages_list)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco Grand Prix Race
    print("Testing get_race_control_messages with 2024 Monaco GP Race...")
    messages = get_race_control_messages(2024, "Monaco", "R")
    print(f"\nSession: {messages.session_name}")
    print(f"Total race control messages: {messages.total_messages}")

    # Count categories
    if messages.messages:
        categories = {}
        for msg in messages.messages:
            cat = msg.category or "Unknown"
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\nMessage categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")

        print(f"\nFirst message:")
        print(f"  Time: {messages.messages[0].time}")
        print(f"  Category: {messages.messages[0].category}")
        print(f"  Message: {messages.messages[0].message}")

    # Test JSON serialization
    print(f"\nJSON: {messages.model_dump_json()[:100]}...")
