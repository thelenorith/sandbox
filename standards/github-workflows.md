# GitHub Workflows Standards

CI/CD pipeline configuration for consistent automated testing and deployment.

## General Principles

1. **Fast feedback** - Developers should know quickly if their changes break anything
2. **Consistency** - Same checks locally and in CI
3. **Reliability** - Workflows should be deterministic and not flaky
4. **Security** - Minimize attack surface, use least-privilege

## Required Workflows

All projects should have these CI workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| Test | push, PR | Run test suite across supported versions |
| Lint | push, PR | Code quality analysis |
| Typecheck | push, PR | Static type verification |
| Format Check | push, PR | Ensure consistent formatting |
| Coverage | push, PR | Verify test coverage meets threshold |

### Documentation Workflows

For documentation-heavy projects (like this standards repository) or projects with extensive markdown documentation, also include:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| Markdown Lint | push, PR | Validate markdown formatting |
| Link Check | push, PR | Verify all links are valid |

## Workflow Templates

Use templates from [templates/workflows/](templates/workflows/) instead of copying inline code. This follows DRY principles and ensures templates stay current.

### Available Templates

| Template | Purpose | Copy To |
|----------|---------|---------|
| [test.yml](templates/workflows/test.yml) | Run tests across Python versions | `.github/workflows/test.yml` |
| [lint.yml](templates/workflows/lint.yml) | Run linter | `.github/workflows/lint.yml` |
| [typecheck.yml](templates/workflows/typecheck.yml) | Run type checker | `.github/workflows/typecheck.yml` |
| [format.yml](templates/workflows/format.yml) | Check code formatting | `.github/workflows/format.yml` |
| [coverage.yml](templates/workflows/coverage.yml) | Coverage with PR comments | `.github/workflows/coverage.yml` |

### Using Templates

Copy templates to your project:

```bash
mkdir -p .github/workflows
cp standards/templates/workflows/*.yml .github/workflows/
```

Or download from this repository:

```bash
mkdir -p .github/workflows
for workflow in test lint typecheck format coverage; do
  curl -sL https://raw.githubusercontent.com/thelenorith/sandbox/main/standards/templates/workflows/${workflow}.yml \
    -o .github/workflows/${workflow}.yml
done
```

### Template Highlights

**test.yml** - Matrix testing across Python 3.10, 3.11, 3.12

**coverage.yml** - Includes:
- 80% coverage threshold enforcement
- Automatic PR comment when coverage fails
- Clear pass/fail status

**format.yml** - Includes:
- Runs formatter and checks for changes
- Reports which files need formatting
- Provides actionable instructions

### Documentation Workflows

For documentation-heavy projects, add markdown linting and link checking. These are simpler and shown inline:

**Markdown Lint** (`.github/workflows/markdown-lint.yml`):
```yaml
name: Markdown Lint
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: make markdown-lint
```

**Link Check** (`.github/workflows/links.yml`):
```yaml
name: Validate Links
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: make links
```

### Combined Workflow (Alternative)

For smaller projects, combine all checks:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: make install-dev
      - run: make format-check
      - run: make lint
      - run: make typecheck

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: make install-dev
      - run: make coverage
```

## JavaScript/TypeScript Workflows

### Test Workflow (Node.js)

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['18', '20', '22']

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test
```

## Conventions

### Version Support

| Language | Versions to Test | Single-Version Jobs |
|----------|------------------|---------------------|
| Python | 3.10 through latest | Use 3.12 |
| Node.js | LTS versions (18, 20, 22) | Use latest LTS |
| Go | Last 2 minor versions | Use latest |

### Action Versions

Use current major versions with explicit version pinning:

```yaml
# Good: Major version pinning
- uses: actions/checkout@v4
- uses: actions/setup-python@v5

# Avoid: No version or SHA pinning for untrusted actions
- uses: actions/checkout           # Missing version
- uses: some-org/action@abc123...  # SHA for untrusted actions
```

### Caching

Enable dependency caching for faster builds:

```yaml
# Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'

# Node.js
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

### Workflow Naming

| Convention | Example |
|------------|---------|
| Use title case | `Test`, `Lint`, `Format Check` |
| Be specific | `Test Python 3.12` vs just `Test` |
| Match file name | `test.yml` -> `name: Test` |

## Branch Protection

Configure branch protection rules to require CI:

| Setting | Recommended Value |
|---------|-------------------|
| Require status checks | Yes |
| Required checks | Test, Lint, Typecheck, Format Check |
| Require branches to be up to date | Yes |
| Require PR before merging | Yes |
| Dismiss stale reviews | Yes |

## Secrets and Security

### Secret Management

```yaml
# Reference secrets securely
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: ./deploy.sh

# Never echo secrets
- name: Bad example
  run: echo ${{ secrets.API_KEY }}  # NEVER DO THIS
```

### Permissions

Use least-privilege permissions:

```yaml
permissions:
  contents: read
  pull-requests: write  # Only if needed for PR comments

jobs:
  test:
    runs-on: ubuntu-latest
    # Job-level permissions can be more restrictive
    permissions:
      contents: read
```

## Release Workflows

### Semantic Release

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

### PyPI Publishing

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For trusted publishing

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Build
        run: |
          pip install build
          python -m build

      - name: Publish
        uses: pypa/gh-action-pypi-publish@release/v1
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Embedding commands in workflows | Use Makefile targets |
| Duplicating workflow logic | Use reusable workflows or composite actions |
| Hardcoded versions everywhere | Use matrix strategy |
| Running all checks sequentially | Parallelize independent jobs |
| Missing `fail-fast: false` in matrix | Allow all versions to complete |
| No caching | Always cache dependencies |
| Overly permissive permissions | Use least-privilege |

## Debugging Workflows

### Enable Debug Logging

Set secret `ACTIONS_RUNNER_DEBUG` to `true` for verbose logs.

### Local Testing

Use [act](https://github.com/nektos/act) to run workflows locally:

```bash
# Run all workflows
act

# Run specific workflow
act -W .github/workflows/test.yml

# Run with specific event
act pull_request
```

## Industry References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
