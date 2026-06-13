FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.8.12 /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/false appuser

WORKDIR /code

COPY --from=builder --chown=appuser:appgroup /code/.venv /code/.venv
COPY --from=builder --chown=appuser:appgroup /code/app /code/app
COPY --from=builder --chown=appuser:appgroup /code/alembic /code/alembic
COPY --from=builder --chown=appuser:appgroup /code/alembic.ini /code/alembic.ini

ENV PATH="/code/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/health/live'); exit(0 if r.status_code == 200 else 1)"

ENTRYPOINT ["tini", "--"]

CMD ["gunicorn", "app.main:app", "-k", "uvicorn_worker.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
