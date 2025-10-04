from clients.rss_client import RSSClient
from models import SillySeasonResponse
from datetime import datetime
from .filters import filter_news_by_keywords, TRANSFER_KEYWORDS

# Initialize RSS client
rss_client = RSSClient()


def driver_transfer_rumors(
    driver: str | None = None,
    limit: int = 15
) -> SillySeasonResponse:
    """
    Get the latest driver transfer rumors and speculation.

    Fetches news specifically about driver transfers, signings, and movement rumors.
    Can be filtered to show rumors about a specific driver.

    Args:
        driver: Filter by specific driver name (e.g., "Hamilton", "Sainz", "Ocon").
                If None, returns all transfer rumors.
        limit: Maximum number of articles to return (1-50). Default: 15

    Returns:
        SillySeasonResponse: Transfer-related news articles sorted by relevance,
        including rumored moves, confirmed signings, and contract negotiations.

    Examples:
        >>> # Get all driver transfer rumors
        >>> rumors = driver_transfer_rumors()

        >>> # Get transfer rumors about Sainz
        >>> sainz_rumors = driver_transfer_rumors(driver="Sainz")

        >>> # Get more transfer rumors
        >>> more_rumors = driver_transfer_rumors(limit=30)
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "transfer_rumors"
    query_value = driver

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for transfer news
    filtered_articles = filter_news_by_keywords(
        news_response.articles,
        TRANSFER_KEYWORDS,
        "driver_transfer",
        query_value
    )

    # Limit results
    filtered_articles = filtered_articles[:limit]

    return SillySeasonResponse(
        query_type=query_type,
        query_value=query_value,
        fetched_at=datetime.now().isoformat(),
        article_count=len(filtered_articles),
        articles=filtered_articles
    )
