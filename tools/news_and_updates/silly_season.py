from clients.rss_client import RSSClient
from models.silly_season import SillySeasonResponse, SillySeasonArticle
from datetime import datetime

# Initialize RSS client
rss_client = RSSClient()

# Keyword sets for different silly season categories
TRANSFER_KEYWORDS = [
    "transfer", "move", "join", "signing", "signs", "switched", "switches",
    "rumor", "rumour", "linked", "target", "interest", "approach", "speculation",
    "deal", "negotiation", "contract negotiation"
]

MANAGEMENT_KEYWORDS = [
    "team principal", "technical director", "sporting director", "ceo",
    "resign", "resignation", "appointed", "appointment", "hire", "hiring",
    "depart", "departure", "replacement", "promoted", "promotion",
    "restructure", "management change"
]

CONTRACT_KEYWORDS = [
    "contract", "extension", "renewal", "renew", "extends", "extended",
    "expire", "expiring", "sign", "signed", "commit", "committed",
    "multi-year", "option", "clause"
]

TEAM_KEYWORDS = [
    "new team", "entry", "join grid", "franchise", "expansion",
    "sponsor", "sponsorship", "partnership", "technical partner",
    "supplier", "engine supplier", "power unit", "switch"
]


def _filter_news_by_keywords(
    articles: list,
    keywords: list[str],
    category: str,
    query_value: str | None = None
) -> list[SillySeasonArticle]:
    """
    Filter news articles by keywords and calculate relevance score.

    Args:
        articles: List of NewsArticle objects
        keywords: List of keywords to search for
        category: Category name for the articles
        query_value: Optional filter value (driver name, team name, year)

    Returns:
        List of filtered SillySeasonArticle objects with relevance scores
    """
    filtered = []

    for article in articles:
        # Combine title and summary for searching
        content = f"{article.title} {article.summary}".lower()

        # Check if any keywords match
        matching_keywords = [kw for kw in keywords if kw.lower() in content]

        # If query_value is provided, check if it's in the content
        if query_value:
            query_match = query_value.lower() in content
            if not query_match:
                continue

        if matching_keywords:
            # Calculate relevance score based on keyword matches
            relevance_score = min(len(matching_keywords) / 3.0, 1.0)

            filtered.append(
                SillySeasonArticle(
                    title=article.title,
                    link=article.link,
                    published=article.published,
                    summary=article.summary,
                    source=article.source,
                    author=article.author,
                    category=category,
                    relevance_score=relevance_score
                )
            )

    # Sort by relevance score (highest first)
    filtered.sort(key=lambda x: x.relevance_score or 0, reverse=True)
    return filtered


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
    filtered_articles = _filter_news_by_keywords(
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
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "transfer_rumors"
    query_value = driver

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for transfer news
    filtered_articles = _filter_news_by_keywords(
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
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "management_changes"
    query_value = constructor

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for management news
    filtered_articles = _filter_news_by_keywords(
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
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    query_type = "contract_news"
    query_value = driver or constructor

    # Fetch news with increased limit
    news_response = rss_client.get_news(source="all", limit=max(limit * 2, 30))

    # Filter for contract news
    filtered_articles = _filter_news_by_keywords(
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
