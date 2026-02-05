---
name: security-scan
description: Scan code for security vulnerabilities. Use before commits or deployments.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git*)
model: inherit
---

## Security Scan

Scan code for common security vulnerabilities and misconfigurations.

### Arguments

- `$ARGUMENTS` - Optional: specific files or directories to scan
- If no arguments, scan entire project

### Vulnerability Categories

#### Secrets and Credentials
Search for hardcoded secrets:
- API keys, tokens, passwords
- Private keys, certificates
- Database connection strings
- AWS/GCP/Azure credentials

Patterns to search:
```
password\s*=
api_key\s*=
secret\s*=
token\s*=
-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----
AKIA[0-9A-Z]{16}
```

#### Injection Vulnerabilities
- SQL injection (string concatenation in queries)
- Command injection (shell commands with user input)
- XSS (unescaped user input in HTML)
- Path traversal (user input in file paths)

#### Authentication/Authorization
- Missing authentication checks
- Weak password requirements
- Session management issues
- Insecure token storage

#### Configuration
- Debug mode enabled in production
- Verbose error messages exposed
- CORS misconfiguration
- Missing security headers

#### Dependencies
- Check for lockfile (package-lock.json, poetry.lock, etc.)
- Note: Full dependency audit requires external tools

### Process

1. **Scan for Secrets**
   ```bash
   grep -rn "password\s*=" --include="*.py" --include="*.js" --include="*.ts" .
   grep -rn "api_key\s*=" --include="*.py" --include="*.js" --include="*.ts" .
   ```

2. **Check Sensitive Files**
   - .env files should be in .gitignore
   - No credentials in config files
   - No private keys committed

3. **Review Code Patterns**
   - Look for string concatenation in SQL
   - Check for eval() or exec() usage
   - Verify input validation

4. **Check Configuration**
   - DEBUG settings
   - Error handling exposure
   - HTTPS enforcement

### Output Format

```
## Security Scan Report

### Critical (Immediate Action Required)
- [CRITICAL] Hardcoded API key found in config.py:42
- [CRITICAL] SQL injection vulnerability in db.py:128

### High Risk
- [HIGH] .env file not in .gitignore
- [HIGH] Debug mode enabled in settings

### Medium Risk
- [MEDIUM] No input validation on user endpoint
- [MEDIUM] Missing rate limiting

### Low Risk
- [LOW] Verbose error messages in development

### Recommendations
1. Remove hardcoded credentials, use environment variables
2. Add .env to .gitignore
3. Disable debug mode for production

### Files Scanned: X
### Issues Found: Y (X critical, Y high, Z medium)
```

### Important Notes

- This is a basic scan, not a replacement for professional security audit
- Always use dedicated security tools (Snyk, Dependabot, etc.) in CI
- Secrets found should be rotated immediately, even after removal
