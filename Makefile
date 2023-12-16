
install:
	poetry install

static:
	poetry run ruff format ek
	poetry run ruff check ek --fix
	poetry run mypy ek

test:
	poetry run pytest