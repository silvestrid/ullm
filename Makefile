.PHONY: install test lint format type-check clean all

install:
	uv pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=ullm --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

type-check:
	mypy ullm --ignore-missing-imports

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

all: format lint type-check test

dev:
	@echo "Setting up development environment..."
	uv venv
	@echo "Now run: source .venv/bin/activate"
	@echo "Then run: make install"
