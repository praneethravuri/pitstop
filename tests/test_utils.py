"""Tests for src/pitstop/utils/utils.py — written first (TDD)."""

import pytest
from pitstop.models.common import PageMeta
from pitstop.utils.utils import drop_none, filter_by_name, paginate, safe_int, safe_str, safe_float


# ---------------------------------------------------------------------------
# drop_none
# ---------------------------------------------------------------------------

def test_drop_none_empty():
    assert drop_none({}) == {}


def test_drop_none_all_none():
    assert drop_none({"a": None, "b": None}) == {}


def test_drop_none_mixed():
    result = drop_none({"a": 1, "b": None, "c": "x"})
    assert result == {"a": 1, "c": "x"}


def test_drop_none_no_none():
    d = {"x": 0, "y": False, "z": ""}
    assert drop_none(d) == d


# ---------------------------------------------------------------------------
# filter_by_name
# ---------------------------------------------------------------------------

RECORDS = [
    {"name": "Max Verstappen", "team": "Red Bull"},
    {"name": "Lewis Hamilton", "team": "Mercedes"},
    {"name": "Charles Leclerc", "team": "Ferrari"},
]


def test_filter_by_name_exact_match():
    result = filter_by_name(RECORDS, "Max Verstappen", ["name"])
    assert len(result) == 1
    assert result[0]["name"] == "Max Verstappen"


def test_filter_by_name_substring():
    result = filter_by_name(RECORDS, "hamilton", ["name"])
    assert len(result) == 1
    assert result[0]["name"] == "Lewis Hamilton"


def test_filter_by_name_case_insensitive():
    result = filter_by_name(RECORDS, "FERRARI", ["team"])
    assert len(result) == 1
    assert result[0]["team"] == "Ferrari"


def test_filter_by_name_multi_field():
    result = filter_by_name(RECORDS, "red", ["name", "team"])
    assert len(result) == 1
    assert result[0]["team"] == "Red Bull"


def test_filter_by_name_no_match():
    result = filter_by_name(RECORDS, "alpine", ["name", "team"])
    assert result == []


def test_filter_by_name_empty_query_returns_all():
    result = filter_by_name(RECORDS, "", ["name"])
    assert result == RECORDS


# ---------------------------------------------------------------------------
# paginate
# ---------------------------------------------------------------------------

ITEMS = list(range(1, 11))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_paginate_page_1():
    page_slice, meta = paginate(ITEMS, 1, 3)
    assert page_slice == [1, 2, 3]
    assert meta.page == 1
    assert meta.page_size == 3
    assert meta.total_items == 10
    assert meta.total_pages == 4
    assert meta.has_prev is False
    assert meta.has_next is True


def test_paginate_middle_page():
    page_slice, meta = paginate(ITEMS, 2, 3)
    assert page_slice == [4, 5, 6]
    assert meta.has_prev is True
    assert meta.has_next is True


def test_paginate_last_page():
    page_slice, meta = paginate(ITEMS, 4, 3)
    assert page_slice == [10]
    assert meta.has_next is False
    assert meta.has_prev is True


def test_paginate_beyond_range_clamps():
    page_slice, meta = paginate(ITEMS, 99, 3)
    assert meta.page == 4  # clamped to last valid page
    assert page_slice == [10]


def test_paginate_page_size_greater_than_total():
    page_slice, meta = paginate(ITEMS, 1, 50)
    assert page_slice == ITEMS
    assert meta.total_pages == 1
    assert meta.has_next is False
    assert meta.has_prev is False


def test_paginate_page_zero_clamps_to_1():
    page_slice, meta = paginate(ITEMS, 0, 3)
    assert meta.page == 1
    assert page_slice == [1, 2, 3]


def test_paginate_empty_list():
    page_slice, meta = paginate([], 1, 10)
    assert page_slice == []
    assert meta.page == 0
    assert meta.total_items == 0
    assert meta.total_pages == 0
    assert meta.has_next is False
    assert meta.has_prev is False


def test_paginate_returns_page_meta():
    _, meta = paginate(ITEMS, 1, 3)
    assert isinstance(meta, PageMeta)


def test_paginate_empty_returns_page_meta():
    _, meta = paginate([], 1, 10)
    assert isinstance(meta, PageMeta)


def test_paginate_negative_page_size_raises():
    with pytest.raises(ValueError, match="page_size must be >= 1"):
        paginate([1, 2, 3], 1, -1)


def test_paginate_zero_page_size_raises():
    with pytest.raises(ValueError, match="page_size must be >= 1"):
        paginate([1, 2, 3], 1, 0)


# ---------------------------------------------------------------------------
# safe_int
# ---------------------------------------------------------------------------

def test_safe_int_happy():
    assert safe_int(42) == 42
    assert safe_int("7") == 7


def test_safe_int_none():
    assert safe_int(None) == 0
    assert safe_int(None, default=5) == 5


def test_safe_int_bad_string():
    assert safe_int("abc") == 0
    assert safe_int("abc", default=-1) == -1


# ---------------------------------------------------------------------------
# safe_str
# ---------------------------------------------------------------------------

def test_safe_str_happy():
    assert safe_str("hello") == "hello"
    assert safe_str(123) == "123"


def test_safe_str_none():
    assert safe_str(None) == ""
    assert safe_str(None, default="n/a") == "n/a"


def test_safe_str_empty():
    assert safe_str("") == ""


# ---------------------------------------------------------------------------
# safe_float
# ---------------------------------------------------------------------------

def test_safe_float_happy():
    assert safe_float(3.14) == pytest.approx(3.14)
    assert safe_float("2.5") == pytest.approx(2.5)


def test_safe_float_none():
    assert safe_float(None) == 0.0
    assert safe_float(None, default=1.0) == 1.0


def test_safe_float_bad_string():
    assert safe_float("not_a_float") == 0.0
    assert safe_float("nope", default=-1.0) == -1.0
