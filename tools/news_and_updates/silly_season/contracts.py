from clients.rss_client import RSSClient
from models import SillySeasonResponse
from datetime import datetime
from .filters import filter_news_by_keywords, CONTRACT_KEYWORDS

# Initialize RSS client
rss_client = RSSClient()


def contract_news(
    driver: str | None = None,
    constructor: str | None = None,
    limit: int = 15
) -> SillySeasonResponse:
    """
    Get contract-related news including renewals, extensions, and expirations.

    Fetches news about driver and team contract situations, including renewals,
    extensions, expirations, and new signings. Can be filtered by driver or team.

    Args:
        driver: Filter by driver name (e.g., "Norris", "Piastri", "Alonso")
        constructor: Filter by team/constructor name (e.g., "McLaren", "Aston Martin")
        limit: Maximum number of articles to return (1-50). Default: 15

    Returns:
        SillySeasonResponse: Contract-related news articles including extensions,
        renewals, expirations, and multi-year deals.

    Examples:
        >>> # Get all contract news
        >>> contracts = contract_news()

        >>> # Get contract news about Norris
        >>> norris_contracts = contract_news(driver="Norris")

        >>> # Get contract news about McLaren
        >>> mclaren_contracts = contract_news(constructor="McLaren")

        >>> # Get more contract news
        >>> more_contracts = contract_news(limit=25)
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "contract_news"
    query_value = driver or constructor

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for contract news
    filtered_articles = filter_news_by_keywords(
        news_response.articles,
        CONTRACT_KEYWORDS,
        "contract",
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
