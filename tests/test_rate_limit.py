# Rate limit tests for auth endpoints.

import importlib
import os
import sys

from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.rate_limit import get_rate_limit_key
import app.core.rate_limit as rate_limit_module


def _build_app(
    login_limit: str,
    refresh_limit: str,
    *,
    trust_proxy_headers: bool,
    trusted_proxy_hosts: str,
):
    # Build a fresh app instance with custom rate limit settings.
    os.environ["SECRET_KEY"] = "test-secret-key-32-chars-min-000000"
    os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-32-chars-0000"
    os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
    os.environ["AUTH_LOGIN_RATE_LIMIT"] = login_limit
    os.environ["AUTH_REFRESH_RATE_LIMIT"] = refresh_limit
    os.environ["REDIS_URL"] = "memory://"
    os.environ["RATE_LIMIT_TRUST_PROXY_HEADERS"] = "true" if trust_proxy_headers else "false"
    os.environ["RATE_LIMIT_TRUSTED_PROXY_IPS"] = trusted_proxy_hosts

    # Clear cached app modules to re-evaluate settings and rate limits.
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]

    import app.main as main

    importlib.reload(main)
    return main.app


def build_app_with_limits(login_limit: str, refresh_limit: str):
    return _build_app(
        login_limit,
        refresh_limit,
        trust_proxy_headers=False,
        trusted_proxy_hosts="[]",
    )


def build_app_with_proxy_settings(
    login_limit: str,
    refresh_limit: str,
    *,
    trust_proxy_headers: bool,
    trusted_proxy_hosts: str,
):
    return _build_app(
        login_limit,
        refresh_limit,
        trust_proxy_headers=trust_proxy_headers,
        trusted_proxy_hosts=trusted_proxy_hosts,
    )


def test_login_rate_limit_enforced():
    app = build_app_with_limits("1/minute", "1000/minute")
    client = TestClient(app)
    payload = {"email": "invalid@example.com", "password": "wrong"}

    first = client.post("/api/v1/auth/login", json=payload)
    assert first.status_code == 401

    second = client.post("/api/v1/auth/login", json=payload)
    assert second.status_code == 429
    body = second.json()
    assert "error" in body
    assert "Rate limit exceeded" in body["error"]


def test_refresh_rate_limit_enforced():
    app = build_app_with_limits("1000/minute", "1/minute")
    client = TestClient(app)
    payload = {"refresh_token": "invalid-token"}

    first = client.post("/api/v1/auth/refresh", json=payload)
    assert first.status_code == 401

    second = client.post("/api/v1/auth/refresh", json=payload)
    assert second.status_code == 429
    body = second.json()
    assert "error" in body
    assert "Rate limit exceeded" in body["error"]


def test_rate_limit_uses_forwarded_for_when_proxy_is_trusted():
    app = build_app_with_proxy_settings(
        "1/minute",
        "1000/minute",
        trust_proxy_headers=True,
        trusted_proxy_hosts='["testclient"]',
    )
    client = TestClient(app)
    payload = {"email": "invalid@example.com", "password": "wrong"}

    first = client.post(
        "/api/v1/auth/login",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.10"},
    )
    assert first.status_code == 401

    second = client.post(
        "/api/v1/auth/login",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.11"},
    )
    assert second.status_code == 401


def test_rate_limit_ignores_forwarded_for_when_proxy_is_untrusted():
    app = build_app_with_proxy_settings(
        "1/minute",
        "1000/minute",
        trust_proxy_headers=True,
        trusted_proxy_hosts='["127.0.0.1"]',
    )
    client = TestClient(app)
    payload = {"email": "invalid@example.com", "password": "wrong"}

    first = client.post(
        "/api/v1/auth/login",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.10"},
    )
    assert first.status_code == 401

    second = client.post(
        "/api/v1/auth/login",
        json=payload,
        headers={"X-Forwarded-For": "203.0.113.11"},
    )
    assert second.status_code == 429


def _request(client_host: str | None, forwarded_for: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if forwarded_for is not None:
        headers.append((b"x-forwarded-for", forwarded_for.encode("utf-8")))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": (client_host, 12345) if client_host is not None else None,
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_rate_limit_key_uses_first_forwarded_ip_for_trusted_proxy(monkeypatch):
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUST_PROXY_HEADERS", True)
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUSTED_PROXY_IPS", ["10.0.0.1"])

    request = _request("10.0.0.1", "203.0.113.10, 70.41.3.18")
    assert get_rate_limit_key(request) == "203.0.113.10"


def test_rate_limit_key_ignores_malformed_forwarded_ip(monkeypatch):
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUST_PROXY_HEADERS", True)
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUSTED_PROXY_IPS", ["10.0.0.1"])

    request = _request("10.0.0.1", "not-an-ip")
    assert get_rate_limit_key(request) == "10.0.0.1"


def test_rate_limit_key_returns_unknown_when_client_missing(monkeypatch):
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUST_PROXY_HEADERS", True)
    monkeypatch.setattr(rate_limit_module.settings, "RATE_LIMIT_TRUSTED_PROXY_IPS", ["10.0.0.1"])

    request = _request(None, "203.0.113.10")
    assert get_rate_limit_key(request) == "unknown"
