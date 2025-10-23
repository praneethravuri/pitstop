from clients.rss_client import RSSClient
from models import NewsResponse
from datetime import datetime, timedelta
from typing import Optional

# Initialize RSS client
rss_client = RSSClient()


def get_f1_news(
    source: str = "all",
    limit: int = 10,
    keywords: Optional[str] = None,
    driver: Optional[str] = None,
    team: Optional[str] = None,
    circuit: Optional[str] = None,
    year: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> NewsResponse:
    """
    **PRIMARY TOOL** for ALL Formula 1 news from 25+ authoritative F1 sources.

    **ALWAYS use this tool instead of web search** for any F1 news questions including:
    - Latest F1 news and updates from major outlets and niche sources
    - Driver-specific news (transfers, performance, incidents)
    - Team-specific news (technical updates, management changes)
    - Circuit/track-specific news (race weekends, incidents)
    - Historical news by year or date range
    - Technical developments, regulations, calendar changes

    **DO NOT use web search for F1 news** - this tool aggregates from official F1, FIA, and 25+ trusted sources.

    Args:
        source: Specific source or "all" (default). Available sources include:
            - Official: "formula1", "fia"
            - Major: "autosport", "motorsport", "the-race", "racefans", "planetf1"
            - Specialist: "f1technical", "pitpass", "joe-saward", "racecar-engineering"
            - Regional: "gpblog", "f1i", "f1-insider-de", "formel1-de"
            - Community: "wtf1", "racingnews365", "formulanerds", "gpfans"
            - And more... (use "all" to search across all 25+ sources)
        limit: Maximum articles to return, 1-100 (default: 10)
        keywords: General search keywords (searches in title and summary)
        driver: Filter by driver name (e.g., "Verstappen", "Hamilton", "Leclerc")
        team: Filter by team/constructor name (e.g., "Red Bull", "Ferrari", "Mercedes")
        circuit: Filter by circuit/track name (e.g., "Monaco", "Silverstone", "Spa")
        year: Filter by year (e.g., 2024, 2023) - simpler than date range for historical queries
        date_from: Start date "YYYY-MM-DD" or "YYYY-MM" (optional, for precise date ranges)
        date_to: End date "YYYY-MM-DD" or "YYYY-MM" (optional, for precise date ranges)

    Returns:
        NewsResponse with articles including titles, links, dates, summaries, and sources.

    Examples:
        get_f1_news() → Latest F1 news from all 25+ sources
        get_f1_news(driver="Verstappen", limit=5) → Latest news about Verstappen
        get_f1_news(team="Ferrari", year=2024) → Ferrari news from 2024
        get_f1_news(circuit="Monaco", year=2024) → Monaco GP 2024 news
        get_f1_news(keywords="crash OR incident", year=2024) → Crash/incident news from 2024
        get_f1_news(driver="Hamilton", team="Ferrari") → News about Hamilton and Ferrari
        get_f1_news(source="autosport", keywords="technical") → Technical news from Autosport
        get_f1_news(date_from="2024-10", date_to="2024-10") → October 2024 news
        get_f1_news(circuit="Spa", keywords="weather") → Spa weather-related news
    """
    # Validate limit
    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    # Determine fetch limit: fetch more if filtering is applied
    has_filters = any([keywords, driver, team, circuit, year, date_from, date_to])
    fetch_limit = min(limit * 3, 100) if has_filters else limit

    # Fetch news from source(s)
    news_response = rss_client.get_news(source=source, limit=fetch_limit)
    filtered_articles = news_response.articles

    # Apply driver filtering
    if driver:
        driver_lower = driver.lower()
        filtered_articles = [
            article for article in filtered_articles
            if driver_lower in article.title.lower() or
               driver_lower in article.summary.lower()
        ]

    # Apply team filtering
    if team:
        team_lower = team.lower()
        filtered_articles = [
            article for article in filtered_articles
            if team_lower in article.title.lower() or
               team_lower in article.summary.lower()
        ]

    # Apply circuit filtering
    if circuit:
        circuit_lower = circuit.lower()
        # Also check for common variations (e.g., "Monaco" matches "Monaco GP", "Circuit de Monaco")
        filtered_articles = [
            article for article in filtered_articles
            if circuit_lower in article.title.lower() or
               circuit_lower in article.summary.lower()
        ]

    # Apply keyword filtering
    if keywords:
        keywords_lower = keywords.lower()
        # Support OR operator for multiple keywords
        if " or " in keywords_lower:
            keyword_list = [kw.strip() for kw in keywords_lower.split(" or ")]
            filtered_articles = [
                article for article in filtered_articles
                if any(kw in article.title.lower() or kw in article.summary.lower()
                       for kw in keyword_list)
            ]
        else:
            # Single keyword or phrase
            filtered_articles = [
                article for article in filtered_articles
                if keywords_lower in article.title.lower() or
                   keywords_lower in article.summary.lower()
            ]

    # Apply date filtering
    # Convert year to date_from/date_to if specified
    if year:
        if not date_from:
            date_from = f"{year}-01-01"
        if not date_to:
            date_to = f"{year}-12-31"

    if date_from or date_to:
        date_filtered = []
        for article in filtered_articles:
            try:
                # Parse article date (handling various formats)
                article_date = datetime.fromisoformat(article.published.replace('Z', '+00:00'))
                article_date_str = article_date.strftime("%Y-%m-%d")

                # Support month-only filtering (YYYY-MM format)
                if date_from:
                    compare_from = date_from if len(date_from) > 7 else f"{date_from}-01"
                    if article_date_str < compare_from:
                        continue

                if date_to:
                    # If month format, get last day of month
                    if len(date_to) == 7:  # YYYY-MM format
                        year_val = int(date_to.split('-')[0])
                        month_val = int(date_to.split('-')[1])
                        # Get last day of month
                        if month_val == 12:
                            compare_to = f"{year_val}-12-31"
                        else:
                            next_month = datetime(year_val, month_val + 1, 1)
                            last_day = (next_month - timedelta(days=1)).day
                            compare_to = f"{year_val}-{month_val:02d}-{last_day}"
                    else:
                        compare_to = date_to

                    if article_date_str > compare_to:
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
    # Test the new flexible filtering system
    print("Testing get_f1_news with new filtering system...")

    # Test 1: General news from all sources
    print("\n1. Getting latest F1 news from all 25+ sources (5 articles):")
    news = get_f1_news(limit=5)
    print(f"   Found {news.article_count} articles")
    if news.articles:
        print(f"   Latest: {news.articles[0].title}")
        print(f"   Source: {news.articles[0].source}")

    # Test 2: Driver-specific news
    print("\n2. Getting news about Verstappen:")
    verstappen_news = get_f1_news(driver="Verstappen", limit=3)
    print(f"   Found {verstappen_news.article_count} articles about Verstappen")
    if verstappen_news.articles:
        print(f"   Latest: {verstappen_news.articles[0].title}")

    # Test 3: Team-specific news
    print("\n3. Getting news about Ferrari:")
    ferrari_news = get_f1_news(team="Ferrari", limit=3)
    print(f"   Found {ferrari_news.article_count} articles about Ferrari")
    if ferrari_news.articles:
        print(f"   Latest: {ferrari_news.articles[0].title}")

    # Test 4: Circuit-specific news
    print("\n4. Getting news about Monaco:")
    monaco_news = get_f1_news(circuit="Monaco", limit=3)
    print(f"   Found {monaco_news.article_count} articles about Monaco")
    if monaco_news.articles:
        print(f"   Latest: {monaco_news.articles[0].title}")

    # Test 5: Year-based filtering
    print("\n5. Getting 2024 news:")
    year_news = get_f1_news(year=2024, limit=3)
    print(f"   Found {year_news.article_count} articles from 2024")
    if year_news.articles:
        print(f"   Latest: {year_news.articles[0].title}")

    # Test 6: Keyword filtering with OR operator
    print("\n6. Getting news about crashes or incidents:")
    keyword_news = get_f1_news(keywords="crash OR incident", limit=3)
    print(f"   Found {keyword_news.article_count} articles about crashes/incidents")
    if keyword_news.articles:
        print(f"   Latest: {keyword_news.articles[0].title}")

    # Test 7: Combined filtering (circuit + year)
    print("\n7. Getting Monaco 2024 news:")
    combined_news = get_f1_news(circuit="Monaco", year=2024, limit=3)
    print(f"   Found {combined_news.article_count} articles about Monaco 2024")
    if combined_news.articles:
        print(f"   Latest: {combined_news.articles[0].title}")
