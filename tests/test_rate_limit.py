# Rate limit tests for auth endpoints.

import importlib
import os
import sys

from fastapi.testclient import TestClient


def build_app_with_limits(login_limit: str, refresh_limit: str):
	# Build a fresh app instance with custom rate limits.
	os.environ["SECRET_KEY"] = "test-secret-key-32-chars-min-000000"
	os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-32-chars-0000"
	os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
	os.environ["AUTH_LOGIN_RATE_LIMIT"] = login_limit
	os.environ["AUTH_REFRESH_RATE_LIMIT"] = refresh_limit

	# Clear cached app modules to re-evaluate settings and rate limits.
	for name in list(sys.modules):
		if name == "app" or name.startswith("app."):
			del sys.modules[name]

	import app.main as main

	importlib.reload(main)
	return main.app


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
