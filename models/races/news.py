from pydantic import BaseModel, Field
from models.news import NewsArticle


class RaceNewsArticle(NewsArticle):
    """News article specific to a race weekend."""

    category: str = Field(..., description="News category (practice, qualifying, race, highlights)")
    race_name: str | None = Field(None, description="Associated race name")


class RaceNewsResponse(BaseModel):
    """Collection of race weekend news articles."""

    race_name: str | None = Field(None, description="Race name filter (if used)")
    year: int | None = Field(None, description="Year filter (if used)")
    category: str = Field(..., description="News category")
    fetched_at: str = Field(..., description="When the feed was fetched")
    article_count: int = Field(..., description="Number of articles returned")
    articles: list[RaceNewsArticle] = Field(..., description="List of race news articles")
