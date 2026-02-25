---
name: review-pr
description: Review a GitHub pull request for code quality, correctness, and best practices. Use when the user asks to review a PR, check a pull request, or provide feedback on changes.
---

# PR Review Skill

Perform a thorough code review of a GitHub pull request.

## Steps

1. Identify the PR to review:
   - If `$ARGUMENTS` contains a number or URL, use that.
   - Otherwise, check if there's a PR for the current branch with `gh pr view`.
2. Gather PR context:
   - Run `gh pr view <number> --json title,body,baseRefName,headRefName,files,additions,deletions` for metadata.
   - Run `gh pr diff <number>` to get the full diff.
   - Read the PR description for stated intent.
3. Review the diff systematically:
   - **Correctness**: Does the code do what it claims? Are there logic errors?
   - **Security**: Are there injection risks, exposed secrets, or unsafe operations?
   - **Error handling**: Are failure cases handled? Are errors swallowed silently?
   - **Readability**: Is the code clear? Are names descriptive?
   - **Tests**: Are changes covered by tests? Are edge cases tested?
   - **Scope**: Does the PR stay focused? Are there unrelated changes?
4. If needed, read the full source files for context beyond the diff using the Read tool.
5. Present findings organized by severity:
   - **Must fix**: Bugs, security issues, data loss risks.
   - **Should fix**: Missing error handling, unclear logic, missing tests.
   - **Nit**: Style preferences, minor naming suggestions.

## Rules

- Be specific — reference file paths and line numbers.
- Suggest fixes, don't just point out problems.
- Acknowledge what's done well.
- If the PR is clean, say so. Don't invent issues.

## Arguments

`$ARGUMENTS` should be a PR number, URL, or branch name.
