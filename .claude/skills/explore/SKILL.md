---
name: explore
description: Deep exploration of a codebase or component. Use to understand unfamiliar code.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git log*), Bash(git show*)
model: inherit
agent: Explore
---

## Codebase Exploration

Explore and understand: `$ARGUMENTS`

### Exploration Process

1. **High-Level Structure**
   - What are the main directories?
   - What's the project type (library, service, CLI)?
   - What are the entry points?

2. **Dependency Map**
   - What external dependencies exist?
   - How do internal modules relate?
   - What's the dependency direction?

3. **Key Patterns**
   - What architectural patterns are used?
   - What conventions does the code follow?
   - What's the error handling strategy?

4. **Data Flow**
   - How does data enter the system?
   - How is it transformed?
   - Where does it persist?

5. **History Context**
   - What were recent significant changes?
   - Who are the main contributors?
   - What areas change frequently?

### Output Format

```markdown
## Exploration: [Codebase/Component Name]

### Overview
[1-2 paragraph summary of what this is and does]

### Structure

```
project/
├── src/           # [purpose]
├── tests/         # [purpose]
└── ...
```

### Entry Points
- `main.py` - [description]
- `cli.py` - [description]

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| [Name] | [What it does] | `path/` |

### Dependencies

**External:**
- `library` - Used for [purpose]

**Internal Module Graph:**
```
module_a ──▶ module_b
    │
    ▼
module_c
```

### Patterns Observed

- **Pattern**: [Description]
- **Convention**: [Description]

### Data Flow

```
Input ──▶ [Transform] ──▶ [Store] ──▶ Output
```

### Configuration
- [How the system is configured]
- [Environment variables, config files]

### Testing Approach
- [How tests are organized]
- [Test patterns used]

### Recent Activity
- [Recent significant changes from git log]

### Areas of Complexity
- [Parts that are complex or risky to change]

### Questions / Unclear Areas
- [Things that aren't obvious from the code]
```

### Guidelines

- Start broad, then dive deep as needed
- Look for README, ARCHITECTURE.md, or similar docs first
- Check test files to understand expected behavior
- Use git history to understand evolution
- Note what's unclear for follow-up
