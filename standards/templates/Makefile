# Makefile template for Python projects
# Replace <package_name> with your package name (snake_case)

PYTHON ?= python3
PACKAGE = <package_name>

.PHONY: all install install-dev install-no-deps uninstall clean format lint typecheck test test-verbose coverage help

all: format lint typecheck test coverage  ## Run all checks (default)

install:  ## Install package
	$(PYTHON) -m pip install .

install-dev:  ## Install package with development dependencies
	$(PYTHON) -m pip install -e ".[dev]"

install-no-deps:  ## Install package without dependencies (for monorepo development)
	$(PYTHON) -m pip install -e . --no-deps

uninstall:  ## Uninstall package
	$(PYTHON) -m pip uninstall -y $(PACKAGE)

clean:  ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/ || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

format: install-dev  ## Format code with black
	$(PYTHON) -m black $(PACKAGE) tests

format-check: install-dev  ## Check formatting without changes
	$(PYTHON) -m black --check $(PACKAGE) tests

lint: install-dev  ## Run flake8 linter
	$(PYTHON) -m flake8 $(PACKAGE) tests

typecheck: install-dev  ## Run mypy type checker
	$(PYTHON) -m mypy $(PACKAGE)

test: install-dev  ## Run tests
	$(PYTHON) -m pytest tests/

test-verbose: install-dev  ## Run tests with verbose output
	$(PYTHON) -m pytest -v tests/

coverage: install-dev  ## Run tests with coverage report
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=term-missing --cov-fail-under=80 tests/

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
