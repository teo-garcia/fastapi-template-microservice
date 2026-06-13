from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest import MonkeyPatch
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import Settings, get_settings
from app.modules.tasks.models import Task  # noqa: F401
from app.shared.database.base import Base
from app.shared.database.engine import get_db
from app.shared.messaging.nats_client import get_nats
from app.shared.redis.client import get_redis


def get_test_settings() -> Settings:
    return Settings(_env_file=".env.test")


@pytest_asyncio.fixture
async def app_client(monkeypatch: MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    monkeypatch.setenv("APP_NAME", "FastAPI Microservice Template")
    monkeypatch.setenv("OTEL_ENABLED", "false")
    monkeypatch.setenv("METRICS_ENABLED", "false")
    monkeypatch.setenv("REDIS_HOST", "127.0.0.1")
    monkeypatch.setenv("REDIS_PORT", "1")
    get_settings.cache_clear()

    from app.main import create_app

    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    get_settings.cache_clear()


@pytest_asyncio.fixture
async def client(monkeypatch: MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    settings = get_test_settings()
    monkeypatch.setenv("API_PREFIX", settings.api_prefix)
    monkeypatch.setenv("OTEL_ENABLED", "false")
    get_settings.cache_clear()
    engine = create_async_engine(settings.database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            yield session

    mock_redis: AsyncMock = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.aclose = AsyncMock()
    mock_nats: AsyncMock = AsyncMock()
    mock_nats.is_healthy = AsyncMock(return_value=True)

    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_nats] = lambda: mock_nats
    app.dependency_overrides[get_settings] = get_test_settings

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    get_settings.cache_clear()
