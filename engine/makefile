# Variables
PYTHON_RUN_SCRIPT = run.py
VENV_DIR ?= .venv
PYTHON_FILES = app/

# Default Target
all: run

install:
	@echo ">>> Installing dependencies using uv..."
	@uv pip sync pyproject.toml
	@echo ">>> Setup complete. Dependencies installed."

run:
	@echo ">>> Running application: $(PYTHON_MAIN)"
	@uv run python $(PYTHON_RUN_SCRIPT)

## Lint code using Ruff
lint: 
	@echo ">>> Linting code with Ruff..."
	@uv run ruff check $(PYTHON_FILES)

## Format code using Ruff
format: 
	@echo ">>> Formatting code with Ruff..."
	@uv run ruff format $(PYTHON_FILES)

## Check code formatting and linting without making changes
check: 
	@echo ">>> Checking code formatting and linting with Ruff..."
	@uv run ruff check $(PYTHON_FILES)
	@uv run ruff format --check $(PYTHON_FILES)

## Remove cache files
clean: 
	@echo ">>> Cleaning cache files..."
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


# Create a virtual environment and install dependencies
migrate-up:
	@echo ">>> Running database migrations..."
	@uv run alembic upgrade head

# Run all database migrations up to the latest version
migrate-down:
	@echo ">>> Running database migrations down..."
	@uv run alembic downgrade -1

# Run all database migrations down to the base
migrate-down-all:
	@echo ">>> Running all database migrations down..."
	@uv run alembic downgrade base

# Create a new migration with a message, using the provided name
migrate-create-empty:
	@echo ">>> Creating new migration..."
	@uv run alembic revision -m "$(name)"

# Create a new migration with autogenerate, using the provided name
migrate-create:
	@echo ">>> Creating new migration..."
	@uv run alembic revision --autogenerate -m "$(name)"

requirements:
	@echo ">>> Generating requirements.txt..."
	@uv pip compile pyproject.toml --generate-hashes -o requirements.txt

.PHONY: all install run lint format check clean migrate-up migrate-down migrate-down-all migrate-create-empty migrate-create requirements
