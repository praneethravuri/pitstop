"""Wikidata tool models."""

from pydantic import BaseModel, ConfigDict

from pitstop.models.common import PageMeta


class WikidataResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    query: str
    rows: list[dict[str, str]]
    row_count: int
    pagination: PageMeta | None = None
