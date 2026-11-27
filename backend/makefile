.PHONY: dev test migrate

dev:
	uv run main.py

test:
	uv run pytest

migrate:
	uv run alembic upgrade head
