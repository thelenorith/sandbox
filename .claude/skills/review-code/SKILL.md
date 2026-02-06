---
name: review-code
description: Review code for quality, security, and best practices. Use when code changes are made or when explicitly requested.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git diff*), Bash(git log*), Bash(git show*)
model: inherit
---

## Code Review

Review code changes for quality, security, and adherence to best practices.

**Note**: The `code-reviewer` agent also performs proactive reviews automatically after code changes. This skill is for manual on-demand reviews.

### Arguments

- `$ARGUMENTS` - Optional: specific files or commit range to review
- If no arguments, review uncommitted changes

### Process

1. **Identify Changes**
   ```bash
   # Uncommitted changes
   git diff --name-only
   git diff

   # Or specific commit/range if provided
   git show $ARGUMENTS
   ```

2. **Review Checklist**

   **Security**
   - [ ] No hardcoded secrets, API keys, or credentials
   - [ ] Input validation on external data
   - [ ] No SQL injection vulnerabilities
   - [ ] No XSS vulnerabilities
   - [ ] Proper authentication/authorization checks

   **Code Quality**
   - [ ] Clear, descriptive variable and function names
   - [ ] No code duplication (DRY)
   - [ ] Single responsibility principle
   - [ ] Proper error handling
   - [ ] No unused imports or dead code

   **Testing**
   - [ ] Tests added for new functionality
   - [ ] Edge cases covered
   - [ ] Tests are meaningful, not just for coverage

   **Performance**
   - [ ] No N+1 query patterns
   - [ ] Efficient algorithms for data size
   - [ ] No unnecessary loops or iterations

   **Documentation**
   - [ ] Public APIs documented
   - [ ] Complex logic explained
   - [ ] README updated if needed

3. **Provide Feedback**

   Organize by priority:
   - **Critical**: Must fix before merge (security, bugs)
   - **Warning**: Should fix (code quality, performance)
   - **Suggestion**: Nice to have (style, minor improvements)

### Output Format

```
## Code Review Summary

### Critical Issues
- [file:line] Description of critical issue

### Warnings
- [file:line] Description of warning

### Suggestions
- [file:line] Description of suggestion

### Positive Notes
- What was done well
```
