# Variables
PYTHON_MAIN = app.main
VENV_DIR ?= .venv

install:
	@echo ">>> Installing dependencies using uv..."
	@uv pip sync pyproject.toml

run:
	@echo ">>> Running application: $(PYTHON_MAIN)"
	@uv run python -m $(PYTHON_MAIN)

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


.PHONY: install run lint format check clean
