"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from visma_hq_api import __version__
from visma_hq_api.config import settings
from visma_hq_api.db import Base, SessionLocal, engine
from visma_hq_api.routers import lockers, massage, me, rooms, wallet
from visma_hq_api.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create tables and seed demo data on startup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        await seed(session)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Visma HQ Employee API",
        version=__version__,
        summary="Concept backend for the Visma HQ employee app.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(me.router, prefix="/api/me", tags=["me"])
    app.include_router(wallet.router, prefix="/api/wallet", tags=["wallet"])
    app.include_router(lockers.router, prefix="/api/lockers", tags=["lockers"])
    app.include_router(massage.router, prefix="/api/massage", tags=["massage"])
    app.include_router(rooms.router, prefix="/api/spaces", tags=["rooms"])

    @app.get("/api/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
