from clients.rss_client import RSSClient
from models import NewsResponse

# Initialize RSS client
rss_client = RSSClient()


def f1_news(source: str = "formula1", limit: int = 10) -> NewsResponse:
    """
    Get the latest Formula 1 news from RSS feeds.

    Stay up-to-date with breaking F1 news, race results, driver updates,
    team announcements, and technical developments from trusted motorsport sources.

    Args:
        source: News source to fetch from. Options: "formula1" (official F1 website),
                "fia" (FIA press releases), "autosport", "the-race", "racefans",
                "planetf1", "motorsport", "all". Default: "formula1"
        limit: Maximum number of articles to return per source (1-50). Default: 10

    Returns:
        NewsResponse: Latest news articles with titles, links, publication dates,
        summaries, and source information. Each article includes the headline,
        full article URL, publication timestamp, excerpt, and source name.
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return rss_client.get_news(source=source, limit=limit)


def latest_f1_news(source: str = "all", limit: int = 15) -> NewsResponse:
    """
    Get the latest Formula 1 news from multiple trusted sources.

    Fetches breaking F1 news including race results, driver announcements, team updates,
    technical developments, FIA statements, and more from trusted motorsport media.

    Args:
        source: News source to fetch from. Options: "formula1" (official F1 website),
                "fia" (FIA press releases), "autosport", "the-race", "racefans",
                "planetf1", "motorsport", "all". Default: "all"
        limit: Maximum number of articles to return per source (1-50). Default: 15

    Returns:
        NewsResponse: Latest news articles with titles, links, publication dates,
        summaries, and source information. Includes driver announcements, team changes,
        rule updates, race reports, and technical news.
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return rss_client.get_news(source=source, limit=limit)
