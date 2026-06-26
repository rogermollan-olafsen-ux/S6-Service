# syntax=docker/dockerfile:1
# Production image for the Visma HQ employee API.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the package. Copy only what the build needs first so Docker can
# cache the dependency layer when only source changes.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

# SQLite lives on a mounted volume so data survives container restarts.
# Override with VISMA_HQ_DATABASE_URL (e.g. a Postgres DSN) in real deployments.
ENV VISMA_HQ_DATABASE_URL=sqlite+aiosqlite:////app/data/visma_hq.db

# Run as a non-root user.
RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Platforms (Render, Fly, etc.) inject $PORT; default to 8000 locally.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','8000'); sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{p}/api/health').status==200 else 1)"

CMD ["sh", "-c", "uvicorn visma_hq_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
