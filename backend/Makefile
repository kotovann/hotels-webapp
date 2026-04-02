migrate:
	docker compose exec backend uv run python manage.py migrate

makemigrations:
	docker compose exec backend uv run python manage.py makemigrations

shell:
	docker compose exec backend uv run python manage.py shell

superuser:
	docker compose exec backend uv run python manage.py createsuperuser

test:
	docker compose exec backend uv run pytest

lint:
	docker compose exec backend uv run ruff check .

lint-fix:
	docker compose exec backend uv run ruff check --fix .
