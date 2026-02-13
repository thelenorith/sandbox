# Code Style Standards

Code style consistency improves readability, reduces bugs, and makes code reviews more efficient.

## Guiding Principles

1. **Adopt established standards** - Use industry-standard style guides rather than inventing custom conventions
2. **Automate enforcement** - Configure formatters and linters to catch violations automatically
3. **Consistency over preference** - Team consistency matters more than individual preferences
4. **Explicit over implicit** - Code should clearly communicate intent

## Function Calls: Named Parameters

**Prefer explicit named parameters over positional parameters when calling functions.**

### Rationale

Positional parameters are error-prone:
- Parameter order changes can silently break code
- Wrong values can be passed to wrong parameters without type checking
- Code is harder to understand without reading function signature

### Example Bug

This bug pattern occurs in production across languages:

```python
# Function signature
def move_file(from_file: str, to_file: str, debug: bool = False, dryrun: bool = False):
    ...

# WRONG: dryrun passed as 3rd positional argument maps to debug parameter
move_file(src, dest, dry_run)  # dry_run → debug, dryrun stays False
# Result: Files actually moved with debug output!

# CORRECT: Named parameter ensures correct mapping
move_file(src, dest, dryrun=dry_run)
```

### Guidelines

| Parameter Type | Guidance | Example |
|---------------|----------|---------|
| 1-2 required params | Positional acceptable | `len(items)`, `open(path, mode)` |
| Optional parameters | Must use named | `func(x, timeout=30)` |
| Boolean flags | Always use named | `process(data, verbose=True)` |
| 3+ parameters | Prefer named | `create_user(name=n, email=e, role=r)` |

### Language Examples

**Python:**
```python
# WRONG
process_data(data, True, False, True)

# CORRECT
process_data(data, validate=True, strict=False, verbose=True)
```

**JavaScript/TypeScript:**
```javascript
// WRONG
createUser('alice', true, false, 30)

// CORRECT - use options object
createUser('alice', { admin: true, verified: false, timeout: 30 })
```

**Go:**
```go
// WRONG - unclear boolean flags
NewClient("localhost", true, false, 30)

// CORRECT - use options pattern
NewClient("localhost", WithTLS(true), WithRetry(false), WithTimeout(30))
```

### Exceptions

Positional parameters are acceptable when:
- Only 1-2 required parameters with clear, unambiguous meaning
- Very common functions where positional usage is idiomatic (`print()`, `len()`)
- All parameters are required with no defaults and clear ordering

## Language-Specific Style Guides

Adopt the canonical style guide for each language. Don't reinvent conventions.

### Python

- **Style guide**: [PEP 8](https://peps.python.org/pep-0008/)
- **Formatter**: [Black](https://black.readthedocs.io/) (opinionated, zero-config)
- **Linter**: [Ruff](https://docs.astral.sh/ruff/) (fast, comprehensive)
- **Type checking**: [mypy](https://mypy.readthedocs.io/) or [pyright](https://github.com/microsoft/pyright)

```toml
# pyproject.toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP"]
```

### JavaScript/TypeScript

- **Style guide**: [Airbnb](https://github.com/airbnb/javascript) or [StandardJS](https://standardjs.com/)
- **Formatter**: [Prettier](https://prettier.io/)
- **Linter**: [ESLint](https://eslint.org/)
- **Type checking**: TypeScript strict mode

```json
{
  "prettier": {
    "semi": true,
    "singleQuote": true,
    "printWidth": 100
  }
}
```

### Go

- **Style guide**: [Effective Go](https://go.dev/doc/effective_go) + [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- **Formatter**: `gofmt` (built-in, non-negotiable)
- **Linter**: [golangci-lint](https://golangci-lint.run/)

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
```

### Rust

- **Style guide**: [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/)
- **Formatter**: `rustfmt` (built-in)
- **Linter**: `clippy` (built-in)

### Java/Kotlin

- **Style guide**: [Google Java Style](https://google.github.io/styleguide/javaguide.html) or [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)
- **Formatter**: [google-java-format](https://github.com/google/google-java-format) or [ktlint](https://ktlint.github.io/)

## Automation

### Pre-commit Hooks

Configure formatters and linters to run before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]
```

### CI Integration

See [GitHub Workflows](github-workflows.md) for CI configuration. At minimum:
- Run formatters in check mode
- Run linters
- Run type checkers (for typed languages)

### Editor Integration

Configure editors to format on save:
- VS Code: `editor.formatOnSave: true`
- JetBrains: Enable "Reformat code" in commit options
- Vim/Neovim: Use `null-ls` or language server formatting

## Code Review Checklist

When reviewing code style:

- [ ] Follows language style guide
- [ ] Named parameters used for optional/boolean arguments
- [ ] Consistent formatting throughout
- [ ] No linter warnings suppressed without justification
- [ ] Type hints/annotations present (where applicable)

## Anti-Patterns

### Suppressing Linter Warnings

```python
# BAD: Blanket suppression
# noqa

# ACCEPTABLE: Targeted suppression with justification
# noqa: E501 - URL cannot be broken across lines
```

### Inconsistent Formatting

Don't mix styles within a codebase. If adopting a new formatter, apply it to the entire codebase in a single commit.

### Over-customizing Rules

Stick to default configurations when possible. Customizations create maintenance burden and onboarding friction.

## References

- [PEP 8 - Python Style Guide](https://peps.python.org/pep-0008/)
- [Google Style Guides](https://google.github.io/styleguide/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Effective Go](https://go.dev/doc/effective_go)
