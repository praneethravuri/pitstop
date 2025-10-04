from clients.rss_client import RSSClient
from models import RaceNewsResponse, RaceNewsArticle
from datetime import datetime

# Initialize RSS client
rss_client = RSSClient()

# Keywords for different race news categories
PRACTICE_KEYWORDS = [
    "practice", "fp1", "fp2", "fp3", "free practice", "practice session",
    "practice 1", "practice 2", "practice 3", "friday practice"
]

QUALIFYING_KEYWORDS = [
    "qualifying", "pole", "pole position", "q1", "q2", "q3", "quali",
    "saturday qualifying", "grid position", "front row"
]

RACE_KEYWORDS = [
    "race", "grand prix", "gp", "wins", "victory", "podium", "race day",
    "sunday race", "race report", "race recap", "race result"
]

HIGHLIGHTS_KEYWORDS = [
    "radio", "team radio", "highlights", "best moments", "key moments",
    "controversy", "incident", "crash", "penalty", "driver quote",
    "post-race", "interview", "reaction"
]


def _filter_race_news(
    race_name: str | None,
    year: int | None,
    keywords: list[str],
    category: str,
    limit: int
) -> RaceNewsResponse:
    """
    Filter news articles by race name, year, and keywords.

    Args:
        race_name: Race name filter (optional)
        year: Year filter (optional)
        keywords: List of keywords to search for
        category: News category
        limit: Max articles to return

    Returns:
        RaceNewsResponse: Filtered race news articles
    """
    # Fetch news from all sources
    news_response = rss_client.get_news(source="all", limit=max(limit * 3, 30))

    filtered_articles = []

    for article in news_response.articles:
        # Combine title and summary for searching
        content = f"{article.title} {article.summary}".lower()

        # Check keywords
        keyword_match = any(kw.lower() in content for kw in keywords)
        if not keyword_match:
            continue

        # Check race name if specified
        if race_name and race_name.lower() not in content:
            continue

        # Check year if specified
        if year and str(year) not in content:
            continue

        # Create race news article
        filtered_articles.append(
            RaceNewsArticle(
                title=article.title,
                link=article.link,
                published=article.published,
                summary=article.summary,
                source=article.source,
                author=article.author,
                category=category,
                race_name=race_name,
            )
        )

    # Limit results
    filtered_articles = filtered_articles[:limit]

    return RaceNewsResponse(
        race_name=race_name,
        year=year,
        category=category,
        fetched_at=datetime.now().isoformat(),
        article_count=len(filtered_articles),
        articles=filtered_articles,
    )


def get_race_weekend_news(race_name: str, year: int | None = None, limit: int = 15) -> RaceNewsResponse:
    """
    Get all news articles for a specific race weekend.

    Returns news covering all aspects of a race weekend including practice,
    qualifying, sprint (if applicable), and race. Filter by race name to get
    comprehensive coverage of a specific Grand Prix.

    Args:
        race_name: Race name to filter by (e.g., 'Bahrain', 'Monaco', 'Silverstone')
        year: Optional year filter (e.g., 2024, 2023)
        limit: Maximum number of articles to return (1-50). Default: 15

    Returns:
        RaceNewsResponse: News articles related to the race weekend, including
        practice reports, qualifying analysis, race coverage, and post-race reactions.
    """
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    # Combine all race weekend keywords
    all_keywords = PRACTICE_KEYWORDS + QUALIFYING_KEYWORDS + RACE_KEYWORDS + HIGHLIGHTS_KEYWORDS

    return _filter_race_news(race_name, year, all_keywords, "race_weekend", limit)


def get_practice_reports(race_name: str | None = None, year: int | None = None, limit: int = 10) -> RaceNewsResponse:
    """
    Get practice session reports and analysis.

    Returns news articles about practice sessions (FP1, FP2, FP3) including
    session reports, pace analysis, team performance, and technical issues.

    Args:
        race_name: Optional race name filter (e.g., 'Bahrain', 'Monaco')
        year: Optional year filter
        limit: Maximum number of articles to return (1-50). Default: 10

    Returns:
        RaceNewsResponse: Practice session news and analysis, including lap times,
        team performance reports, and technical observations from Friday/Saturday practice.
    """
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return _filter_race_news(race_name, year, PRACTICE_KEYWORDS, "practice", limit)


def get_qualifying_reports(race_name: str | None = None, year: int | None = None, limit: int = 10) -> RaceNewsResponse:
    """
    Get qualifying reports and analysis.

    Returns news about qualifying sessions including pole position battles,
    Q1/Q2/Q3 analysis, grid penalties, and qualifying controversies.

    Args:
        race_name: Optional race name filter
        year: Optional year filter
        limit: Maximum number of articles to return (1-50). Default: 10

    Returns:
        RaceNewsResponse: Qualifying news including pole position stories, session
        analysis, driver quotes, and grid position updates.
    """
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return _filter_race_news(race_name, year, QUALIFYING_KEYWORDS, "qualifying", limit)


def get_race_reports(race_name: str | None = None, year: int | None = None, limit: int = 15) -> RaceNewsResponse:
    """
    Get race reports, results, and post-race analysis.

    Returns news about race day including race reports, results, podium finishes,
    race incidents, strategy analysis, and post-race reactions.

    Args:
        race_name: Optional race name filter
        year: Optional year filter
        limit: Maximum number of articles to return (1-50). Default: 15

    Returns:
        RaceNewsResponse: Race day news including race reports, winner stories,
        podium results, race analysis, and championship implications.
    """
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return _filter_race_news(race_name, year, RACE_KEYWORDS, "race", limit)


def get_race_highlights(race_name: str | None = None, year: int | None = None, limit: int = 10) -> RaceNewsResponse:
    """
    Get race weekend highlights including radio messages, key moments, and reactions.

    Returns news about memorable moments, team radio highlights, driver quotes,
    controversies, incidents, and post-race interviews from race weekends.

    Args:
        race_name: Optional race name filter
        year: Optional year filter
        limit: Maximum number of articles to return (1-50). Default: 10

    Returns:
        RaceNewsResponse: Highlight news including team radio messages, driver reactions,
        key incidents, controversies, penalties, and memorable moments from the weekend.
    """
    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    return _filter_race_news(race_name, year, HIGHLIGHTS_KEYWORDS, "highlights", limit)
