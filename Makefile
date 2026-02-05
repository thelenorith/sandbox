PYTHON ?= python3
PACKAGE = prometheus_mcp_server

.PHONY: default install install-dev uninstall clean format lint typecheck test coverage

default: format lint typecheck test coverage

install:
	$(PYTHON) -m pip install .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

uninstall:
	$(PYTHON) -m pip uninstall -y prometheus-mcp-server 2>/dev/null || true

clean:
	rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/ 2>/dev/null || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

format: install-dev
	$(PYTHON) -m black $(PACKAGE) tests

lint: install-dev
	$(PYTHON) -m flake8 $(PACKAGE) tests --max-line-length=88 --extend-ignore=E203,W503

typecheck: install-dev
	$(PYTHON) -m mypy $(PACKAGE)

test: install-dev
	$(PYTHON) -m pytest tests/ -v

coverage: install-dev
	$(PYTHON) -m pytest tests/ --cov=$(PACKAGE) --cov-report=term-missing --cov-report=html --cov-fail-under=80
