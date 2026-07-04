"""Tests for src/pitstop/clients/rss_client.py — written first (TDD)."""

import logging
from unittest.mock import MagicMock, patch

import httpx
import pytest

from pitstop.clients import rss_client as rss_mod
from pitstop.clients.rss_client import RSSClient
from pitstop.exceptions import DataSourceError
from pitstop.tools.news.models import NewsArticle, NewsResponse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_http_response(status_code=200, content=b"<rss></rss>"):
    """Fake httpx.Response standing in for the module-level cached client's .get()."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content
    if status_code >= 400:
        request = MagicMock()

        def _raise():
            raise httpx.HTTPStatusError(f"{status_code} error", request=request, response=resp)

        resp.raise_for_status.side_effect = _raise
    else:
        resp.raise_for_status.return_value = None
    return resp


def _patch_client_get(**kwargs):
    """Patch the shared rss_client._client.get so tests never hit the network."""
    return patch.object(rss_mod._client, "get", **kwargs)


def _make_entry(
    title="Test Article",
    link="https://example.com/1",
    published="2026-01-01T00:00:00",
    summary="Test summary",
    author="Test Author",
):
    entry = MagicMock()
    data = {
        "title": title,
        "link": link,
        "published": published,
        "summary": summary,
        "author": author,
    }
    entry.get = lambda key, default=None: data.get(key, default)
    return entry


def _make_feed(entries):
    feed = MagicMock()
    feed.entries = entries
    return feed


def _make_article(source="formula1"):
    return NewsArticle(
        title="Test Article",
        link="https://example.com/1",
        published="2026-01-01T00:00:00",
        summary="Test summary",
        source=source,
        author=None,
    )


def _make_response(source="formula1"):
    return NewsResponse(
        source=source,
        fetched_at="2026-01-01T00:00:00",
        article_count=1,
        articles=[_make_article(source)],
    )


# ---------------------------------------------------------------------------
# Import check
# ---------------------------------------------------------------------------


def test_import_works():
    """Importing RSSClient raises no ImportError."""
    from pitstop.clients.rss_client import RSSClient as _RSSClient  # noqa: F401

    assert _RSSClient is not None


# ---------------------------------------------------------------------------
# Per-feed failure → warning logged
# ---------------------------------------------------------------------------


def test_empty_feed_logs_warning(caplog):
    """When feedparser returns no entries, a WARNING is logged for each failed feed."""
    client = RSSClient()
    empty_feed = _make_feed([])

    with caplog.at_level(logging.WARNING, logger="pitstop.rss"):
        with patch("feedparser.parse", return_value=empty_feed):
            with _patch_client_get(return_value=_make_http_response()):
                with pytest.raises(DataSourceError):
                    client._fetch_all_sources(limit=5)

    warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warning_records) > 0


def test_empty_feed_warning_contains_source_info(caplog):
    """Warning log messages should mention the feed that failed."""
    client = RSSClient()
    empty_feed = _make_feed([])

    with caplog.at_level(logging.WARNING, logger="pitstop.rss"):
        with patch("feedparser.parse", return_value=empty_feed):
            with _patch_client_get(return_value=_make_http_response()):
                with pytest.raises(DataSourceError):
                    client._fetch_all_sources(limit=5)

    warning_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warning_messages) > 0
    # At least one warning should reference a feed URL or name
    combined = " ".join(warning_messages)
    assert "formula1" in combined or "http" in combined


# ---------------------------------------------------------------------------
# Aggregate mode collects from multiple feeds
# ---------------------------------------------------------------------------


def test_aggregate_collects_articles_from_two_feeds():
    """_fetch_all_sources collects articles from all feeds that succeed."""
    client = RSSClient()
    two_sources = list(client.RSS_FEEDS.keys())[:2]

    def mock_fetch_single(source, limit):
        if source in two_sources:
            return _make_response(source)
        raise RuntimeError(f"No articles from {source}")

    with patch.object(client, "_fetch_single_source", side_effect=mock_fetch_single):
        result = client._fetch_all_sources(limit=5)

    assert result.article_count == 2
    assert len(result.articles) == 2


def test_aggregate_tracks_failed_feeds():
    """_fetch_all_sources tracks which feeds failed."""
    client = RSSClient()
    good_sources = list(client.RSS_FEEDS.keys())[:2]
    all_sources = list(client.RSS_FEEDS.keys())
    expected_failures = [s for s in all_sources if s not in good_sources]

    def mock_fetch_single(source, limit):
        if source in good_sources:
            return _make_response(source)
        raise RuntimeError(f"No articles from {source}")

    with patch.object(client, "_fetch_single_source", side_effect=mock_fetch_single):
        result = client._fetch_all_sources(limit=5)

    assert set(result.failed_feeds) == set(expected_failures)


def test_aggregate_raises_data_source_error_when_all_fail():
    """_fetch_all_sources raises DataSourceError when every feed fails."""
    client = RSSClient()

    def always_fail(source, limit):
        raise RuntimeError("network error")

    with patch.object(client, "_fetch_single_source", side_effect=always_fail):
        with pytest.raises(DataSourceError) as exc_info:
            client._fetch_all_sources(limit=5)

    assert exc_info.value.source == "rss"


def test_aggregate_one_feed_500_others_still_aggregate():
    """A single feed returning HTTP 500 is recorded as failed; other feeds still aggregate."""
    client = RSSClient()
    entry = _make_entry()
    good_feed = _make_feed([entry])
    bad_source = next(iter(client.RSS_FEEDS))
    bad_url = client.RSS_FEEDS[bad_source]

    def fake_get(url, *args, **kwargs):
        if url == bad_url:
            return _make_http_response(status_code=500)
        return _make_http_response()

    with patch("feedparser.parse", return_value=good_feed):
        with _patch_client_get(side_effect=fake_get):
            result = client._fetch_all_sources(limit=5)

    assert bad_source in result.failed_feeds
    assert result.article_count > 0
    assert all(a.source != bad_source for a in result.articles)


# ---------------------------------------------------------------------------
# get_news — public API
# ---------------------------------------------------------------------------


def test_get_news_invalid_source_raises_value_error():
    """get_news raises ValueError for unknown source names."""
    client = RSSClient()
    with pytest.raises(ValueError, match="Invalid source"):
        client.get_news(source="not-a-real-source", limit=5)


def test_get_news_single_source_success():
    """get_news returns a NewsResponse for a valid single source."""
    client = RSSClient()
    entry = _make_entry()
    good_feed = _make_feed([entry])

    with patch("feedparser.parse", return_value=good_feed):
        with _patch_client_get(return_value=_make_http_response()):
            result = client.get_news(source="formula1", limit=5)

    assert isinstance(result, NewsResponse)
    assert result.source == "formula1"
    assert result.article_count == 1


def test_get_news_single_source_empty_raises_data_source_error():
    """get_news raises DataSourceError (not bare RuntimeError) when a single source has no entries."""
    client = RSSClient()
    empty_feed = _make_feed([])

    with patch("feedparser.parse", return_value=empty_feed):
        with _patch_client_get(return_value=_make_http_response()):
            with pytest.raises(DataSourceError):
                client.get_news(source="formula1", limit=5)


def test_get_news_all_respects_limit():
    """get_news with source='all' respects the articles-per-source limit."""
    client = RSSClient()
    entries = [_make_entry(title=f"Article {i}") for i in range(10)]
    good_feed = _make_feed(entries)

    with patch("feedparser.parse", return_value=good_feed):
        with _patch_client_get(return_value=_make_http_response()):
            result = client.get_news(source="all", limit=3)

    # Each source contributes up to 3 articles; at most 3 * num_feeds total
    assert result.article_count <= 3 * len(client.RSS_FEEDS)


# ---------------------------------------------------------------------------
# RSS_FEEDS expansion — new feeds
# ---------------------------------------------------------------------------


def test_rss_feeds_contains_five_new_feeds():
    """RSS_FEEDS dict contains all 5 new feeds added in expansion."""
    client = RSSClient()
    new_feeds = ["formula1", "reddit_f1", "the_race", "crash_net", "racefans"]
    for feed_key in new_feeds:
        assert feed_key in client.RSS_FEEDS, f"Feed '{feed_key}' not found in RSS_FEEDS"


def test_rss_feeds_new_feeds_have_correct_urls():
    """New feeds have the correct RSS URLs."""
    client = RSSClient()
    expected_urls = {
        "formula1": "https://www.formula1.com/en/latest/all.rss",
        "reddit_f1": "https://www.reddit.com/r/formula1/.rss",
        "the_race": "https://the-race.com/feed/",
        "crash_net": "https://www.crash.net/rss/f1",
        "racefans": "https://www.racefans.net/feed/",
    }
    for feed_key, expected_url in expected_urls.items():
        assert client.RSS_FEEDS[feed_key] == expected_url, (
            f"Feed '{feed_key}' has URL '{client.RSS_FEEDS[feed_key]}' "
            f"but expected '{expected_url}'"
        )
