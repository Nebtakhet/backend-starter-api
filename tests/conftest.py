# Pytest fixtures and test configuration.

import os
import asyncio

import pytest

# Override config for test runs.

os.environ["SECRET_KEY"] = "test-secret-key-32-chars-min-000000"
os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret-32-chars-0000"
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./test.db"
os.environ["AUTH_LOGIN_RATE_LIMIT"] = "1000/minute"
os.environ["AUTH_REFRESH_RATE_LIMIT"] = "1000/minute"
os.environ["REDIS_URL"] = "memory://"

from app.db.base import Base
from app.db.session import engine


def _run(coro):
    return asyncio.run(coro)


async def _create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create and teardown schema once for the test session.
    _run(_create_all())
    yield
    _run(_drop_all())
