# Database engine and session factory configuration.

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def to_async_database_uri(uri: str) -> str:
    if uri.startswith("sqlite://") and not uri.startswith("sqlite+aiosqlite://"):
        return uri.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if uri.startswith("postgres://"):
        return uri.replace("postgres://", "postgresql+asyncpg://", 1)
    if uri.startswith("postgresql+asyncpg://"):
        return uri
    if uri.startswith("postgresql+"):
        scheme = uri.split("://", 1)[0]
        return uri.replace(f"{scheme}://", "postgresql+asyncpg://", 1)
    if uri.startswith("postgresql://"):
        return uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    return uri


engine = create_async_engine(to_async_database_uri(settings.SQLALCHEMY_DATABASE_URI))

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)
