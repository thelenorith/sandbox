---
name: write-tests
description: Generate comprehensive tests for specified code. Use when new code is written or test coverage is needed.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Write, Edit
model: inherit
---

## Test Generation

Generate comprehensive tests for the specified code.

### Arguments

- `$ARGUMENTS` - Required: file path or function name to test

### Process

1. **Analyze Target Code**
   - Read the file or function to test
   - Identify public interfaces
   - Understand dependencies and side effects

2. **Identify Test Cases**

   **Happy Path**
   - Normal expected usage
   - Valid inputs produce correct outputs

   **Edge Cases**
   - Empty inputs (null, empty string, empty array)
   - Boundary values (0, -1, max int)
   - Single element collections

   **Error Cases**
   - Invalid inputs
   - Missing required parameters
   - Permission/access errors

   **Integration Points**
   - Mock external dependencies
   - Test interaction with other components

3. **Generate Tests**

   Follow project conventions:
   - Use existing test framework (pytest, jest, etc.)
   - Match existing test file naming (`test_*.py`, `*.test.ts`)
   - Use existing fixtures/utilities

4. **Test Quality Checklist**
   - [ ] Each test has a single assertion focus
   - [ ] Test names describe the scenario
   - [ ] Tests are independent (no shared state)
   - [ ] Mocks are minimal and focused
   - [ ] No testing of implementation details

### Output

Create or update test files following project structure:

```python
# Example pytest output
def test_function_returns_expected_value():
    """Function returns correct result for valid input."""
    result = function_under_test(valid_input)
    assert result == expected_output

def test_function_handles_empty_input():
    """Function handles empty input gracefully."""
    result = function_under_test("")
    assert result is None

def test_function_raises_on_invalid_input():
    """Function raises ValueError for invalid input."""
    with pytest.raises(ValueError):
        function_under_test(invalid_input)
```
