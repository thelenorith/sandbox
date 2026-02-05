PYTHON ?= python3
STANDARDS_REPO ?= https://github.com/thelenorith/sandbox

.PHONY: all check install-dev markdown-lint links sync-agents help

all: check  ## Run all checks (default)

check: links markdown-lint  ## Run all validation

install-dev:  ## Install development dependencies
	$(PYTHON) -m pip install --quiet pymarkdown-lnt linkcheckmd

markdown-lint: install-dev  ## Lint markdown files
	$(PYTHON) -m pymarkdown --disable-rules MD013,MD024,MD031,MD036 scan .

links: install-dev  ## Validate markdown links
	$(PYTHON) -m linkcheck --no-status --no-warnings *.md standards/*.md

sync-agents:  ## Sync agents and skills from standards repo
	@echo "Syncing agents from $(STANDARDS_REPO)..."
	@mkdir -p .claude/skills .claude/agents
	@rm -rf /tmp/work-standards-sync
	@git clone --depth 1 --filter=blob:none --sparse $(STANDARDS_REPO) /tmp/work-standards-sync 2>/dev/null
	@cd /tmp/work-standards-sync && git sparse-checkout set .claude
	@cp -r /tmp/work-standards-sync/.claude/skills/* .claude/skills/ 2>/dev/null || true
	@cp -r /tmp/work-standards-sync/.claude/agents/* .claude/agents/ 2>/dev/null || true
	@rm -rf /tmp/work-standards-sync
	@echo "Synced skills:"
	@ls -1 .claude/skills/ 2>/dev/null || echo "  (none)"
	@echo "Synced agents:"
	@ls -1 .claude/agents/ 2>/dev/null || echo "  (none)"

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all
