up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

db-shell:
	docker compose exec db psql -U telecom_user -d telecom_db

migrate:
	uv run alembic upgrade head

run:
	uv run uvicorn app.main:app --reload

lint:
	uv run bandit -r app

audit:
	uv run pip-audit

test:
	uv run pytest
