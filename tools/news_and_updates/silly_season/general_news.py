from clients.rss_client import RSSClient
from models import SillySeasonResponse
from datetime import datetime
from .filters import (
    filter_news_by_keywords,
    TRANSFER_KEYWORDS,
    MANAGEMENT_KEYWORDS,
    CONTRACT_KEYWORDS,
    TEAM_KEYWORDS
)

# Initialize RSS client
rss_client = RSSClient()


def silly_season_news(
    year: int | None = None,
    driver: str | None = None,
    constructor: str | None = None,
    limit: int = 20
) -> SillySeasonResponse:
    """
    Get Formula 1 silly season news including driver transfers, team changes, and rumors.

    Fetches the latest silly season news from multiple F1 sources, filtering for
    transfer rumors, contract negotiations, driver movements, and team changes.
    Can be filtered by year, specific driver, or constructor.

    Args:
        year: Filter news by specific year (e.g., 2024, 2025). If None, returns all recent news.
        driver: Filter by driver name (e.g., "Hamilton", "Verstappen", "Leclerc")
        constructor: Filter by team/constructor name (e.g., "Ferrari", "Mercedes", "Red Bull")
        limit: Maximum number of articles to return (1-50). Default: 20

    Returns:
        SillySeasonResponse: Silly season news articles with titles, links, publication dates,
        summaries, source, category, and relevance scores. Articles are sorted by relevance.

    Examples:
        >>> # Get all silly season news
        >>> news = silly_season_news()

        >>> # Get silly season news for 2025
        >>> news_2025 = silly_season_news(year=2025)

        >>> # Get silly season news about Hamilton
        >>> hamilton_news = silly_season_news(driver="Hamilton")

        >>> # Get silly season news about Ferrari
        >>> ferrari_news = silly_season_news(constructor="Ferrari", limit=15)
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    # Determine query type and value
    query_type = "general"
    query_value = None

    if year:
        query_type = "year"
        query_value = str(year)
    elif driver:
        query_type = "driver"
        query_value = driver
    elif constructor:
        query_type = "constructor"
        query_value = constructor

    # Fetch news from all sources with increased limit to ensure enough results after filtering
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Combine all silly season keywords
    all_keywords = TRANSFER_KEYWORDS + MANAGEMENT_KEYWORDS + CONTRACT_KEYWORDS + TEAM_KEYWORDS

    # Filter articles
    filtered_articles = filter_news_by_keywords(
        news_response.articles,
        all_keywords,
        "silly_season",
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
