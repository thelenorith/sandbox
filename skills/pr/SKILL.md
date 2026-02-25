---
name: pr
description: Create a GitHub pull request with a structured description. Use when the user asks to create a PR, open a pull request, or submit their changes for review.
---

# PR Creation Skill

Create a GitHub pull request with a well-structured title and description.

## Steps

1. Run `git status` to check for uncommitted changes. If there are uncommitted changes, ask the user if they want to commit first.
2. Identify the current branch and base branch:
   - Run `git branch --show-current` to get the current branch.
   - The base branch is typically `main` or `master`. Check with `git remote show origin` if unsure.
3. Review all commits that will be in the PR:
   - Run `git log --oneline <base>..HEAD` to see the commit history.
   - Run `git diff <base>...HEAD` to see the full diff.
4. Check if the branch is pushed to remote:
   - If not, push with `git push -u origin <branch-name>`.
5. Draft the PR:
   - **Title**: Short (under 70 chars), descriptive of the overall change.
   - **Body**: Use the format below.
6. Create the PR using `gh pr create`.

## PR Body Format

Use a HEREDOC to pass the body:

```
gh pr create --title "the title" --body "$(cat <<'EOF'
## Summary
- Bullet points summarizing what changed and why

## Test plan
- [ ] How to verify the changes work

EOF
)"
```

## Rules

- Never push to `main` or `master` directly.
- If `$ARGUMENTS` contains a PR number or URL, this is likely a request to update an existing PR — check with the user.
- Always show the draft title and body to the user before creating.
- If the diff is large, summarize by area of change rather than listing every file.

## Arguments

If `$ARGUMENTS` is provided, use it as the PR description guidance or to identify the target branch.
