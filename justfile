# ullm development tasks

# Default recipe - show available commands
default:
    @just --list

# Install package in development mode
install:
    uv pip install -e ".[dev]"

# Run tests
test:
    pytest tests/ -v

# Run tests with coverage
test-cov:
    pytest tests/ --cov=ullm --cov-report=html --cov-report=term

# Run linter
lint:
    ruff check .

# Format code and fix issues
format:
    ruff format .
    ruff check --fix .

# Run type checker
type-check:
    mypy ullm --ignore-missing-imports

# Clean build artifacts and cache files
clean:
    rm -rf build dist *.egg-info
    rm -rf .pytest_cache .mypy_cache .ruff_cache
    rm -rf htmlcov .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +

# Run all checks (format, lint, type-check, test)
all: format lint type-check test

# Set up development environment
dev:
    @echo "Setting up development environment..."
    uv venv
    @echo "Now run: source .venv/bin/activate"
    @echo "Then run: just install"

# Run CI checks (same as CI will run)
ci: lint type-check test-cov
