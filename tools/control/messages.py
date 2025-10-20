from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.control import RaceControlMessagesResponse, RaceControlMessage
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_race_control_messages(
    year: int,
    gp: Union[str, int],
    session: str,
    message_type: Optional[Literal["all", "penalties", "investigations", "flags", "safety_car"]] = "all"
) -> RaceControlMessagesResponse:
    """
    Get race control messages - flags, safety cars, investigations, penalties.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        message_type: Filter type - 'all', 'penalties', 'investigations', 'flags', 'safety_car' (default: 'all')

    Returns:
        RaceControlMessagesResponse with filtered messages

    Examples:
        get_race_control_messages(2024, "Monaco", "R") → All race control messages
        get_race_control_messages(2024, "Monaco", "R", "penalties") → Penalties only
        get_race_control_messages(2024, "Monaco", "R", "flags") → Flag periods only
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)

    event = session_obj.event
    messages_df = session_obj.race_control_messages

    # Define filter keywords based on message type
    filter_keywords = {
        "penalties": ['penalty', 'penalties', 'penalised', 'penalized', 'reprimand',
                      'time penalty', 'grid penalty', 'warning', 'fine', 'disqualified'],
        "investigations": ['investigation', 'investigated', 'under investigation', 'incident',
                          'noted', 'will be investigated', 'under review', 'reported'],
        "flags": ['yellow', 'red flag', 'green', 'double yellow', 'track clear', 'all clear'],
        "safety_car": ['safety car', 'virtual safety', 'vsc', 'sc deployed', 'sc ending']
    }

    # Convert to Pydantic models with optional filtering
    messages_list = []
    for idx, row in messages_df.iterrows():
        message_text = str(row.get('Message', '')).lower()
        category = str(row.get('Category', '')).lower()
        flag = str(row.get('Flag', '')).lower() if pd.notna(row.get('Flag')) else ''

        # Apply filter if not "all"
        if message_type != "all":
            keywords = filter_keywords.get(message_type, [])

            # Check if message matches filter
            matches = False
            if message_type == "flags":
                # For flags, also check the Flag column
                matches = (any(keyword in message_text for keyword in keywords) or
                          any(keyword in category for keyword in keywords) or
                          (pd.notna(row.get('Flag')) and row.get('Flag') not in ['', 'CLEAR']))
            else:
                matches = (any(keyword in message_text for keyword in keywords) or
                          any(keyword in category for keyword in keywords))

            if not matches:
                continue

        # Add message to list
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
