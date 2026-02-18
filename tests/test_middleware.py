# Tests for middleware behavior.

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cors_preflight_allows_origin():
	response = client.options(
		"/health",
		headers={
			"Origin": "http://localhost:3000",
			"Access-Control-Request-Method": "GET",
		},
	)
	assert response.status_code in (200, 204)
	assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
