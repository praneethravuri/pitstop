"""Shared response primitives."""

from pydantic import BaseModel, ConfigDict


class PageMeta(BaseModel):
    model_config = ConfigDict(strict=True)

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PartialError(BaseModel):
    model_config = ConfigDict(strict=True)

    item: str
    source: str
    reason: str


class PartialErrors(BaseModel):
    model_config = ConfigDict(strict=True)

    errors: list[PartialError] = []

    def add(self, item: str, source: str, exc: Exception) -> None:
        self.errors.append(PartialError(item=item, source=source, reason=str(exc)))

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)
