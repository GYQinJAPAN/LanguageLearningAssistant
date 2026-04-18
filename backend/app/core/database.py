"""Database engine, session factory, and initialization helpers."""

from collections.abc import AsyncGenerator
from pathlib import Path

from app.core.config import settings
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""

    pass


engine = create_async_engine(settings.DATABASE_URL, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def ensure_sqlite_parent_dir() -> None:
    """Create the parent directory for file-based SQLite databases."""

    url = make_url(settings.DATABASE_URL)

    if not url.drivername.startswith("sqlite"):
        return

    database_path = url.database

    if not database_path or database_path == ":memory:":
        return

    Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


async def init_db() -> None:
    """Create missing database tables for registered ORM models."""
    ensure_sqlite_parent_dir()

    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI dependencies."""
    async with AsyncSessionLocal() as session:
        yield session
