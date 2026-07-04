import html
import re


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
