.PHONY: sync run lint typecheck security audit check smoke docker-up docker-down docker-build

sync:
	uv sync

run:
	uv run uvicorn app.main:app --reload

lint:
	uv run ruff check app scripts

typecheck:
	uv run mypy app

security:
	uv run bandit -r app

audit:
	uv run pip-audit

smoke:
	uv run python scripts/smoke_check.py

check: lint typecheck security smoke

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-build:
	docker compose build
