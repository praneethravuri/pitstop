from pydantic import BaseModel, Field
from .general import NewsArticle


class SillySeasonArticle(NewsArticle):
    """Silly season news article with categorization."""

    category: str = Field(..., description="News category (transfer, management, contract, etc.)")
    relevance_score: float | None = Field(None, description="Relevance score based on keywords (0-1)")


class SillySeasonResponse(BaseModel):
    """Collection of silly season news articles."""

    query_type: str = Field(..., description="Type of query (year, driver, constructor, etc.)")
    query_value: str | None = Field(None, description="The search parameter value")
    fetched_at: str = Field(..., description="When the feed was fetched")
    article_count: int = Field(..., description="Number of articles returned")
    articles: list[SillySeasonArticle] = Field(..., description="List of silly season articles")
