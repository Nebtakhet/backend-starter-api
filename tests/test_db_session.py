# Tests for database session URI conversion helpers.

from app.db.session import to_async_database_uri


def test_sqlite_uri_converts_to_aiosqlite():
    uri = "sqlite:///./app.db"
    assert to_async_database_uri(uri) == "sqlite+aiosqlite:///./app.db"


def test_sqlite_async_uri_is_unchanged():
    uri = "sqlite+aiosqlite:///./app.db"
    assert to_async_database_uri(uri) == uri


def test_postgres_short_scheme_converts_to_asyncpg():
    uri = "postgres://user:pass@localhost:5432/db"
    assert to_async_database_uri(uri) == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_postgresql_plain_scheme_converts_to_asyncpg():
    uri = "postgresql://user:pass@localhost:5432/db"
    assert to_async_database_uri(uri) == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_postgresql_psycopg2_scheme_converts_to_asyncpg():
    uri = "postgresql+psycopg2://user:pass@localhost:5432/db"
    assert to_async_database_uri(uri) == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_postgresql_asyncpg_scheme_is_unchanged():
    uri = "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert to_async_database_uri(uri) == uri


def test_other_uris_are_unchanged():
    uri = "mysql://user:pass@localhost:3306/db"
    assert to_async_database_uri(uri) == uri
