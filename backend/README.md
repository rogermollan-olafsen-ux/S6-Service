# Visma HQ Employee API

Concept backend for the Visma HQ employee app. FastAPI + async SQLAlchemy 2.0 + SQLite.
Follows PEP 517/518 packaging (`pyproject.toml`, src layout).

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run the API (auto-creates + seeds the SQLite db on first start)
python -m visma_hq_api
# → http://127.0.0.1:8000   ·   interactive docs at /docs
```

Then open `../index.html` in a browser — it auto-detects the API at
`http://127.0.0.1:8000` and goes live. If the API isn't running, the mockup
falls back to its built-in demo values, so the static GitHub Pages version
still works.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Liveness check |
| GET | `/api/me` | Current employee (SSO stub) |
| GET | `/api/wallet` | Wallet balance |
| GET | `/api/wallet/transactions` | Recent transactions |
| POST | `/api/wallet/pay` | Charge the wallet `{merchant, amount_ore}` |
| POST | `/api/wallet/topup` | Add funds `{amount_ore}` |
| GET | `/api/lockers/mine` | Lockers assigned to you |
| POST | `/api/lockers/{id}/toggle` | Lock / unlock |
| GET | `/api/massage/slots` | Slots (optional `?day=`) |
| POST | `/api/massage/slots/{id}/book` | Book a slot |
| DELETE | `/api/massage/slots/{id}/book` | Cancel your booking |
| GET | `/api/spaces` | Desks/rooms/booths (optional `?kind=`) |
| POST | `/api/spaces/{id}/reserve` | Reserve |
| POST | `/api/spaces/{id}/release` | Release your reservation |

Money is handled as integer **øre** (1 NOK = 100 øre) to avoid float errors.

## Deploy

A production `Dockerfile` lives here; deploy configs are at the repo root.

**Docker (anywhere):**

```bash
docker build -t visma-hq-api ./backend
docker run -p 8000:8000 -v visma_hq_data:/app/data visma-hq-api
```

**Local / self-hosted (Docker Compose)** — best fit for an internal Visma
server. SQLite by default (data in a named volume):

```bash
docker compose up --build                                   # SQLite
# or run against Postgres instead:
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build
```

**Public demo (Render):** push to GitHub, then Render → New → Blueprint → pick
the repo (`render.yaml` is detected automatically). The blueprint provisions a
managed Postgres database, wires its connection string into the API, and
**redeploys automatically on every push** (`autoDeploy: true`). You get a
public `https` URL — point the static mockup at it:

```
https://<org>.github.io/<repo>/?api=https://visma-hq-api.onrender.com
```

The container runs `uvicorn` on `0.0.0.0:$PORT` (no `--reload`), runs as a
non-root user, and exposes a `/api/health` healthcheck.

**Database URLs:** the default is local SQLite. Set `VISMA_HQ_DATABASE_URL` to a
Postgres URL for a shared, durable database — plain `postgres://` and
`postgresql://` URLs (what Render/Heroku hand out) are accepted and upgraded to
the async `asyncpg` driver automatically. See `.env.example` for all settings.

> Schema is created on startup (`create_all`). For evolving a real Postgres
> schema over time you'll want migrations (Alembic) — a logical next step.

## Tests, lint, types

```bash
pytest                  # in-memory DB, fully isolated per test
ruff check src tests
mypy
```

## Not production-ready — known stubs

- **Auth:** `/api/me` always returns the seeded demo user. Replace
  `get_current_employee` with real Visma SSO (OIDC) before any deployment.
- **CORS** is wide open (`*`). Lock to real origins.
- **No concurrency control** on bookings beyond a status check; a real build
  needs row locking / unique constraints to prevent double-booking races.
- SQLite is fine for the concept; switch `VISMA_HQ_DATABASE_URL` to Postgres
  (`postgresql+asyncpg://…`) for anything shared.
