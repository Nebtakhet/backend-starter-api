from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
