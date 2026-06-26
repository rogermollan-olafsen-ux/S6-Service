"""Test fixtures: each test runs against a fresh, seeded in-memory database.

Note: httpx's ASGITransport does not emit ASGI lifespan events, so the app's
own startup (which would create a file-based DB) never runs here. We build and
seed an isolated in-memory engine and override the request session dependency.
A StaticPool is required so the single in-memory connection is shared across
sessions — otherwise each connection would see an empty, separate database.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from visma_hq_api.db import Base, get_session
from visma_hq_api.main import create_app
from visma_hq_api.seed import seed


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",  # in-memory
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with sessionmaker() as session:
        await seed(session)

    app = create_app()

    async def _override() -> AsyncIterator:
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = _override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await engine.dispose()
