from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from core.config import settings


def _build_async_url(url: str) -> str:
    """Convert sync postgres:// URL to async postgresql+asyncpg://"""
    return (
        url.replace("postgresql://", "postgresql+asyncpg://")
           .replace("postgres://", "postgresql+asyncpg://")
    )


ASYNC_DATABASE_URL = _build_async_url(settings.DATABASE_URL)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """Create all tables defined by ORM models (called on app startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
