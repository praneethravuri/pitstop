import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import TYPE_CHECKING

import feedparser

from pitstop.clients.http import make_client
from pitstop.config import HTTP_CACHE_TTL
from pitstop.exceptions import DataSourceError
from pitstop.utils.text_cleaner import clean_html

if TYPE_CHECKING:
    from pitstop.tools.news.models import NewsResponse

logger = logging.getLogger("pitstop.rss")

# Redirects are common among these feeds; caching makes repeated news calls cheap.
_client = make_client(
    timeout=10.0,
    follow_redirects=True,
    cache_ttl=HTTP_CACHE_TTL,
)


class RSSClient:
    """
    RSS client for accessing Formula 1 news feeds.

    Aggregates F1 news from 20 trusted sources including:
    - Official Formula 1 website & FIA
    - Major outlets: Autosport, Motorsport.com, The Race, RaceFans
    - Specialist sources: Pitpass, Joe Saward, Racecar Engineering
    - Regional sources: F1i, F1 Insider
    - Community sources: FormulaNerds, GPFans, Reddit F1

    Every URL below was verified live (HTTP 200 + parseable entries).
    """

    RSS_FEEDS = {
        # Official sources
        "formula1": "https://www.formula1.com/en/latest/all.xml",
        "fia": "https://www.fia.com/rss/press-release",
        # Major F1 news outlets
        "autosport": "https://www.autosport.com/rss/feed/f1",
        "motorsport": "https://www.motorsport.com/rss/f1/news/",
        "the_race": "https://the-race.com/feed/",
        "racefans": "https://www.racefans.net/feed/",
        "crash_net": "https://www.crash.net/rss/f1",
        "grandprix": "https://www.grandprix.com/rss.xml",
        "espnf1": "https://www.espn.com/espn/rss/rpm/news",
        "skysportsf1": "https://www.skysports.com/rss/12040",
        "reddit_f1": "https://www.reddit.com/r/formula1/.rss",
        # Specialist & Technical sources
        "pitpass": "https://www.pitpass.com/fes_php/fes_usr_sit_newsfeed.php",
        "joe-saward": "https://joesaward.wordpress.com/feed/",
        "racecar-engineering": "https://www.racecar-engineering.com/feed/",
        # Regional & International sources
        "f1i": "https://f1i.com/feed",
        "f1-insider-de": "https://www.f1-insider.com/feed/",
        # Community & Fan sources
        "formulanerds": "https://formulanerds.com/feed/",
        "f1destinations": "https://f1destinations.com/feed/",
        "gpfans": "https://www.gpfans.com/en/rss.xml",
        # Additional coverage
        "motorsportweek": "https://www.motorsportweek.com/feed/",
    }

    def get_news(self, source: str, limit: int) -> "NewsResponse":
        """
        Fetch F1 news from RSS feeds.

        Args:
            source: News source identifier or "all"
            limit: Maximum articles to return

        Returns:
            NewsResponse: Structured news data

        Raises:
            ValueError: If source is invalid
            DataSourceError: If feed fetch fails
        """
        if source != "all" and source not in self.RSS_FEEDS:
            valid_sources = ", ".join(self.RSS_FEEDS.keys())
            raise ValueError(f"Invalid source '{source}'. Must be one of: {valid_sources}, all")

        try:
            if source == "all":
                return self._fetch_all_sources(limit)
            else:
                return self._fetch_single_source(source, limit)
        except Exception as e:
            raise DataSourceError("rss", f"fetch:{source}", str(e))

    def _fetch_single_source(self, source: str, limit: int):
        """Fetch from a single RSS source."""
        from pitstop.tools.news.models import NewsArticle, NewsResponse

        feed_url = self.RSS_FEEDS[source]
        resp = _client.get(feed_url)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)

        if not feed.entries:
            raise RuntimeError(f"No articles found from {source}")

        articles = []
        for entry in feed.entries[:limit]:
            articles.append(
                NewsArticle(
                    title=entry.get("title", "No title"),
                    link=entry.get("link", ""),
                    published=entry.get("published", entry.get("updated", "Unknown date")),
                    summary=clean_html(
                        entry.get("summary", entry.get("description", "No summary available"))
                    ),
                    source=source,
                    author=entry.get("author", None),
                )
            )

        return NewsResponse(
            source=source,
            fetched_at=datetime.now().isoformat(),
            article_count=len(articles),
            articles=articles,
        )

    def _fetch_all_sources(self, limit: int):
        """Fetch from all RSS sources and aggregate."""
        from pitstop.tools.news.models import NewsArticle, NewsResponse

        # Ceiling division so each source contributes proportionally; ensures diversity
        per_source = max(1, -(-limit // len(self.RSS_FEEDS)))  # ceil(limit/n)

        def _try_fetch(source: str) -> "NewsResponse | None":
            try:
                return self._fetch_single_source(source, per_source)
            except Exception as e:
                logger.warning("RSS feed failed: %s (%s) — %s", source, self.RSS_FEEDS[source], e)
                return None

        # executor.map preserves RSS_FEEDS insertion order in its results
        with ThreadPoolExecutor(max_workers=8) as executor:
            outcomes = list(executor.map(_try_fetch, self.RSS_FEEDS))

        failed_feeds: list[str] = []
        all_articles: list[NewsArticle] = []
        for source, resp in zip(self.RSS_FEEDS, outcomes):
            if resp is None:
                failed_feeds.append(source)
            else:
                all_articles.extend(resp.articles)

        if not all_articles:
            reason = f"all {len(failed_feeds)} feeds failed"
            raise DataSourceError("rss", "fetch", reason)

        all_articles = all_articles[:limit]

        return NewsResponse(
            source="all",
            fetched_at=datetime.now().isoformat(),
            article_count=len(all_articles),
            articles=all_articles,
            failed_feeds=failed_feeds,
        )
