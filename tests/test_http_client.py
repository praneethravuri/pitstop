"""Tests for src/pitstop/clients/http.py — written first (TDD)."""

from urllib.parse import urlparse

import httpx

from pitstop.clients import get_jolpica_client, get_openf1_client
from pitstop.clients.http import http_retry, make_client


def test_make_client_returns_nonnone():
    client = make_client()
    assert client is not None
    client.close()


def test_make_client_is_httpx_client():
    client = make_client()
    assert isinstance(client, httpx.Client)
    client.close()


def test_make_client_has_correct_base_url():
    client = make_client(base_url="https://api.openf1.org/v1")
    assert "openf1.org" in str(client.base_url)
    client.close()


def test_make_client_custom_timeout():
    client = make_client(timeout=10.0)
    assert client.timeout.connect == 10.0
    client.close()


def test_http_retry_is_callable():
    decorator = http_retry()
    assert callable(decorator)


def test_http_retry_wraps_function():
    calls = []

    @http_retry(max_attempts=1)
    def dummy():
        calls.append(1)
        return "ok"

    result = dummy()
    assert result == "ok"
    assert calls == [1]


def test_get_openf1_client_returns_nonnone():
    import pitstop.clients as clients_mod

    clients_mod._openf1_client = None

    client = get_openf1_client()
    assert client is not None


def test_get_openf1_client_singleton():
    import pitstop.clients as clients_mod

    clients_mod._openf1_client = None

    c1 = get_openf1_client()
    c2 = get_openf1_client()
    assert c1 is c2


def test_get_openf1_client_base_url():
    import pitstop.clients as clients_mod

    clients_mod._openf1_client = None

    client = get_openf1_client()
    host = urlparse(str(client.base_url)).hostname
    assert host is not None and (host == "openf1.org" or host.endswith(".openf1.org"))


def test_get_jolpica_client_returns_nonnone():
    import pitstop.clients as clients_mod

    clients_mod._jolpica_client = None

    client = get_jolpica_client()
    assert client is not None


def test_get_jolpica_client_singleton():
    import pitstop.clients as clients_mod

    clients_mod._jolpica_client = None

    c1 = get_jolpica_client()
    c2 = get_jolpica_client()
    assert c1 is c2


def test_get_jolpica_client_base_url():
    import pitstop.clients as clients_mod

    clients_mod._jolpica_client = None

    client = get_jolpica_client()
    assert "jolpi.ca" in str(client.base_url)
