---
name: design
description: Design architecture for a system or component. Use for significant new features or refactors.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob
model: inherit
agent: Plan
---

## Architecture Design

Design the architecture for: `$ARGUMENTS`

### Design Process

1. **Requirements Gathering**
   - Functional requirements (what it must do)
   - Non-functional requirements (performance, security, scalability)
   - Constraints (technology, timeline, budget)

2. **Context Analysis**
   - How does this fit into the existing system?
   - What are the integration points?
   - What patterns does the codebase already use?

3. **Option Exploration**
   - What are the possible approaches?
   - What are the tradeoffs of each?
   - What does the industry typically do?

4. **Decision Making**
   - Which option best fits the requirements?
   - What are we trading off?
   - What's the migration path?

### Output Format

```markdown
## Design: [Component/System Name]

### Context
[Where this fits in the system]

### Requirements

**Functional:**
- [Must do X]
- [Must do Y]

**Non-Functional:**
- Performance: [target]
- Security: [requirements]
- Scalability: [requirements]

### Options Considered

#### Option A: [Name]
```
[Simple diagram or description]
```

**Pros:**
- [Advantage]

**Cons:**
- [Disadvantage]

#### Option B: [Name]
...

### Recommendation

**Selected: Option [X]**

**Rationale:**
- [Why this option]
- [What we're trading off]

### Component Design

```
[Component diagram]

┌─────────────┐     ┌─────────────┐
│  Component  │────▶│  Component  │
└─────────────┘     └─────────────┘
```

### Interfaces

```python
# Key interfaces/contracts
class ComponentInterface:
    def method(self, param: Type) -> ReturnType:
        """Description"""
        ...
```

### Data Model

```
[Entity relationships or schema]
```

### Security Considerations
- [Authentication]
- [Authorization]
- [Data protection]

### Migration Path
1. [Step 1]
2. [Step 2]

### Open Questions
- [ ] [Question needing resolution]
```

### Guidelines

- Consider existing patterns in the codebase
- Prefer simple solutions over clever ones
- Design for testability
- Document tradeoffs explicitly
- Include migration strategy for existing systems
- Consider operational aspects (monitoring, debugging)
