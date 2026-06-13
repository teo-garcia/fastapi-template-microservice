.PHONY: dev start build ruff-config lint lint-check lint-types format format-check test test-cov test-e2e check db-migrate db-deploy db-reset db-seed docker-dev

# -- Development --

dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start:
	uv run gunicorn app.main:app -k uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000

build:
	docker build -f docker/Dockerfile -t fastapi-template-microservice .

# -- Quality --

ruff-config:
	@printf 'extend = "%s"\n' "$$(uv run teo-ruff-config-path)" > ruff.extend.toml

lint: ruff-config
	uv run ruff check --fix .

lint-check: ruff-config
	uv run ruff check .

lint-types:
	uv run mypy .

format: ruff-config
	uv run ruff format .

format-check: ruff-config
	uv run ruff format --check .

test:
	uv run pytest

test-cov:
	uv run pytest --cov

test-e2e:
	uv run pytest -m e2e

check: lint-check format-check lint-types test

# -- Database --

db-migrate:
	uv run alembic revision --autogenerate -m "$(msg)"

db-deploy:
	uv run alembic upgrade head

db-reset:
	uv run alembic downgrade base && uv run alembic upgrade head

db-seed:
	uv run python -m app.seed

# -- Docker --

docker-dev:
	docker compose up --build
