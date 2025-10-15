from clients.fastf1_client import FastF1Client
from typing import Union
from models.control import RaceControlMessagesResponse, RaceControlMessage
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_penalties(year: int, gp: Union[str, int], session: str) -> RaceControlMessagesResponse:
    """
    Get penalty decisions from race control - time penalties, grid drops, warnings.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        RaceControlMessagesResponse with penalty messages only

    Example:
        get_penalties(2024, "Monaco", "R") → All penalty decisions
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)

    event = session_obj.event
    messages_df = session_obj.race_control_messages

    # Filter for penalty-related messages
    penalty_keywords = ['penalty', 'penalties', 'penalised', 'penalized', 'reprimand',
                       'time penalty', 'grid penalty', 'warning', 'fine', 'disqualified']

    penalty_messages = []
    for idx, row in messages_df.iterrows():
        message_text = str(row.get('Message', '')).lower()
        category = str(row.get('Category', '')).lower()

        # Check if message is penalty-related
        if any(keyword in message_text for keyword in penalty_keywords) or \
           any(keyword in category for keyword in penalty_keywords):
            penalty_messages.append(
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
        messages=penalty_messages,
        total_messages=len(penalty_messages)
    )


def get_investigations(year: int, gp: Union[str, int], session: str) -> RaceControlMessagesResponse:
    """
    Get investigation notices from race control - incidents under review.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        RaceControlMessagesResponse with investigation messages only

    Example:
        get_investigations(2024, "Monaco", "R") → All investigation notices
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)

    event = session_obj.event
    messages_df = session_obj.race_control_messages

    # Filter for investigation-related messages
    investigation_keywords = ['investigation', 'investigated', 'under investigation', 'incident',
                             'noted', 'will be investigated', 'under review', 'reported']

    investigation_messages = []
    for idx, row in messages_df.iterrows():
        message_text = str(row.get('Message', '')).lower()
        category = str(row.get('Category', '')).lower()

        # Check if message is investigation-related
        if any(keyword in message_text for keyword in investigation_keywords) or \
           any(keyword in category for keyword in investigation_keywords):
            investigation_messages.append(
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
        messages=investigation_messages,
        total_messages=len(investigation_messages)
    )


if __name__ == "__main__":
    # Test penalties
    print("Testing get_penalties with 2024 Monaco GP Race...")
    penalties = get_penalties(2024, "Monaco", "R")
    print(f"Total penalties: {penalties.total_messages}")
    if penalties.messages:
        print(f"First penalty: {penalties.messages[0].message}")

    # Test investigations
    print("\nTesting get_investigations with 2024 Monaco GP Race...")
    investigations = get_investigations(2024, "Monaco", "R")
    print(f"Total investigations: {investigations.total_messages}")
    if investigations.messages:
        print(f"First investigation: {investigations.messages[0].message}")
