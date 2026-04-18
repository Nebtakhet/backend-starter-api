# Tests for configuration safety validation rules.

import pytest

from app.core.config import Settings


def test_rejects_change_me_secret_key() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY must be set to a strong value"):
        Settings(
            SECRET_KEY="change-me-change-me-change-me-change-me",
            REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000",
            SQLALCHEMY_DATABASE_URI="postgresql://user:pass@localhost:5432/app",
            ENVIRONMENT="development",
        )


def test_rejects_change_me_refresh_token_secret() -> None:
    with pytest.raises(ValueError, match="REFRESH_TOKEN_SECRET must be set to a strong value"):
        Settings(
            SECRET_KEY="test-secret-key-32-chars-min-000000",
            REFRESH_TOKEN_SECRET="change-me-change-me-change-me-change-me",
            SQLALCHEMY_DATABASE_URI="postgresql://user:pass@localhost:5432/app",
            ENVIRONMENT="development",
        )


def test_production_rejects_auto_create_schema() -> None:
    with pytest.raises(ValueError, match="AUTO_CREATE_SCHEMA must be false"):
        Settings(
            SECRET_KEY="test-secret-key-32-chars-min-000000",
            REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000",
            SQLALCHEMY_DATABASE_URI="postgresql://user:pass@localhost:5432/app",
            ENVIRONMENT="production",
            AUTO_CREATE_SCHEMA=True,
        )


def test_production_rejects_proxy_header_trust_without_trusted_peers() -> None:
    with pytest.raises(ValueError, match="RATE_LIMIT_TRUSTED_PROXY_IPS must be set"):
        Settings(
            SECRET_KEY="test-secret-key-32-chars-min-000000",
            REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000",
            SQLALCHEMY_DATABASE_URI="postgresql://user:pass@localhost:5432/app",
            ENVIRONMENT="production",
            RATE_LIMIT_TRUST_PROXY_HEADERS=True,
            RATE_LIMIT_TRUSTED_PROXY_IPS=[],
        )


def test_production_rejects_sqlite() -> None:
    with pytest.raises(ValueError, match="must not use sqlite"):
        Settings(
            SECRET_KEY="test-secret-key-32-chars-min-000000",
            REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000",
            ENVIRONMENT="production",
            SQLALCHEMY_DATABASE_URI="sqlite:///./prod.db",
        )


def test_production_accepts_safe_combination() -> None:
    settings = Settings(
        SECRET_KEY="test-secret-key-32-chars-min-000000",
        REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000",
        SQLALCHEMY_DATABASE_URI="postgresql://user:pass@localhost:5432/app",
        ENVIRONMENT="production",
        AUTO_CREATE_SCHEMA=False,
        RATE_LIMIT_TRUST_PROXY_HEADERS=True,
        RATE_LIMIT_TRUSTED_PROXY_IPS=["127.0.0.1"],
    )
    assert settings.ENVIRONMENT == "production"
