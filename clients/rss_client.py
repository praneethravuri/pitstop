import feedparser
from datetime import datetime
from models import NewsResponse, NewsArticle
from utils import clean_html


class RSSClient:
    """
    RSS client for accessing Formula 1 news feeds.

    Aggregates F1 news from 25+ trusted sources including:
    - Official Formula 1 website & FIA
    - Major outlets: Autosport, Motorsport.com, The Race, RaceFans
    - Specialist sources: F1Technical, Pitpass, Joe Saward
    - Regional sources: GPBlog, Formel1.de, F1 Insider
    - Community sources: WTF1, FormulaNerds, RacingNews365
    """

    RSS_FEEDS = {
        # Official sources
        "formula1": "https://www.formula1.com/content/fom-website/en/latest/all.xml",
        "fia": "https://www.fia.com/rss/press-release",

        # Major F1 news outlets
        "autosport": "https://www.autosport.com/rss/feed/f1",
        "motorsport": "https://www.motorsport.com/rss/f1/news/",
        "the-race": "https://the-race.com/formula-1/feed/",
        "racefans": "https://www.racefans.net/feed/",
        "planetf1": "https://www.planetf1.com/feed/",
        "crash": "https://www.crash.net/rss/f1/news/1",
        "grandprix": "https://www.grandprix.com/feed/",
        "espnf1": "https://www.espn.com/espn/rss/rpm/news",
        "skysportsf1": "https://www.skysports.com/rss/12040",

        # Specialist & Technical sources
        "f1technical": "https://www.f1technical.net/rss/news.xml",
        "pitpass": "https://www.pitpass.com/rss",
        "joe-saward": "https://joesaward.wordpress.com/feed/",
        "racecar-engineering": "https://www.racecar-engineering.com/feed/",

        # Regional & International sources
        "gpblog": "https://www.gpblog.com/en/rss.xml",
        "f1i": "https://f1i.com/feed",
        "f1-insider-de": "https://www.f1-insider.com/feed/",
        "formel1-de": "https://www.formel1.de/rss.xml",

        # Community & Fan sources
        "wtf1": "https://wtf1.com/feed/",
        "racingnews365": "https://racingnews365.com/rss",
        "formulanerds": "https://formulanerds.com/feed/",
        "f1destinations": "https://f1destinations.com/feed/",
        "gpfans": "https://www.gpfans.com/en/rss.xml",

        # Additional coverage
        "motorsportweek": "https://www.motorsportweek.com/feed/",
        "racedepartment": "https://www.racedepartment.com/forums/f1-2021-the-game.214/index.rss",
    }

    def __init__(self):
        """Initialize the RSS client."""
        pass

    def get_news(self, source: str, limit: int) -> NewsResponse:
        """
        Fetch F1 news from RSS feeds.

        Args:
            source: News source identifier or "all"
            limit: Maximum articles to return

        Returns:
            NewsResponse: Structured news data

        Raises:
            ValueError: If source is invalid
            RuntimeError: If feed fetch fails
        """
        # Validate source
        if source != "all" and source not in self.RSS_FEEDS:
            valid_sources = ", ".join(self.RSS_FEEDS.keys())
            raise ValueError(
                f"Invalid source '{source}'. Must be one of: {valid_sources}, all"
            )

        try:
            if source == "all":
                return self._fetch_all_sources(limit)
            else:
                return self._fetch_single_source(source, limit)
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to fetch news from {source}: {str(e)}")

    def _fetch_single_source(self, source: str, limit: int) -> NewsResponse:
        """Fetch from a single RSS source."""
        feed_url = self.RSS_FEEDS[source]
        feed = feedparser.parse(feed_url)

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

    def _fetch_all_sources(self, limit: int) -> NewsResponse:
        """Fetch from all RSS sources and aggregate."""
        all_articles = []

        for source in self.RSS_FEEDS.keys():
            try:
                result = self._fetch_single_source(source, limit)
                all_articles.extend(result.articles)
            except Exception:
                # Skip failed sources when aggregating
                continue

        if not all_articles:
            raise RuntimeError("Failed to fetch articles from all sources")

        # Sort by source and limit total
        all_articles = all_articles[: limit * len(self.RSS_FEEDS)]

        return NewsResponse(
            source="all",
            fetched_at=datetime.now().isoformat(),
            article_count=len(all_articles),
            articles=all_articles,
        )
