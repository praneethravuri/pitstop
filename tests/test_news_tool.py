"""Tests for tools/media/news.py — TDD-first."""

import logging
from unittest.mock import patch

from pitstop.models.news_and_updates import NewsArticle, NewsResponse
from pitstop.tools.media.news import get_f1_news


def _article(title, summary="", published="2024-05-26T12:00:00+00:00", source="autosport"):
    return NewsArticle(
        title=title, link="https://example.com", published=published, summary=summary, source=source
    )


def _make_news_response(*articles):
    return NewsResponse(
        source="all",
        fetched_at="2024-05-26T12:00:00",
        article_count=len(articles),
        articles=list(articles),
        failed_feeds=[],
    )


@patch("pitstop.tools.media.news.rss_client")
def test_driver_filter(mock_rss):
    articles = [
        _article("Hamilton wins in Monaco", summary="Lewis Hamilton took victory"),
        _article("Verstappen extends lead", summary="Max Verstappen now leads"),
    ]
    mock_rss.get_news.return_value = _make_news_response(*articles)

    result = get_f1_news(driver="Hamilton")

    assert result.article_count == 1
    assert "Hamilton" in result.articles[0].title


@patch("pitstop.tools.media.news.rss_client")
def test_team_filter(mock_rss):
    articles = [
        _article("Red Bull strategy pays off", summary="Red Bull Racing claim 1-2"),
        _article("Ferrari struggles in heat", summary="Leclerc fades in the closing laps"),
    ]
    mock_rss.get_news.return_value = _make_news_response(*articles)

    result = get_f1_news(team="Red Bull")

    assert result.article_count == 1
    assert "Red Bull" in result.articles[0].title


@patch("pitstop.tools.media.news.rss_client")
def test_bad_date_skipped_with_warning(mock_rss, caplog):
    articles = [
        _article("Good article", published="2024-05-26T12:00:00+00:00"),
        _article("Bad date article", published="not-a-date"),
    ]
    mock_rss.get_news.return_value = _make_news_response(*articles)

    with caplog.at_level(logging.WARNING, logger="pitstop.news"):
        result = get_f1_news(date_from="2024-01-01")

    # Bad date article should be skipped
    assert result.article_count == 1
    assert result.articles[0].title == "Good article"
    assert any("date" in r.message.lower() for r in caplog.records)


@patch("pitstop.tools.media.news.rss_client")
def test_pagination(mock_rss):
    articles = [_article(f"Article {i}") for i in range(5)]
    mock_rss.get_news.return_value = _make_news_response(*articles)

    result = get_f1_news(page=2, page_size=2)

    assert result.article_count == 2
    assert result.articles[0].title == "Article 2"
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 5
    assert result.pagination.has_prev is True
    assert result.pagination.has_next is True


@patch("pitstop.tools.media.news.rss_client")
def test_limit_legacy_param(mock_rss):
    articles = [_article(f"Article {i}") for i in range(10)]
    mock_rss.get_news.return_value = _make_news_response(*articles)

    result = get_f1_news(limit=5)

    assert result.article_count == 5
    assert result.pagination is not None
    assert result.pagination.page == 1
    assert result.pagination.total_items == 10
