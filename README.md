# my-tools

A Claude Code plugin for centrally managing skills, agents, hooks, and MCP servers across environments.

## Structure

```
.
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
├── .claude/
│   └── settings.json        # Project-level permissions (for repo contributors, not plugin consumers)
├── skills/
│   ├── commit/SKILL.md      # /my-tools:commit  — conventional commit workflow
│   ├── pr/SKILL.md          # /my-tools:pr      — PR creation with structured body
│   └── review-pr/SKILL.md   # /my-tools:review-pr — PR code review
├── agents/
│   └── code-reviewer.md     # Code review subagent (restricted tool access)
├── hooks/
│   └── hooks.json           # Git safety hooks (force push, destructive ops)
├── .mcp.json                # GitHub MCP server
└── README.md
```

## Installation

### Local development / testing

```bash
claude --plugin-dir /path/to/this/repo
```

### As a marketplace plugin

Add this repo as a marketplace source in your `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "my-tools": {
      "source": {
        "source": "github",
        "repo": "thelenorith/sandbox"
      }
    }
  }
}
```

Then install with `/plugin install my-tools@my-tools`.

## What's included

### Skills

| Skill | Invocation | Description |
|---|---|---|
| commit | `/my-tools:commit` | Stages changes, drafts a conventional commit message, and commits. Respects pre-commit hooks. |
| pr | `/my-tools:pr` | Creates a GitHub PR with a structured summary and test plan. |
| review-pr | `/my-tools:review-pr <number>` | Reviews a PR for correctness, security, error handling, and test coverage. |

### Agents

| Agent | Description |
|---|---|
| code-reviewer | Restricted-tool subagent for code review. Has access to Read, Glob, Grep, and read-only git/gh commands. |

Use via `/agents` or the Task tool with `subagent_type`.

### Hooks

All hooks fire on `PreToolUse` for `Bash` commands:

| Hook | Decision | Trigger |
|---|---|---|
| Force push to main/master | `deny` | `git push --force` targeting main or master |
| Force push to feature branch | `ask` | `git push --force` on any other branch |
| Destructive git operations | `ask` | `git reset --hard` or `git clean -f` |

### MCP Servers

| Server | Purpose |
|---|---|
| github | GitHub MCP server via `@modelcontextprotocol/server-github`. Requires `GITHUB_TOKEN` env var. |

## Customization

### Adding a new skill

```bash
mkdir skills/my-skill
```

Create `skills/my-skill/SKILL.md` with frontmatter:

```markdown
---
name: my-skill
description: When to use this skill.
---

Instructions for Claude when this skill is invoked.
```

### Adding a new agent

Create `agents/my-agent.md` with frontmatter:

```markdown
---
name: my-agent
description: What this agent does.
model: sonnet
allowedTools:
  - Read
  - Glob
---

System prompt for the agent.
```

### Adding hooks

Edit `hooks/hooks.json`. Hooks receive tool input as JSON on stdin. Use `jq` to extract fields. Return a JSON object with `decision` (`deny`, `ask`, or omit for allow) and `reason`.

### Adding MCP servers

Edit `.mcp.json`. Use `${ENV_VAR}` syntax for secrets.

## Gaps: what plugins cannot manage

A plugin's `settings.json` (at the plugin root) currently **only supports the `agent` key**. Other settings keys are silently ignored. The following configurations must be managed separately:

| Configuration | Where it lives | Notes |
|---|---|---|
| **Permission rules** (allow/deny/ask) | `settings.json` → `permissions` | Cannot travel with a plugin through marketplace installation. |
| **CLAUDE.md instructions** | `CLAUDE.md`, `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md` | Memory/instruction files are not part of the plugin system. |
| **Environment variables** | `settings.json` → `env` | Plugin MCP servers can reference env vars with `${VAR}`, but you can't define env vars via a plugin. |
| **Model preferences** | `settings.json` → `model` | Default model selection is per-environment. Agents *within* the plugin can specify a model. |
| **Sandbox configuration** | `settings.json` → `sandbox` | Network allowlists, excluded commands, etc. are environment-specific. |
| **Status line** | `settings.json` → `statusLine` | Custom status line commands are environment-specific. |
| **Managed/enterprise settings** | `managed-settings.json` | IT-deployed policies (forced login, hook restrictions, MCP allowlists) are out of scope for plugins. |

### The project-settings workaround

Permissions can't live in the **plugin** `settings.json`, but they *can* live in a **project-level** `.claude/settings.json` — which is exactly what [cblecker/claude-plugins](https://github.com/cblecker/claude-plugins) does. This repo includes one at `.claude/settings.json`.

**How it works**: When someone clones this repo and runs `claude` inside it, the `.claude/settings.json` file applies as project-level config. It auto-allows the plugin's skills, read-only git/gh commands, and blocks reads of sensitive files.

**Limitation**: This only applies to people working *inside this repo*. It does **not** travel with the plugin when installed via a marketplace. For permissions that follow you everywhere, use `~/.claude/settings.json` (user scope).

```
Plugin settings.json (plugin root)     →  only "agent" key, ships with plugin
Project .claude/settings.json           →  full settings, applies to repo cloners only
User ~/.claude/settings.json            →  full settings, applies everywhere for you
```

### Practical impact

- **Permissions**: No plugin-level permissions config exists today. Use `~/.claude/settings.json` on each machine for personal defaults, or `.claude/settings.json` in a repo for team defaults.
- **CLAUDE.md**: Project-specific instructions remain in the repo's `CLAUDE.md`. Personal instructions go in `~/.claude/CLAUDE.md`. Neither can be packaged as a plugin.
- **Model**: Set `"model": "sonnet"` in user settings for a global default. Agents within the plugin can specify their own model independently.
