"""F1DB tool models."""

from typing import Any

from pydantic import BaseModel, ConfigDict

from pitstop.models.common import PageMeta


class F1DBResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    sql: str
    rows: list[dict[str, Any]]
    row_count: int
    pagination: PageMeta | None = None
