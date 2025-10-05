from clients.rss_client import RSSClient
from models import NewsResponse, SillySeasonResponse
from datetime import datetime
from typing import Optional, Literal
from .silly_season.filters import (
    filter_news_by_keywords,
    TRANSFER_KEYWORDS,
    MANAGEMENT_KEYWORDS,
    CONTRACT_KEYWORDS
)

# Initialize RSS client
rss_client = RSSClient()


def get_f1_news(
    source: str = "formula1",
    limit: int = 10,
    category: Optional[Literal["general", "transfers", "management", "contracts", "silly_season"]] = "general",
    driver: Optional[str] = None,
    team: Optional[str] = None,
    year: Optional[int] = None
):
    """
    Get Formula 1 news with flexible filtering options.

    A composable function to retrieve F1 news - general news, silly season rumors,
    transfer news, management changes, or contract updates. Use this single tool
    for all news-related queries instead of multiple separate tools.

    Use this tool to:
    - Get general F1 news from various sources
    - Find driver transfer rumors and confirmed moves
    - Track team management changes and appointments
    - Monitor contract renewals, extensions, and expirations
    - Filter silly season news by driver, team, or year

    Args:
        source: News source - "formula1" (official F1), "fia", "autosport",
                "the-race", "racefans", "planetf1", "motorsport", or "all"
                Default: "formula1"
        limit: Maximum number of articles to return (1-50). Default: 10
        category: News category - "general" (all F1 news), "transfers" (driver moves),
                 "management" (team leadership), "contracts" (renewals/extensions),
                 "silly_season" (all silly season news). Default: "general"
        driver: Optional - Filter by driver name (e.g., "Hamilton", "Verstappen")
                Works with transfers, contracts, and silly_season categories
        team: Optional - Filter by team/constructor (e.g., "Ferrari", "Red Bull", "McLaren")
              Works with management, contracts, and silly_season categories
        year: Optional - Filter by year (e.g., 2024, 2025)
              Works with silly_season category

    Returns:
        NewsResponse or SillySeasonResponse: News articles with titles, links,
        publication dates, summaries, and source information. Silly season news
        includes relevance scores and is sorted by relevance.

    Examples:
        >>> # Get latest general F1 news from official website
        >>> news = get_f1_news()

        >>> # Get news from all sources
        >>> all_news = get_f1_news(source="all", limit=20)

        >>> # Get driver transfer rumors
        >>> transfers = get_f1_news(category="transfers", limit=15)

        >>> # Get transfer rumors about a specific driver
        >>> sainz_rumors = get_f1_news(category="transfers", driver="Sainz")

        >>> # Get team management changes
        >>> management = get_f1_news(category="management")

        >>> # Get management news for Ferrari
        >>> ferrari_mgmt = get_f1_news(category="management", team="Ferrari")

        >>> # Get contract news
        >>> contracts = get_f1_news(category="contracts")

        >>> # Get contract news for a driver
        >>> hamilton_contract = get_f1_news(category="contracts", driver="Hamilton")

        >>> # Get all silly season news for 2025
        >>> silly_2025 = get_f1_news(category="silly_season", year=2025, limit=20)

        >>> # Get silly season news about Red Bull
        >>> rb_silly = get_f1_news(category="silly_season", team="Red Bull")
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    # Handle general news category
    if category == "general":
        return rss_client.get_news(source=source, limit=limit)

    # For filtered categories, fetch from all sources with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Apply filtering based on category
    if category == "transfers":
        filtered_articles = filter_news_by_keywords(
            news_response.articles,
            TRANSFER_KEYWORDS,
            "driver_transfer",
            driver
        )
        query_type = "transfer_rumors"
        query_value = driver

    elif category == "management":
        filtered_articles = filter_news_by_keywords(
            news_response.articles,
            MANAGEMENT_KEYWORDS,
            "team_management",
            team
        )
        query_type = "management_changes"
        query_value = team

    elif category == "contracts":
        # Combine driver and team filtering for contracts
        query_value = driver or team
        filtered_articles = filter_news_by_keywords(
            news_response.articles,
            CONTRACT_KEYWORDS,
            "contract",
            query_value
        )
        query_type = "contract_news"

    elif category == "silly_season":
        # Combine all silly season keywords
        all_keywords = TRANSFER_KEYWORDS + MANAGEMENT_KEYWORDS + CONTRACT_KEYWORDS
        # Apply filters for year, driver, or team
        query_value = driver or team or (str(year) if year else None)
        filtered_articles = filter_news_by_keywords(
            news_response.articles,
            all_keywords,
            "silly_season",
            query_value
        )
        query_type = "silly_season"

    else:
        # Default to general if unknown category
        return rss_client.get_news(source=source, limit=limit)

    # Limit results
    filtered_articles = filtered_articles[:limit]

    # Return appropriate response type
    return SillySeasonResponse(
        query_type=query_type,
        query_value=query_value,
        fetched_at=datetime.now().isoformat(),
        article_count=len(filtered_articles),
        articles=filtered_articles
    )
