from datetime import datetime


def validate_f1_year(year: int) -> bool:
    """
    Validate if a year is valid for F1 data.
    F1 started in 1950 and continues to present.

    Args:
        year: The year to validate

    Returns:
        bool: True if year is valid, False otherwise
    """
    current_year = datetime.now().year
    return 1950 <= year <= current_year


def get_valid_year_range() -> tuple[int, int]:
    """
    Get the valid year range for F1 data.

    Returns:
        tuple: (start_year, current_year)
    """
    current_year = datetime.now().year
    return (1950, current_year)
