# Project Structure Standards

Standard directory layout and required files for consistent project organization.

## General Principles

1. **Predictable locations** - Same file types in same places across projects
2. **Flat over nested** - Avoid deep directory hierarchies
3. **Separation of concerns** - Source, tests, config, and docs are distinct
4. **Convention over configuration** - Standard structures reduce setup

## Python Projects

### Directory Layout

```
project-name/
├── project_name/           # Package directory (snake_case)
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── cli.py             # CLI interface (if applicable)
│   └── ...                # Other modules
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Shared fixtures
│   ├── test_main.py
│   └── fixtures/          # Test data
│       └── README.md      # Document fixture purposes
├── .claude/                # Claude Code agents and skills
│   ├── skills/
│   └── agents/
├── .github/
│   └── workflows/         # CI/CD workflows
├── .work/                  # Working directory (gitignored)
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
├── pyproject.toml         # Package metadata (PEP 517/518)
└── MANIFEST.in            # Source distribution rules
```

### pyproject.toml Template

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "project-name"
version = "0.1.0"
description = "Brief description"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Author Name", email = "author@example.com"}]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "flake8>=6.0",
    "mypy>=1.0",
]

[project.scripts]
project-name = "project_name.cli:main"

[tool.black]
line-length = 88

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

## JavaScript/TypeScript Projects

### Directory Layout

```
project-name/
├── src/
│   ├── index.ts           # Entry point
│   ├── cli.ts             # CLI interface (if applicable)
│   └── ...
├── tests/
│   ├── setup.ts           # Test configuration
│   └── *.test.ts
├── dist/                   # Build output (gitignored)
├── .claude/                # Claude Code agents and skills
│   ├── skills/
│   └── agents/
├── .github/
│   └── workflows/
├── .work/                  # Working directory (gitignored)
├── .gitignore
├── .eslintrc.json
├── .prettierrc
├── LICENSE
├── Makefile               # Or use npm scripts
├── README.md
├── package.json
└── tsconfig.json
```

### package.json Scripts

```json
{
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/",
    "typecheck": "tsc --noEmit"
  }
}
```

## Go Projects

### Directory Layout

```
project-name/
├── cmd/
│   └── project-name/
│       └── main.go        # Entry point
├── internal/              # Private packages
│   └── ...
├── pkg/                   # Public packages (optional)
│   └── ...
├── .github/
│   └── workflows/
├── .gitignore
├── go.mod
├── go.sum
├── LICENSE
├── Makefile
└── README.md
```

## Required Files

All projects must include:

| File | Purpose |
|------|---------|
| `README.md` | Project overview and usage (see [README Format](readme-format.md)) |
| `LICENSE` | License terms |
| `.gitignore` | Version control exclusions |
| `Makefile` | Build automation (see [Makefile Standards](makefile.md)) |

## .gitignore Essentials

### Python

```gitignore
# Build artifacts
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/

# Virtual environments
venv/
.venv/
env/

# IDE
.idea/
.vscode/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Environment
.env
.env.local

# Working directory (agent output, drafts, temporary files)
.work/
```

### JavaScript/TypeScript

```gitignore
# Dependencies
node_modules/

# Build
dist/
build/
*.js.map

# IDE
.idea/
.vscode/
*.swp

# Testing
coverage/
.jest/

# Environment
.env
.env.local

# Working directory (agent output, drafts, temporary files)
.work/
```

### Working Directory

The `.work/` directory is for temporary files that should not be committed:

| Subdirectory | Purpose |
|--------------|---------|
| `.work/reviews/` | Code review and architecture review output |
| `.work/drafts/` | Work-in-progress documentation |
| `.work/scratch/` | Temporary exploration files |

This directory is always gitignored and can be safely deleted.

## Configuration File Placement

| File Type | Location | Example |
|-----------|----------|---------|
| Package metadata | Project root | `pyproject.toml`, `package.json` |
| Linter config | Project root | `.eslintrc.json`, `pyproject.toml` |
| Editor config | Project root | `.editorconfig`, `.prettierrc` |
| CI/CD workflows | `.github/workflows/` | `test.yml`, `lint.yml` |
| Docker files | Project root | `Dockerfile`, `docker-compose.yml` |
| Environment | Project root (gitignored) | `.env`, `.env.local` |

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| `src/` for Python packages | Package name as directory |
| Deeply nested modules | Flat module structure |
| Multiple config formats | Single source of truth (e.g., `pyproject.toml`) |
| Generated files in git | Generate in CI, add to `.gitignore` |
| Secrets in repository | Use environment variables or secret management |

## Industry References

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/)
- [Node.js Project Structure Best Practices](https://nodejs.org/en/docs/guides/)
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout)
