
.PHONY: install
install:
	poetry install

.PHONY: static
static:
	poetry run ruff format ek
	poetry run ruff check ek --fix
	poetry run mypy ek

.PHONY: test
test:
	poetry run pytest --cov=ek
