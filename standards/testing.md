# Testing Standards

Unit testing conventions for consistent, reliable test suites.

## General Principles

1. **Tests are documentation** - Tests demonstrate how code should be used
2. **Isolation** - Tests should not depend on each other or external state
3. **Speed** - Tests should run quickly to enable frequent execution
4. **Determinism** - Same inputs produce same results every time

## Test Organization

### Directory Structure

```
project/
├── src/              # or package_name/
│   ├── module_a.py
│   └── module_b.py
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    ├── test_module_a.py     # Tests for module_a
    ├── test_module_b.py     # Tests for module_b
    └── fixtures/            # Test data files
        └── README.md        # Document fixture purposes
```

### File Naming

| Pattern | Example | Use |
|---------|---------|-----|
| `test_<module>.py` | `test_parser.py` | Python (pytest) |
| `<module>.test.ts` | `parser.test.ts` | TypeScript (Jest) |
| `<module>_test.go` | `parser_test.go` | Go |

### Test Function Naming

| Pattern | Example |
|---------|---------|
| `test_<function>_<scenario>` | `test_parse_valid_input` |
| `test_<function>_<expected_result>` | `test_parse_returns_empty_on_null` |
| `test_<function>_raises_<error>` | `test_parse_raises_on_invalid_json` |

### Test Class Naming

| Pattern | Example |
|---------|---------|
| `Test<Class>` | `TestUserService` |
| `Test<Feature>` | `TestAuthentication` |

## Test Isolation

Tests must be completely independent:

| Requirement | Implementation |
|-------------|----------------|
| No real filesystem access | Use `tmp_path` (pytest) or temp directories |
| No network calls | Mock external APIs |
| No mutation of source files | Work with copies in temp directories |
| No persistent state | Each test starts clean |
| Automatic cleanup | Use fixtures with proper teardown |

### Filesystem Isolation (Python)

```python
def test_file_processing(tmp_path):
    """Test using pytest's tmp_path fixture."""
    # Create test file in temporary directory
    test_file = tmp_path / "input.txt"
    test_file.write_text("test content")

    # Run function under test
    result = process_file(test_file)

    # Assert results
    assert result.success
    # tmp_path is automatically cleaned up
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    """Test with mocked external API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}

    with patch("requests.get", return_value=mock_response):
        result = fetch_status()
        assert result == "ok"
```

## Fixtures

### Fixture Guidelines

| Guideline | Rationale |
|-----------|-----------|
| Generate test data programmatically | Avoid large binary files in repository |
| Keep fixtures minimal | Test only what's needed |
| Document fixture purposes | Add README in fixtures directory |
| Use factory functions | Create data with sensible defaults |

### Shared Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_config():
    """Provide a minimal valid configuration."""
    return {
        "name": "test",
        "version": "1.0.0",
        "enabled": True,
    }

@pytest.fixture
def temp_project(tmp_path):
    """Create a minimal project structure for testing."""
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
    return tmp_path
```

### Factory Fixtures

```python
@pytest.fixture
def user_factory():
    """Factory for creating test users with defaults."""
    def _create_user(
        name: str = "Test User",
        email: str = "test@example.com",
        role: str = "user",
    ):
        return User(name=name, email=email, role=role)
    return _create_user

def test_admin_permissions(user_factory):
    admin = user_factory(role="admin")
    assert admin.can_delete_users()
```

## Coverage

### Coverage Targets

| Level | Target | Notes |
|-------|--------|-------|
| Line coverage | 80%+ | Minimum acceptable |
| Branch coverage | 70%+ | For complex logic |
| Critical paths | 100% | Authentication, payments, data integrity |

### What to Test

| Test | Priority |
|------|----------|
| Public functions | High |
| Edge cases | High |
| Error conditions | High |
| Boundary values | Medium |
| Integration points | Medium |

### What NOT to Test

| Avoid Testing | Rationale |
|---------------|-----------|
| Private functions directly | Test through public interface |
| Third-party library behavior | Trust library tests |
| Simple getters/setters | No meaningful logic |
| Framework code | Test your code, not the framework |

## Test Patterns

### Arrange-Act-Assert (AAA)

```python
def test_calculate_total():
    # Arrange
    items = [
        Item(price=10.00, quantity=2),
        Item(price=5.00, quantity=1),
    ]

    # Act
    total = calculate_total(items)

    # Assert
    assert total == 25.00
```

### Given-When-Then (BDD Style)

```python
def test_user_login():
    # Given a registered user
    user = create_user(email="test@example.com", password="secret")

    # When they provide correct credentials
    result = authenticate(email="test@example.com", password="secret")

    # Then they are authenticated
    assert result.success
    assert result.user_id == user.id
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected

@pytest.mark.parametrize("invalid_input", [None, [], {}])
def test_uppercase_raises_on_invalid_type(invalid_input):
    with pytest.raises(TypeError):
        uppercase(invalid_input)
```

### Testing Exceptions

```python
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError) as exc_info:
        divide(10, 0)
    assert "division by zero" in str(exc_info.value)
```

## Test Categories

### Unit Tests

| Characteristic | Description |
|----------------|-------------|
| Scope | Single function or class |
| Dependencies | Mocked |
| Speed | < 100ms per test |
| Isolation | Complete |

### Integration Tests

| Characteristic | Description |
|----------------|-------------|
| Scope | Multiple components working together |
| Dependencies | Real or stubbed services |
| Speed | May be slower |
| Isolation | May share test database |

### End-to-End Tests

| Characteristic | Description |
|----------------|-------------|
| Scope | Full system |
| Dependencies | Real services |
| Speed | Slowest |
| Isolation | Dedicated test environment |

## Test Configuration

### pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

### Jest Configuration (jest.config.js)

```javascript
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts'],
  coverageThreshold: {
    global: {
      lines: 80,
      branches: 70,
    },
  },
};
```

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Tests depend on order | Flaky, hard to debug | Make tests independent |
| Shared mutable state | Tests affect each other | Use fixtures with fresh state |
| Testing implementation | Brittle tests | Test behavior, not internals |
| Too many assertions | Unclear failure cause | One concept per test |
| No assertion messages | Hard to debug | Add context to assertions |
| Ignoring flaky tests | Hidden reliability issues | Fix or quarantine flaky tests |
| Copy-paste test code | Maintenance burden | Use fixtures and helpers |

## Running Tests

### Local Development

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/test_parser.py

# Run specific test
pytest tests/test_parser.py::test_parse_valid_input

# Run tests matching pattern
pytest -k "parse"

# Skip slow tests
pytest -m "not slow"
```

### CI Integration

See [GitHub Workflows](github-workflows.md) for CI configuration.

## Industry References

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Google Testing Blog](https://testing.googleblog.com/)
- [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [FIRST Principles](https://pragprog.com/titles/utc2/pragmatic-unit-testing-in-c-with-nunit/)
