PYTHON ?= python3

.PHONY: all check install-dev markdown-lint links help

all: check  ## Run all checks (default)

check: links markdown-lint  ## Run all validation

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install --quiet pymarkdown-lnt linkcheckmd

markdown-lint: install-dev  ## Lint markdown files
	$(PYTHON) -m pymarkdown --disable-rules MD013,MD024,MD031,MD036 scan .

links: install-dev  ## Validate markdown links
	$(PYTHON) -m linkcheck --no-status --no-warnings *.md standards/*.md

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
