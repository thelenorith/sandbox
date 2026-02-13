# Work Standards

[![Markdown Lint](https://github.com/thelenorith/sandbox/actions/workflows/markdown-lint.yml/badge.svg)](https://github.com/thelenorith/sandbox/actions/workflows/markdown-lint.yml)
[![Validate Links](https://github.com/thelenorith/sandbox/actions/workflows/links.yml/badge.svg)](https://github.com/thelenorith/sandbox/actions/workflows/links.yml)

Reusable software development standards. Reference these instead of recreating project-specific guidelines.

## Usage

Reference in your project:

```markdown
This project follows the [Work Standards](https://github.com/thelenorith/sandbox/tree/main/standards).
```

Sync Claude Code agents:

```bash
make sync-agents STANDARDS_REPO=https://github.com/thelenorith/sandbox
```

## Standards

See [standards/index.md](standards/index.md) for complete catalog with guiding principles.

| Area | Standards |
|------|-----------|
| Code | [Naming](standards/naming.md), [Code Style](standards/code-style.md), [Project Structure](standards/project-structure.md), [Testing](standards/testing.md) |
| Build | [Makefile](standards/makefile.md), [GitHub Workflows](standards/github-workflows.md), [Releases](standards/releases.md) |
| Docs | [README Format](standards/readme-format.md) |
| CLI | [CLI](standards/cli.md), [Logging & Progress](standards/logging-progress.md) |
| Services | [Services](standards/services.md), [API Design](standards/api-design.md) |
| UI | [User Interface](standards/user-interface.md) |
| Agents | [Agents](standards/agents.md) |

## Included Agents

### Planning (use before coding)

| Type | Name | Purpose |
|------|------|---------|
| Skill | `/plan` | Implementation planning with task breakdown |
| Skill | `/design` | Architecture design with tradeoff analysis |
| Skill | `/explore` | Deep codebase exploration |
| Agent | `architect` | Proactive design review for structural changes |

### Reactive (use during/after coding)

| Type | Name | Purpose |
|------|------|---------|
| Skill | `/review-code` | Code review checklist |
| Skill | `/write-tests` | Generate tests |
| Skill | `/check-standards` | Verify project compliance |
| Skill | `/security-scan` | Security vulnerability scan |
| Agent | `code-reviewer` | Proactive code review |
| Agent | `test-writer` | Proactive test generation |
| Agent | `documentation` | Documentation generation |

## License

MIT
