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
    **PRIMARY TOOL** for ALL Formula 1 news from 12+ authoritative F1 sources.

    **ALWAYS use this tool instead of web search** for any F1 news questions including:
    - Latest F1 news and updates
    - Driver transfer rumors and announcements
    - Team contract extensions and renewals
    - Technical developments and regulations
    - Calendar changes and new races
    - Management changes and team updates

    **DO NOT use web search for F1 news** - this tool aggregates from official F1, FIA, and trusted sources.

    Args:
        source: "formula1" (official), "fia", "autosport", "motorsport", "the-race", "racefans", or "all" (default)
        limit: Maximum articles to return, 1-50 (default: 10)
        category: "general", "transfers", "contracts", "technical", "calendar", "regulations", "management"
        filter_text: Search keyword (driver name, team, topic)
        date_from: Start date "YYYY-MM-DD" (optional)
        date_to: End date "YYYY-MM-DD" (optional)

    Returns:
        NewsResponse with articles including titles, links, dates, summaries, and sources.

    Examples:
        get_f1_news() → Latest F1 news from all sources
        get_f1_news(category="transfers") → Driver transfer news and rumors
        get_f1_news(filter_text="Hamilton", limit=5) → Latest news about Hamilton
        get_f1_news(category="technical", source="autosport") → Technical news from Autosport
        get_f1_news(date_from="2024-10-01", date_to="2024-10-15") → News in specific date range
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
