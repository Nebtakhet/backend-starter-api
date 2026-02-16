# Pytest fixtures and test configuration.

import os

import pytest

# Override config for test runs.

os.environ["SECRET_KEY"] = "test-secret-key-32-chars-min-000000"
os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-32-chars-0000"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
os.environ["AUTH_LOGIN_RATE_LIMIT"] = "1000/minute"
os.environ["AUTH_REFRESH_RATE_LIMIT"] = "1000/minute"

from app.db.base import Base
from app.db.session import engine


@pytest.fixture(scope="session", autouse=True)
def setup_database():
	# Create and teardown schema once for the test session.
	Base.metadata.create_all(bind=engine)
	yield
	Base.metadata.drop_all(bind=engine)
