"""News tool models."""

from pydantic import BaseModel, ConfigDict, Field

from pitstop.models.common import PageMeta


class NewsArticle(BaseModel):
    """Individual news article from RSS feed."""

    model_config = ConfigDict(strict=True)

    title: str = Field(..., description="Article headline")
    link: str = Field(..., description="URL to full article")
    published: str = Field(..., description="Publication date and time")
    summary: str = Field(..., description="Article excerpt or description")
    source: str = Field(..., description="News source name")
    author: str | None = Field(None, description="Article author if available")


class NewsResponse(BaseModel):
    """Collection of F1 news articles."""

    model_config = ConfigDict(strict=True)

    source: str = Field(..., description="News source(s) queried")
    fetched_at: str = Field(..., description="When the feed was fetched")
    article_count: int = Field(..., description="Number of articles returned")
    articles: list[NewsArticle] = Field(..., description="List of news articles")
    failed_feeds: list[str] = Field(
        default_factory=list, description="Feed names that failed to fetch"
    )
    pagination: PageMeta | None = Field(None, description="Pagination metadata")
