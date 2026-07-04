"""Pure helper functions."""

import math

from pitstop.models.common import PageMeta


def drop_none(d: dict) -> dict:
    """Remove keys with None values from a dict."""
    return {k: v for k, v in d.items() if v is not None}


def filter_by_name(records: list[dict], query: str, fields: list[str]) -> list[dict]:
    """Case-insensitive substring filter across any of the given fields."""
    if not query:
        return records
    q = query.lower()
    return [r for r in records if any(q in str(r.get(f, "")).lower() for f in fields)]


def paginate(items: list, page: int, page_size: int) -> tuple[list, PageMeta]:
    """Slice items and return (page_slice, PageMeta). page is 1-indexed."""
    if page_size <= 0:
        raise ValueError("page_size must be >= 1")
    if not items:
        return [], PageMeta(
            page=0,
            page_size=page_size,
            total_items=0,
            total_pages=0,
            has_next=False,
            has_prev=False,
        )
    total = len(items)
    total_pages = math.ceil(total / page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], PageMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
