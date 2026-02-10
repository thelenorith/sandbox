# Makefile Standards

Build automation conventions for consistent project workflows.

## General Principles

1. **Self-documenting** - Running `make` without arguments shows available targets
2. **Idempotent** - Running a target multiple times produces the same result
3. **Fast feedback** - Common tasks should be quick to execute
4. **Portable** - Avoid platform-specific commands without alternatives

## Default Target

The default target should run all validation steps:

```makefile
.PHONY: all
all: format lint typecheck test  ## Run all checks (default)
```

Running `make` with no arguments executes `all`, ensuring code quality before commits.

## Required Targets

All projects should include these standard targets:

| Target | Purpose |
|--------|---------|
| `all` | Run all validation (default) |
| `install` | Install production dependencies |
| `install-dev` | Install development dependencies |
| `clean` | Remove build artifacts |
| `format` | Format code |
| `lint` | Run linter |
| `typecheck` | Run type checker |
| `test` | Run tests |
| `coverage` | Run tests with coverage |
| `build` | Build distributable package |
| `help` | Show available targets |

### Documentation Targets

Documentation-heavy projects should also include:

| Target | Purpose |
|--------|---------|
| `markdown-lint` | Lint markdown files for formatting |
| `links` | Validate markdown links |

## Templates

Use templates from [templates/](templates/) instead of copying inline code:

| Template | Purpose |
|----------|---------|
| [Makefile](templates/Makefile) | Python project Makefile |

## Template (Python)

See [templates/Makefile](templates/Makefile) for a ready-to-use template. Replace `<package_name>` with your package name.

Key structure:

```makefile
PYTHON ?= python3
PACKAGE = <package_name>

.PHONY: all install install-dev clean format lint typecheck test coverage build help

all: format lint typecheck test  ## Run all checks (default)

install:  ## Install production dependencies
	$(PYTHON) -m pip install -e .

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install -e ".[dev]"

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

coverage: install-dev  ## Run tests with coverage
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=term-missing --cov-fail-under=80 tests/

build: clean  ## Build distribution packages
	$(PYTHON) -m build

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
```

## Template (JavaScript/TypeScript)

```makefile
.PHONY: all install install-dev clean format lint typecheck test coverage build help

all: format lint typecheck test  ## Run all checks (default)

install:  ## Install production dependencies
	npm ci --production

install-dev:  ## Install all dependencies
	npm ci

clean:  ## Remove build artifacts
	rm -rf dist/ node_modules/.cache/ coverage/ || true

format: install-dev  ## Format code with prettier
	npm run format

format-check: install-dev  ## Check formatting without changes
	npm run format -- --check

lint: install-dev  ## Run eslint
	npm run lint

typecheck: install-dev  ## Run TypeScript compiler
	npm run typecheck

test: install-dev  ## Run tests
	npm test

coverage: install-dev  ## Run tests with coverage
	npm run test -- --coverage

build: install-dev  ## Build for production
	npm run build

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
```

## Template (Documentation)

For documentation-only projects or to add to existing templates:

```makefile
PYTHON ?= python3

.PHONY: all check install-dev markdown-lint links help

all: check  ## Run all checks (default)

check: links markdown-lint  ## Run all validation

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install --quiet pymarkdown-lnt linkcheckmd

markdown-lint: install-dev  ## Lint markdown files
	$(PYTHON) -m pymarkdown --disable-rules MD013,MD024,MD031,MD036 scan .

links: install-dev  ## Validate markdown links
	$(PYTHON) -m linkcheck --no-status --no-warnings *.md **/*.md

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
```

### Disabled Markdown Rules

| Rule | Reason |
|------|--------|
| MD013 | Line length - impractical for prose and tables |
| MD024 | Duplicate headings - valid in different sections |
| MD031 | Fenced code blocks - conflicts with some valid patterns |
| MD036 | Emphasis as heading - intentional stylistic choice |

## Conventions

### Variables

Use variables for configurable values:

```makefile
# Use variables instead of hardcoded values
PYTHON ?= python3         # Allow override: make PYTHON=python3.11 test
PACKAGE = my_package      # Package name
COVERAGE_MIN = 80         # Minimum coverage threshold
```

### Dependencies

Quality-focused targets should depend on `install-dev`:

```makefile
format: install-dev  ## Ensures dev dependencies are installed first
	$(PYTHON) -m black $(PACKAGE)
```

### Phony Targets

Declare all non-file targets as `.PHONY`:

```makefile
.PHONY: all install clean test
```

### Silent Failures for Cleanup

Use `|| true` for cleanup operations that may fail:

```makefile
clean:
	rm -rf build/ dist/ || true
	find . -name "*.pyc" -delete 2>/dev/null || true
```

### Self-Documenting Help

Add `## Description` comments for automatic help generation:

```makefile
test:  ## Run the test suite
	pytest tests/

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
```

## CI Integration

Makefile targets should be used in CI workflows:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: make install-dev
      - run: make test
```

See [GitHub Workflows](github-workflows.md) for complete CI configuration.

## Tool Configuration

### Black (Python Formatter)

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py310']
```

### Flake8 (Python Linter)

```ini
# .flake8 or setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
per-file-ignores =
    __init__.py: F401
```

### ESLint (JavaScript/TypeScript)

```json
{
  "extends": ["eslint:recommended"],
  "rules": {
    "no-unused-vars": "error"
  }
}
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Complex shell logic in Makefile | Move to scripts or Python |
| Platform-specific commands | Use portable alternatives or conditionals |
| Hardcoded paths | Use variables |
| Modifying git state | Handle in CI workflows, not Makefile |
| Targets without `.PHONY` | Declare all non-file targets |
| Missing `install-dev` dependency | Always ensure dependencies first |
| Silent failures for non-cleanup | Only use `|| true` for cleanup |

## Platform Compatibility

For cross-platform support, use conditionals:

```makefile
ifeq ($(OS),Windows_NT)
    RM = del /Q
    RMDIR = rmdir /S /Q
else
    RM = rm -f
    RMDIR = rm -rf
endif

clean:
	$(RMDIR) build dist
```

## Advanced Patterns

### Parallel Execution

```makefile
# Run independent checks in parallel
check: install-dev
	$(MAKE) -j3 lint typecheck test
```

### Watching for Changes

```makefile
watch-test:  ## Run tests on file changes
	watchmedo shell-command \
		--patterns="*.py" \
		--recursive \
		--command='make test'
```

### Docker Integration

```makefile
docker-build:  ## Build Docker image
	docker build -t $(IMAGE_NAME):$(VERSION) .

docker-test:  ## Run tests in Docker
	docker run --rm $(IMAGE_NAME):$(VERSION) make test
```

## Industry References

- [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)
- [Makefile Tutorial](https://makefiletutorial.com/)
- [Self-Documenting Makefiles](https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html)
