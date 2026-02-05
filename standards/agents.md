# Claude Code Agents and Skills Standards

Standards for creating, distributing, and managing Claude Code custom skills and subagents.

## Overview

Claude Code supports two extension mechanisms:

| Type | Purpose | Location | Invocation |
|------|---------|----------|------------|
| **Skills** | Custom slash commands | `.claude/skills/<name>/` | `/skill-name` |
| **Subagents** | Specialized AI agents | `.claude/agents/` | Automatic delegation |

## Directory Structure

```
.claude/
├── skills/
│   └── review-code/
│       ├── SKILL.md           # Required: skill definition
│       ├── checklist.md       # Optional: supporting docs
│       └── scripts/
│           └── helper.sh      # Optional: executable scripts
├── agents/
│   └── code-reviewer.md       # Agent definition
├── settings.json              # Project settings
└── hooks/
    └── pre-push.sh            # Hook scripts
```

## Skills

### SKILL.md Format

Skills use Markdown with YAML frontmatter:

```markdown
---
name: skill-name
description: When and why to use this skill. Be specific.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob
model: inherit
---

## Instructions

What Claude should do when this skill is invoked.

Use `$ARGUMENTS` for passed arguments.
Use `$0`, `$1` for positional arguments.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase with hyphens, becomes `/name` |
| `description` | Yes | When Claude should use this skill |
| `disable-model-invocation` | No | `true` = manual only (for dangerous operations) |
| `user-invocable` | No | `false` = Claude only, not in menu |
| `allowed-tools` | No | Tools available without prompts |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `context` | No | `fork` to run in isolated subagent |

### Skill Design Guidelines

| Do | Don't |
|----|-------|
| Single responsibility | Multiple unrelated tasks |
| Clear, specific descriptions | Vague "helps with code" |
| Document all arguments | Assume usage is obvious |
| Keep SKILL.md under 500 lines | Embed all documentation inline |
| Use `disable-model-invocation` for destructive ops | Let Claude auto-deploy |

### Example Skill

```markdown
---
name: review-pr
description: Review pull request for code quality and security issues
disable-model-invocation: true
allowed-tools: Read, Grep, Bash(git diff*), Bash(git log*)
---

## Pull Request Review

Review the current branch against main:

1. **Get changes**: `git diff main...HEAD`
2. **Check for issues**:
   - Security vulnerabilities
   - Missing tests
   - Code style violations
3. **Provide feedback** organized by severity

Arguments: `$ARGUMENTS` (optional: specific files to focus on)
```

## Subagents

### Agent File Format

Agents are Markdown files in `.claude/agents/`:

```markdown
---
name: agent-name
description: What this agent does. Include "use proactively" for auto-delegation.
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
model: sonnet
---

You are a specialized agent for [purpose].

## Capabilities
- What you can do
- What you should do

## Process
1. Step one
2. Step two
```

### Agent Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier |
| `description` | Yes | When Claude should delegate to this agent |
| `tools` | No | Allowlist of available tools |
| `disallowedTools` | No | Deny specific tools |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | No | Permission handling mode |

### Permission Modes

| Mode | Description |
|------|-------------|
| `default` | Prompt for each permission |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Run without asking |
| `bypassPermissions` | Skip all prompts (dangerous) |
| `plan` | Planning only, no execution |

### Agent Design Guidelines

| Do | Don't |
|----|-------|
| Focused expertise | Jack of all trades |
| Include "use proactively" in description | Require manual invocation only |
| Limit tools to what's needed | Grant all tools |
| Read-only for review agents | Allow writes for analysis |

## Distribution

### Approach: Sync from Upstream

Projects sync agents from a central standards repository:

```makefile
STANDARDS_REPO ?= https://github.com/thelenorith/sandbox

sync-agents:  ## Sync agents and skills from standards repo
	@echo "Syncing agents from $(STANDARDS_REPO)..."
	@mkdir -p .claude/skills .claude/agents
	@curl -sL $(STANDARDS_REPO)/archive/main.tar.gz | \
		tar -xz --strip-components=2 -C .claude/ '*/\.claude/*' 2>/dev/null || \
		echo "Using git clone fallback..."
	@if [ ! -d ".claude/skills" ] || [ -z "$$(ls -A .claude/skills 2>/dev/null)" ]; then \
		rm -rf /tmp/standards-sync && \
		git clone --depth 1 --sparse $(STANDARDS_REPO) /tmp/standards-sync && \
		cd /tmp/standards-sync && git sparse-checkout set .claude && \
		cp -r .claude/* $(CURDIR)/.claude/ && \
		rm -rf /tmp/standards-sync; \
	fi
	@echo "Agents synced successfully"
```

### Alternative: Git Submodule

```bash
# Add standards as submodule
git submodule add https://github.com/thelenorith/sandbox .standards

# Symlink .claude directory
ln -s .standards/.claude .claude
```

### Local Customization

After syncing, projects can:

1. **Override** - Create same-named skill locally
2. **Extend** - Add project-specific skills
3. **Disable** - Remove unwanted skills

Local `.claude/skills/` takes precedence over synced content.

## Standard Skills

These skills are provided by the standards repository:

| Skill | Purpose | Manual Only |
|-------|---------|-------------|
| `/review-code` | Code review with checklist | No |
| `/write-tests` | Generate tests for code | No |
| `/check-standards` | Verify project follows standards | No |
| `/security-scan` | Security vulnerability check | No |

## Standard Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| `code-reviewer` | Proactive code review | Read, Grep, Glob |
| `test-writer` | Generate comprehensive tests | Read, Grep, Write |
| `documentation` | Generate and update docs | Read, Write |

## Project Setup

### Initial Setup

```bash
# In your project
make sync-agents

# Or manually
mkdir -p .claude/skills .claude/agents
# Copy desired skills/agents from standards repo
```

### Keeping Updated

```bash
# Re-sync periodically
make sync-agents
```

### Verification

```bash
# List available skills
ls .claude/skills/

# Test a skill
# Type /review-code in Claude Code
```

## Settings Integration

Configure agent behavior in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Grep",
      "Glob",
      "Skill"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-write.sh"
          }
        ]
      }
    ]
  }
}
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Vague descriptions | Specific use cases |
| Granting all tools | Minimal tool access |
| `bypassPermissions` in shared agents | `default` or `acceptEdits` |
| Duplicating skills across repos | Sync from central standards |
| Ignoring `disable-model-invocation` for destructive ops | Always require manual for deploy/push |
| Global installation without version control | Project-level with git tracking |

## Industry References

- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code Subagents Documentation](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Claude Code Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks)
