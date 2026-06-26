# Visma HQ — Employee App (Concept Mockup)

Interactive, clickable concept mockup of the employee app for Visma's new HQ.
Single self-contained `index.html` file — no build step, no dependencies.

**Live demo:** _(enable GitHub Pages — see below — then paste the URL here)_

## What's in it

A mobile (phone) prototype in the Visma brand look (red ribbon `#E60641` on white). Tap through:

- **Home** — wallet balance, service tiles, "coming soon" items
- **Pay** — HQ wallet, tap-to-pay, recent transactions
- **Lockers** — view and remotely unlock your personal locker
- **Massage** — book an in-house wellness slot
- **Rooms & Desks** — reserve a desk, meeting room, or phone booth

> This is a **visual concept only**. No real data, authentication, or payments. It exists to align stakeholders before we scope the real build.

## Run it locally

Just open `index.html` in any modern browser. That's it — it shows built-in
demo data.

### Make it live (optional backend)

A FastAPI + SQLite backend lives in [`backend/`](backend/). When it's running,
the mockup auto-detects it at `http://127.0.0.1:8000`, shows a green **Live**
badge, and every action (pay, unlock, book) hits real endpoints backed by a
database. If the backend isn't running, the mockup silently falls back to its
demo values — so the static GitHub Pages version always works.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m visma_hq_api          # API at http://127.0.0.1:8000, docs at /docs
```

See [`backend/README.md`](backend/README.md) for the full endpoint list and the
known stubs (auth, CORS) to address before any real deployment.

## Publish a shareable link (GitHub Pages)

1. Push this repo to GitHub (see commands below).
2. In the repo on GitHub: **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Branch: **main**, folder: **/ (root)**. Save.
5. Wait ~1 minute, then your link appears at the top of the Pages settings — typically `https://<org>.github.io/<repo>/`.
6. Paste that link into the **Live demo** line above.

> Pages on a **private** org repo requires GitHub Enterprise / a paid plan. If Pages is unavailable, share the repo and have people open `index.html` locally.

## Open questions before a real build

- **Payments:** does the app hold a balance, or authorize against payroll / an external wallet? (PCI scope, POS integration)
- **Locker unlock:** which lock hardware (BLE vs networked)? Auth model for a lost/stolen phone?
- **Identity:** Visma SSO?

## Continuous integration

`.github/workflows/ci.yml` runs on every push and PR to `main`:

1. **Lint & test** — `ruff check` + `pytest` against the backend.
2. **Build & push** (main only) — builds the Docker image and publishes it to
   the GitHub Container Registry at `ghcr.io/<org>/<repo>:latest`.

No setup needed — it uses the built-in `GITHUB_TOKEN`. After the first run,
the image is pullable with `docker pull ghcr.io/<org>/<repo>:latest`, and Render
(or any host) can deploy straight from GHCR.

## Status

`v0.1` — concept mockup. Not production code.
