---
name: plan
description: Create implementation plan for a feature or task. Use before starting complex work.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob
model: inherit
agent: Plan
---

## Implementation Planning

Create a detailed implementation plan for: `$ARGUMENTS`

### Planning Process

1. **Understand the Goal**
   - What is being requested?
   - What is the expected outcome?
   - Who are the stakeholders/users?

2. **Analyze Current State**
   - What exists today?
   - What patterns does the codebase use?
   - What dependencies are involved?

3. **Identify Scope**
   - What's in scope?
   - What's explicitly out of scope?
   - What assumptions are we making?

4. **Break Down Tasks**
   - What are the discrete units of work?
   - What's the logical sequence?
   - What can be parallelized?

5. **Identify Risks**
   - What could go wrong?
   - What's uncertain?
   - What needs clarification?

### Output Format

```markdown
## Plan: [Feature/Task Name]

### Goal
[1-2 sentence description]

### Current State
- [What exists]
- [Relevant patterns]

### Tasks

1. [ ] **Task name** - Description
   - Files: `path/to/file.py`
   - Estimated complexity: Low/Medium/High

2. [ ] **Task name** - Description
   - Files: `path/to/file.py`
   - Dependencies: Task 1

### Risks & Open Questions
- [ ] [Risk or question]
- [ ] [Risk or question]

### Out of Scope
- [What we're not doing]

### Testing Strategy
- [ ] Unit tests for [component]
- [ ] Integration tests for [flow]
```

### Guidelines

- Keep tasks small (< 1 hour each ideally)
- Identify file paths that will be modified
- Note dependencies between tasks
- Flag anything that needs clarification before starting
- Consider backward compatibility
- Include testing in the plan
