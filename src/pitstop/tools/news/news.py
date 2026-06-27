import logging
from datetime import datetime, timedelta

from fastmcp.exceptions import ToolError

from pitstop.clients.rss_client import RSSClient
from pitstop.exceptions import DataSourceError
from pitstop.tools.news.models import NewsArticle, NewsResponse
from pitstop.utils import filter_by_name, paginate, to_tool_error

logger = logging.getLogger("pitstop.news")

# Initialize RSS client
rss_client = RSSClient()


def get_f1_news(
    source: str = "all",
    limit: int | None = None,
    keywords: str | None = None,
    driver: str | None = None,
    team: str | None = None,
    circuit: str | None = None,
    year: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> NewsResponse:
    """
    **PRIMARY TOOL** for RECENT Formula 1 news from 25+ authoritative F1 sources via RSS feeds.

    ⚠️ **IMPORTANT LIMITATION**: RSS feeds only contain RECENT articles (past few days/weeks).
    This tool CANNOT retrieve historical news from months or years ago (e.g., 2013, 2020, etc.).

    **For historical F1 news (older than ~2 months), use web search instead.**

    **USE THIS TOOL FOR:**
    - Latest breaking F1 news and updates
    - Current race weekend coverage
    - Recent driver/team announcements (within past few weeks)
    - Current season news filtering by driver, team, circuit
    - Technical developments and regulations from recent weeks

    **DO NOT use this tool for:**
    - Historical news from past years (e.g., "2013 Indian GP", "2020 season")
    - News older than ~2 months
    - Historical race coverage or archived articles

    **Available Sources (25+ RSS Feeds):**

    Official Sources:
    - "formula1" - Official Formula 1 website
    - "fia" - FIA press releases

    Major Outlets:
    - "autosport" - Autosport F1
    - "motorsport" - Motorsport.com F1
    - "the-race" - The Race
    - "racefans" - RaceFans.net
    - "planetf1" - PlanetF1
    - "crash" - Crash.net F1
    - "grandprix" - GrandPrix.com
    - "espnf1" - ESPN F1
    - "skysportsf1" - Sky Sports F1

    Specialist & Technical:
    - "f1technical" - F1Technical.net
    - "pitpass" - Pitpass
    - "joe-saward" - Joe Saward's F1 Blog
    - "racecar-engineering" - Racecar Engineering

    Regional & International:
    - "gpblog" - GPBlog (Dutch/English)
    - "f1i" - F1i.com
    - "f1-insider-de" - F1 Insider (German)
    - "formel1-de" - Formel1.de (German)

    Community & Fan Sources:
    - "wtf1" - WTF1
    - "racingnews365" - RacingNews365
    - "formulanerds" - Formula Nerds
    - "f1destinations" - F1 Destinations
    - "gpfans" - GPFans
    - "motorsportweek" - Motorsport Week
    - "racedepartment" - Race Department

    Args:
        source: Specific source or "all" (default) - see full list above
        limit: Legacy param — if set, overrides page_size and forces page=1
        keywords: General search keywords (searches in title and summary)
        driver: Filter by driver name (e.g., "Verstappen", "Hamilton", "Leclerc")
        team: Filter by team/constructor name (e.g., "Red Bull", "Ferrari", "Mercedes")
        circuit: Filter by circuit/track name (e.g., "Monaco", "Silverstone", "Spa")
        year: Filter by year (e.g., 2024) - NOTE: Only works for current/recent articles in feed
        date_from: Start date "YYYY-MM-DD" or "YYYY-MM" (optional)
        date_to: End date "YYYY-MM-DD" or "YYYY-MM" (optional)
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 10)

    Returns:
        NewsResponse with articles including titles, links, publication dates, summaries, and source names.

    Examples:
        get_f1_news() → Latest F1 news from all 25+ sources
        get_f1_news(driver="Verstappen") → Recent news about Verstappen
        get_f1_news(team="Ferrari") → Recent Ferrari news
        get_f1_news(circuit="Monaco") → Recent Monaco-related news
        get_f1_news(keywords="crash OR incident") → Recent crash/incident news
        get_f1_news(source="autosport", keywords="technical") → Technical news from Autosport
    """
    try:
        # ponytail: limit is legacy compat; new callers use page/page_size
        if limit is not None:
            page_size = limit
            page = 1

        has_filters = any([keywords, driver, team, circuit, year, date_from, date_to])
        fetch_limit = min(page_size * 3, 100) if has_filters else page_size * page

        news_response = rss_client.get_news(source=source, limit=fetch_limit)
        filtered_articles = news_response.articles

        # Apply driver/team/circuit filters via filter_by_name (works on dicts)
        articles_dicts = [a.model_dump() for a in filtered_articles]
        if driver:
            articles_dicts = filter_by_name(articles_dicts, driver, ["title", "summary"])
        if team:
            articles_dicts = filter_by_name(articles_dicts, team, ["title", "summary"])
        if circuit:
            articles_dicts = filter_by_name(articles_dicts, circuit, ["title", "summary"])
        filtered_articles = [NewsArticle(**d) for d in articles_dicts]

        # Apply keyword filtering (supports OR operator — filter_by_name doesn't)
        if keywords:
            keywords_lower = keywords.lower()
            if " or " in keywords_lower:
                keyword_list = [kw.strip() for kw in keywords_lower.split(" or ")]
                filtered_articles = [
                    article
                    for article in filtered_articles
                    if any(
                        kw in article.title.lower() or kw in article.summary.lower()
                        for kw in keyword_list
                    )
                ]
            else:
                filtered_articles = [
                    article
                    for article in filtered_articles
                    if keywords_lower in article.title.lower()
                    or keywords_lower in article.summary.lower()
                ]

        # Apply date filtering
        if year:
            if not date_from:
                date_from = f"{year}-01-01"
            if not date_to:
                date_to = f"{year}-12-31"

        if date_from or date_to:
            date_filtered = []
            for article in filtered_articles:
                try:
                    article_date = datetime.fromisoformat(article.published.replace("Z", "+00:00"))
                    article_date_str = article_date.strftime("%Y-%m-%d")

                    if date_from:
                        compare_from = date_from if len(date_from) > 7 else f"{date_from}-01"
                        if article_date_str < compare_from:
                            continue

                    if date_to:
                        if len(date_to) == 7:
                            year_val = int(date_to.split("-")[0])
                            month_val = int(date_to.split("-")[1])
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
                except Exception as exc:
                    logger.warning(
                        "Skipping article with unparseable date %r: %s",
                        article.published,
                        exc,
                    )

            filtered_articles = date_filtered

        paged, meta = paginate(filtered_articles, page, page_size)

        return NewsResponse(
            source=source,
            fetched_at=datetime.now().isoformat(),
            article_count=len(paged),
            articles=paged,
            failed_feeds=news_response.failed_feeds,
            pagination=meta,
        )

    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("get_f1_news", exc.source, exc)
    except Exception as exc:
        raise to_tool_error("get_f1_news", "rss", exc)
