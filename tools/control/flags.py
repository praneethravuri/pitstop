from clients.fastf1_client import FastF1Client
from typing import Union
from models.control import RaceControlMessagesResponse, RaceControlMessage
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_flag_history(year: int, gp: Union[str, int], session: str) -> RaceControlMessagesResponse:
    """
    Get all flag periods (yellow, red, safety car, virtual safety car) from race control.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        RaceControlMessagesResponse with flag-related messages only

    Example:
        get_flag_history(2024, "Monaco", "R") → All flag periods during race
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)

    event = session_obj.event
    messages_df = session_obj.race_control_messages

    # Filter for flag-related messages
    flag_keywords = ['yellow', 'red flag', 'green', 'safety car', 'virtual safety',
                     'vsc', 'sc deployed', 'sc ending', 'double yellow',
                     'track clear', 'all clear']

    flag_messages = []
    for idx, row in messages_df.iterrows():
        message_text = str(row.get('Message', '')).lower()
        category = str(row.get('Category', '')).lower()
        flag = str(row.get('Flag', '')).lower()

        # Check if message is flag-related
        if any(keyword in message_text for keyword in flag_keywords) or \
           any(keyword in category for keyword in flag_keywords) or \
           (pd.notna(row.get('Flag')) and row.get('Flag') not in ['', 'CLEAR']):
            flag_messages.append(
                RaceControlMessage(
                    time=str(row['Time']) if pd.notna(row.get('Time')) else None,
                    category=str(row['Category']) if pd.notna(row.get('Category')) else None,
                    message=str(row['Message']) if pd.notna(row.get('Message')) else None,
                    status=str(row['Status']) if pd.notna(row.get('Status')) else None,
                    flag=str(row['Flag']) if pd.notna(row.get('Flag')) else None,
                    scope=str(row['Scope']) if pd.notna(row.get('Scope')) else None,
                    sector=float(row['Sector']) if pd.notna(row.get('Sector')) else None,
                    racing_number=str(row['RacingNumber']) if pd.notna(row.get('RacingNumber')) else None,
                )
            )

    return RaceControlMessagesResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        messages=flag_messages,
        total_messages=len(flag_messages)
    )


if __name__ == "__main__":
    # Test flag history
    print("Testing get_flag_history with 2024 Monaco GP Race...")
    flags = get_flag_history(2024, "Monaco", "R")
    print(f"Total flag periods: {flags.total_messages}")
    if flags.messages:
        print(f"First flag: {flags.messages[0].message}")
