up:
	@docker compose up -d --build

down:
	@docker compose down

r:
	@docker compose restart

rebuild-api:
	@docker compose build api

logs:
	docker compose logs -f api

db-shell:
	docker compose exec db psql -U $${POSTGRES_USER:-telecom_user} -d $${POSTGRES_DB:-telecom_db}

migrate:
	uv run alembic upgrade head

run:
	uv run uvicorn app.main:app --reload

bandit:
	uv run bandit -r app

audit:
	uv run pip-audit

ruff:
	uv run ruff check app

mypy:
	uv run mypy app
