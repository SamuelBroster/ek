
.PHONY: install
install:
	poetry install

.PHONY: static
static:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy ek

.PHONY: test
test:
	poetry run pytest --cov=ek
