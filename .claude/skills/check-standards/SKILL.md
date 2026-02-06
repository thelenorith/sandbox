---
name: check-standards
description: Verify project follows work standards. Use to audit project structure and configuration.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(ls*), Bash(cat*), Bash(test*)
model: inherit
---

## Standards Compliance Check

Verify the project follows the work standards.

### Arguments

- `$ARGUMENTS` - Optional: specific standard to check (e.g., "naming", "testing")
- If no arguments, check all applicable standards

### Standards Reference

Check local `standards/` directory (synced from https://github.com/thelenorith/sandbox)

### Checklist

#### Project Structure
- [ ] README.md exists and follows format standards
- [ ] LICENSE file exists
- [ ] .gitignore exists with appropriate patterns
- [ ] Makefile exists with standard targets
- [ ] Source code in appropriate directory structure

#### Naming Conventions
- [ ] Repository name is lowercase with hyphens
- [ ] Package/module names follow language conventions
- [ ] No abbreviations without explanation

#### Build Automation (Makefile)
- [ ] `make` runs all checks by default
- [ ] `make help` shows available targets
- [ ] `make test` runs tests
- [ ] `make lint` runs linter
- [ ] `make format` formats code

#### Testing
- [ ] Tests directory exists
- [ ] Test files follow naming convention
- [ ] Coverage configuration present

#### CI/CD (if .github/workflows exists)
- [ ] Test workflow runs on push/PR
- [ ] Lint workflow runs on push/PR
- [ ] Workflows use Makefile targets

#### Documentation Projects
- [ ] `make markdown-lint` target exists
- [ ] `make links` target exists

### Output Format

```
## Standards Compliance Report

### Passing
- [x] README.md exists
- [x] Makefile has help target

### Failing
- [ ] Missing LICENSE file
- [ ] Makefile missing 'lint' target

### Recommendations
- Add LICENSE file (MIT recommended)
- Add lint target to Makefile

### Score: X/Y standards met
```

### Auto-Fix

If issues are found, offer to fix automatically:
- Create missing files from templates
- Add missing Makefile targets
- Update README structure
