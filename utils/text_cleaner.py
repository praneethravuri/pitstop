import re
import html


def clean_html(text: str) -> str:
    """
    Clean HTML tags and entities from text.

    Removes HTML tags, decodes HTML entities, and normalizes whitespace
    to produce clean, readable plain text.

    Args:
        text: Text potentially containing HTML tags and entities

    Returns:
        str: Cleaned plain text with HTML removed and whitespace normalized
    """
    if not text:
        return ""

    # Decode HTML entities (e.g., &amp; -> &, &quot; -> ")
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^<]+?>", "", text)

    # Remove extra whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.

    Args:
        text: Text to truncate
        max_length: Maximum length of the resulting text (including suffix)
        suffix: String to append if text is truncated (default: "...")

    Returns:
        str: Truncated text with suffix, or original text if under max_length
    """
    if len(text) <= max_length:
        return text

    # Account for suffix length
    truncate_at = max_length - len(suffix)

    # Try to truncate at a word boundary
    truncated = text[:truncate_at].rsplit(" ", 1)[0]

    return truncated + suffix


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Replaces multiple spaces, tabs, and newlines with single spaces,
    and removes leading/trailing whitespace.

    Args:
        text: Text to normalize

    Returns:
        str: Text with normalized whitespace
    """
    # Replace multiple whitespace characters with single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    return text.strip()
