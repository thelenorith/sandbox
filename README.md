# my-tools

A Claude Code plugin for centrally managing skills, agents, hooks, and MCP servers across environments.

## Structure

```
.
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (name, version, metadata)
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

The following configurations **cannot** be set via a plugin and must be managed separately in settings files (`~/.claude/settings.json`, `.claude/settings.json`, or `.claude/settings.local.json`):

| Configuration | Where it lives | Notes |
|---|---|---|
| **Permission rules** (allow/deny/ask) | `settings.json` → `permissions` | Cannot be bundled in a plugin. Each environment needs its own permission rules. |
| **CLAUDE.md instructions** | `CLAUDE.md`, `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md` | Memory/instruction files are not part of the plugin system. |
| **Environment variables** | `settings.json` → `env` | Plugin MCP servers can reference env vars with `${VAR}`, but you can't set arbitrary env vars via a plugin. |
| **Model preferences** | `settings.json` → `model` | Default model selection is per-environment. |
| **Sandbox configuration** | `settings.json` → `sandbox` | Network allowlists, excluded commands, etc. are environment-specific. |
| **Plugin `settings.json`** (limited) | Plugin root `settings.json` | Currently **only supports the `agent` key** to set a default agent. Other settings keys are silently ignored. |
| **Status line** | `settings.json` → `statusLine` | Custom status line commands are environment-specific. |
| **Managed/enterprise settings** | `managed-settings.json` | IT-deployed policies (forced login, hook restrictions, MCP allowlists) are out of scope for plugins. |

### Practical impact

- **Permissions**: If you want `Bash(npm run test *)` auto-approved everywhere, you need to add it to `~/.claude/settings.json` on each machine. There is no plugin-level permissions config.
- **CLAUDE.md**: Project-specific instructions (coding style, architecture notes) remain in the repo's `CLAUDE.md`. Personal instructions go in `~/.claude/CLAUDE.md`. Neither can be packaged as a plugin.
- **Model**: If you prefer `sonnet` by default, set `"model": "sonnet"` in your user settings. Agents within the plugin *can* specify a model, but the top-level default cannot be set by a plugin.
