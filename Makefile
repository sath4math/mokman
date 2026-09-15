.PHONY: dev dev-web dev-api infra-up infra-down migrate test

infra-up:
	docker compose up -d

infra-down:
	docker compose down

dev-web:
	pnpm install
	pnpm --filter web dev

dev-api:
	cd services/api && uv sync && uv run uvicorn app.main:app --reload

migrate:
	cd services/api && uv run alembic upgrade head

test:
	cd services/api && uv run pytest
	pnpm --filter web test
