from clients.rss_client import RSSClient
from models import SillySeasonResponse
from datetime import datetime
from .filters import filter_news_by_keywords, MANAGEMENT_KEYWORDS

# Initialize RSS client
rss_client = RSSClient()


def team_management_changes(
    constructor: str | None = None,
    limit: int = 15
) -> SillySeasonResponse:
    """
    Get news about team management changes including team principals and technical directors.

    Fetches news about management appointments, departures, and restructuring within F1 teams.
    Includes team principals, technical directors, sporting directors, and other key positions.

    Args:
        constructor: Filter by team/constructor name (e.g., "Ferrari", "Alpine", "Williams").
                    If None, returns all management change news.
        limit: Maximum number of articles to return (1-50). Default: 15

    Returns:
        SillySeasonResponse: Management-related news articles including appointments,
        resignations, promotions, and team restructuring news.

    Examples:
        >>> # Get all management change news
        >>> changes = team_management_changes()

        >>> # Get management changes at Ferrari
        >>> ferrari_changes = team_management_changes(constructor="Ferrari")

        >>> # Get more management news
        >>> more_changes = team_management_changes(limit=25)
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "management_changes"
    query_value = constructor

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for management news
    filtered_articles = filter_news_by_keywords(
        news_response.articles,
        MANAGEMENT_KEYWORDS,
        "team_management",
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
