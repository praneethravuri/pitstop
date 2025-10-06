from clients.rss_client import RSSClient
from models import NewsResponse
from datetime import datetime
from typing import Optional, Literal

# Initialize RSS client
rss_client = RSSClient()

# Keyword sets for different news categories
CATEGORY_KEYWORDS = {
    "transfers": [
        "transfer", "move", "sign", "join", "switch", "switch to", "rumour", "rumor",
        "linked", "target", "interest", "reportedly", "deal", "agreement", "swap",
        "loan", "option", "clause", "leaving", "exit", "departure", "replace"
    ],
    "contracts": [
        "contract", "extension", "renewal", "extend", "renew", "signed", "deal",
        "agreement", "multi-year", "option", "expire", "expiring", "expire at",
        "terms", "negotiate", "negotiation", "re-sign", "commit"
    ],
    "technical": [
        "upgrade", "development", "aero", "aerodynamic", "chassis", "engine",
        "power unit", "regulation", "technical", "innovation", "design", "concept",
        "performance", "wind tunnel", "CFD", "floor", "sidepod", "rear wing", "front wing"
    ],
    "calendar": [
        "calendar", "schedule", "race", "grand prix", "venue", "circuit", "track",
        "postpone", "cancel", "reschedule", "new race", "date", "host", "return",
        "rotation", "contract extension", "race weekend", "sprint"
    ],
    "regulations": [
        "regulation", "rule", "FIA", "sporting", "technical directive", "clarification",
        "illegal", "legal", "penalty", "fine", "ban", "sanction", "investigation",
        "protest", "appeal", "steward"
    ],
    "management": [
        "team principal", "CEO", "manage", "appoint", "hire", "resign", "leave",
        "director", "technical director", "sporting director", "depart", "join as",
        "promote", "reshuffle", "reorganize", "restructure", "leadership"
    ]
}


def get_f1_news(
    source: str = "all",
    limit: int = 10,
    category: Optional[Literal["general", "transfers", "contracts", "technical", "calendar", "regulations", "management"]] = "general",
    filter_text: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> NewsResponse:
    """
    Get Formula 1 news with flexible filtering options.

    A unified tool to retrieve all types of F1 news - latest updates, driver transfers,
    technical developments, calendar changes, regulations, contracts, and more.

    Use this tool to:
    - Get latest F1 news from various sources
    - Find driver transfer rumors and confirmed moves
    - Track technical developments and upgrades
    - Monitor calendar changes and new races
    - Follow regulation changes and FIA decisions
    - Track contract renewals, extensions, and expirations
    - Monitor team management changes

    Args:
        source: News source - "formula1", "fia", "autosport", "motorsport", "the-race",
                "racefans", "planetf1", "crash", "gpblog", "f1-insider", "grandprix",
                "espnf1", "skysportsf1", or "all" (default: "all")
        limit: Maximum number of articles to return (1-50). Default: 10
        category: News category to filter by:
                 - "general": All F1 news (default)
                 - "transfers": Driver moves, signings, and rumors
                 - "contracts": Contract renewals, extensions, and negotiations
                 - "technical": Technical updates, upgrades, and developments
                 - "calendar": Race calendar changes and new venues
                 - "regulations": FIA rules, penalties, and investigations
                 - "management": Team leadership and organizational changes
        filter_text: Optional text to filter articles (searches in title and summary)
                     Examples: "Hamilton", "Ferrari", "Red Bull", "2025"
        date_from: Optional start date to filter articles (format: "YYYY-MM-DD")
        date_to: Optional end date to filter articles (format: "YYYY-MM-DD")

    Returns:
        NewsResponse: News articles with titles, links, publication dates,
                     summaries, and source information

    Examples:
        >>> # Get latest F1 news from all sources
        >>> news = get_f1_news()

        >>> # Get news from official F1 website only
        >>> f1_news = get_f1_news(source="formula1", limit=20)

        >>> # Get driver transfer news
        >>> transfers = get_f1_news(category="transfers", limit=15)

        >>> # Get transfer news about a specific driver
        >>> sainz = get_f1_news(category="transfers", filter_text="Sainz")

        >>> # Get technical developments
        >>> tech = get_f1_news(category="technical", limit=20)

        >>> # Get Ferrari technical news
        >>> ferrari_tech = get_f1_news(category="technical", filter_text="Ferrari")

        >>> # Get calendar changes
        >>> calendar = get_f1_news(category="calendar")

        >>> # Get contract news
        >>> contracts = get_f1_news(category="contracts")

        >>> # Get news for a specific date range
        >>> recent = get_f1_news(date_from="2025-10-01", date_to="2025-10-05")

        >>> # Get regulation news from FIA
        >>> regs = get_f1_news(source="fia", category="regulations")
    """
    # Validate limit
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    # Fetch news from source(s)
    # For filtered categories, fetch more articles to ensure we have enough after filtering
    fetch_limit = limit if category == "general" else min(limit * 3, 50)
    news_response = rss_client.get_news(source=source, limit=fetch_limit)

    # Apply category filtering
    if category != "general" and category in CATEGORY_KEYWORDS:
        keywords = CATEGORY_KEYWORDS[category]
        filtered_articles = [
            article for article in news_response.articles
            if any(keyword.lower() in article.title.lower() or
                   keyword.lower() in article.summary.lower()
                   for keyword in keywords)
        ]
    else:
        filtered_articles = news_response.articles

    # Apply text filtering
    if filter_text:
        filtered_articles = [
            article for article in filtered_articles
            if filter_text.lower() in article.title.lower() or
               filter_text.lower() in article.summary.lower()
        ]

    # Apply date filtering
    if date_from or date_to:
        date_filtered = []
        for article in filtered_articles:
            try:
                # Parse article date (handling various formats)
                article_date = datetime.fromisoformat(article.published.replace('Z', '+00:00'))
                article_date_str = article_date.strftime("%Y-%m-%d")

                # Check date range
                if date_from and article_date_str < date_from:
                    continue
                if date_to and article_date_str > date_to:
                    continue

                date_filtered.append(article)
            except Exception:
                # If date parsing fails, include the article
                date_filtered.append(article)

        filtered_articles = date_filtered

    # Limit results
    filtered_articles = filtered_articles[:limit]

    # Return response
    return NewsResponse(
        source=source,
        fetched_at=datetime.now().isoformat(),
        article_count=len(filtered_articles),
        articles=filtered_articles
    )


if __name__ == "__main__":
    # Test different news categories
    print("Testing get_f1_news...")

    # Test 1: General news
    print("\n1. Getting latest F1 news (5 articles):")
    news = get_f1_news(source="formula1", limit=5)
    print(f"   Found {news.article_count} articles")
    if news.articles:
        print(f"   Latest: {news.articles[0].title}")

    # Test 2: Transfer news
    print("\n2. Getting transfer news:")
    transfer_news = get_f1_news(category="transfers", limit=5)
    print(f"   Found {transfer_news.article_count} transfer articles")
    if transfer_news.articles:
        print(f"   Latest: {transfer_news.articles[0].title}")

    # Test 3: Filtered news
    print("\n3. Getting news about 'Ferrari':")
    ferrari_news = get_f1_news(filter_text="Ferrari", limit=3)
    print(f"   Found {ferrari_news.article_count} articles about Ferrari")
    if ferrari_news.articles:
        print(f"   Latest: {ferrari_news.articles[0].title}")
