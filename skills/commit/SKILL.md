---
name: commit
description: Create a well-structured git commit using conventional commit format. Use when the user asks to commit changes, create a commit, or save their work.
---

# Commit Skill

Create a git commit following conventional commit conventions.

## Steps

1. Run `git status` to see all changed and untracked files. Never use `-uall`.
2. Run `git diff` and `git diff --staged` to understand what changed.
3. Run `git log --oneline -5` to see recent commit style for this repo.
4. Analyze the changes and draft a commit message:
   - Use conventional commit format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`
   - Scope is optional but encouraged when changes are focused on a specific area.
   - The description should explain **why**, not just **what**.
   - Add a body for non-trivial changes, separated by a blank line.
5. Stage the relevant files. Prefer `git add <specific-files>` over `git add .` or `git add -A`.
   - Never stage files that likely contain secrets (`.env`, credentials, tokens).
   - If unsure about a file, ask the user.
6. Create the commit. Use a HEREDOC for multi-line messages.
7. Run `git status` to confirm the commit succeeded.

## Rules

- Never amend a previous commit unless the user explicitly asks.
- Never use `--no-verify` unless the user explicitly asks.
- If a pre-commit hook fails, fix the issue and create a NEW commit (do not amend).
- If there are no changes to commit, tell the user — do not create an empty commit.
- Present the draft commit message to the user before committing.

## Arguments

If `$ARGUMENTS` is provided, use it as guidance for the commit message or to identify which files to include.
