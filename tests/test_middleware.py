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


def test_response_includes_timing_header():
    response = client.get("/health")
    assert response.status_code == 200
    timing = response.headers.get("x-process-time-ms")
    assert timing is not None
    assert float(timing) >= 0


def test_response_includes_request_id_header():
    response = client.get("/health")
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert len(request_id) > 0


def test_request_id_passthrough_from_header():
    expected_request_id = "test-request-id-123"
    response = client.get("/health", headers={"X-Request-ID": expected_request_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == expected_request_id
