"""Pure helper functions."""

import math


def drop_none(d: dict) -> dict:
    """Remove keys with None values from a dict."""
    return {k: v for k, v in d.items() if v is not None}


def filter_by_name(records: list[dict], query: str, fields: list[str]) -> list[dict]:
    """Case-insensitive substring filter across any of the given fields."""
    if not query:
        return records
    q = query.lower()
    return [
        r for r in records
        if any(q in str(r.get(f, "")).lower() for f in fields)
    ]


def paginate(items: list, page: int, page_size: int) -> tuple[list, dict]:
    """Slice items and return (page_slice, pagination_meta). page is 1-indexed."""
    total = len(items)
    total_pages = math.ceil(total / page_size) if total and page_size else 0
    page = max(1, min(page, total_pages)) if total_pages else 1
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def safe_int(val, default: int = 0) -> int:
    """Convert val to int, returning default on failure."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def safe_str(val, default: str = "") -> str:
    """Convert val to str, returning default on failure."""
    if val is None:
        return default
    return str(val)


def safe_float(val, default: float = 0.0) -> float:
    """Convert val to float, returning default on failure."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
