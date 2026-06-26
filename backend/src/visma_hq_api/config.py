"""Application settings (pydantic-settings, env-overridable)."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VISMA_HQ_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Async SQLite by default. Set VISMA_HQ_DATABASE_URL to a Postgres URL for a
    # shared/durable database. Plain `postgres://` and `postgresql://` URLs
    # (what Render/Heroku hand out) are accepted and upgraded to the async
    # asyncpg driver automatically — see the validator below.
    database_url: str = "sqlite+aiosqlite:///./visma_hq.db"
    debug: bool = False

    # CORS: the static mockup may be opened from file://, GitHub Pages, etc.
    # Wide-open ("*") for the concept; set to real origins before deployment,
    # e.g. VISMA_HQ_CORS_ORIGINS='["https://visma.github.io"]'.
    cors_origins: list[str] = ["*"]

    # --- SSO integration point (not yet wired) --------------------------------
    # Populate these with your Visma identity provider's OIDC details to replace
    # the demo-user stub in dependencies.get_current_employee. Left blank, the
    # API runs in concept mode (always the seeded demo user).
    oidc_issuer: str = ""
    oidc_audience: str = ""

    @field_validator("database_url")
    @classmethod
    def _use_async_driver(cls, v: str) -> str:
        """Normalize common Postgres URL schemes to the async driver."""
        if v.startswith("postgresql+asyncpg://") or v.startswith("sqlite+aiosqlite://"):
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
