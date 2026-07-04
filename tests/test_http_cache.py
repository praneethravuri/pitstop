"""Tests for transparent HTTP response caching (src/pitstop/clients/http.py)."""

import pytest

import pitstop.clients as clients_mod
from pitstop.clients.http import make_client


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the OpenF1 client singleton before and after each test."""
    clients_mod._openf1_client = None
    yield
    clients_mod._openf1_client = None


def test_identical_get_is_cached(httpx_mock):
    httpx_mock.add_response(json={"a": 1})
    client = make_client(base_url="https://example.com", cache_ttl=60)

    r1 = client.get("/thing")
    r2 = client.get("/thing")

    assert len(httpx_mock.get_requests()) == 1
    assert r1.json() == r2.json() == {"a": 1}


def test_error_response_is_not_cached(httpx_mock):
    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(json={"ok": True})
    client = make_client(base_url="https://example.com", cache_ttl=60)

    r1 = client.get("/thing")
    r2 = client.get("/thing")

    assert r1.status_code == 500
    assert r2.status_code == 200
    assert len(httpx_mock.get_requests()) == 2


def test_no_cache_ttl_means_no_caching(httpx_mock):
    httpx_mock.add_response(json={"a": 1})
    httpx_mock.add_response(json={"a": 1})
    client = make_client(base_url="https://example.com", cache_ttl=None)

    client.get("/thing")
    client.get("/thing")

    assert len(httpx_mock.get_requests()) == 2


def test_factory_wiring_caches_repeated_openf1_calls(httpx_mock, monkeypatch):
    monkeypatch.setattr(clients_mod, "ENABLE_CACHING", True)
    monkeypatch.setattr(clients_mod, "CACHE_TTL_SECONDS", 60)
    httpx_mock.add_response(json=[{"session_name": "Race"}])

    client = clients_mod.get_openf1_client()
    client.get("/sessions", params={"year": 2024})
    client.get("/sessions", params={"year": 2024})

    assert len(httpx_mock.get_requests()) == 1
