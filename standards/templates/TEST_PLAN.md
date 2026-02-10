# Test Plan

> This document describes the testing strategy for this project. It serves as the single source of truth for testing decisions and rationale.

## Overview

**Project:** <project-name>
**Primary functionality:** <one sentence description>

## Testing Philosophy

This project follows the [Testing Standards](../testing.md).

Key testing principles for this project:

- <!-- principle 1 -->
- <!-- principle 2 -->

## Test Categories

### Unit Tests

Tests for isolated functions with mocked dependencies.

| Module | Function | Test Coverage | Notes |
|--------|----------|---------------|-------|
| `<module>.py` | `function_name()` | Core logic paths | <!-- any special considerations --> |

### Integration Tests

Tests for multiple components working together.

| Workflow | Components | Test Coverage | Notes |
|----------|------------|---------------|-------|
| <!-- workflow name --> | <!-- modules involved --> | <!-- what's tested --> | <!-- any special considerations --> |

## Untested Areas

| Area | Reason Not Tested |
|------|-------------------|
| <!-- area --> | <!-- rationale --> |

## Bug Fix Testing Protocol

All bug fixes to existing functionality **must** follow TDD:

1. Write a failing test that exposes the bug
2. Verify the test fails before implementing the fix
3. Implement the fix
4. Verify the test passes
5. Verify reverting the fix causes the test to fail again
6. Commit test and fix together with issue reference

### Regression Tests

| Issue | Test | Description |
|-------|------|-------------|
| <!-- #123 --> | `test_function_issue_123` | <!-- what bug was fixed --> |

## Coverage Goals

**Target:** 80%+ line coverage

**Philosophy:** Coverage measures completeness, not quality. A test that executes code without meaningful assertions provides no value. Focus on:

- Testing behavior, not implementation details
- Covering edge cases and error conditions
- Ensuring assertions verify expected outcomes

## Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test
pytest tests/test_module.py::TestClass::test_function
```

## Test Data

Test data is:
- Generated programmatically in fixtures where possible
- Stored in `tests/fixtures/` when static files are needed
- Documented in `tests/fixtures/README.md`

**Important:** Keep test data small (< 100KB) or generate it programmatically.

## Maintenance

When modifying this project:

1. **Adding features**: Add tests for new functionality
2. **Fixing bugs**: Follow TDD protocol above (test first, then fix)
3. **Refactoring**: Existing tests should pass without modification (behavior unchanged)
4. **Removing features**: Remove associated tests

## Changelog

| Date | Change | Rationale |
|------|--------|-----------|
| YYYY-MM-DD | Initial test plan | Project creation |
