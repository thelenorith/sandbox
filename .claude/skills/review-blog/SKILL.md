---
name: review-blog
description: >
  Perform a structured technical blog post review with link validation, claim verification,
  severity-categorized findings, and actionable recommendations. Use this skill when the user
  asks to review a blog post, technical article, draft, or writing — including requests like
  "review this blog", "check my post", "validate my article", "review my draft for accuracy",
  "fact-check my article", or "proofread my technical post".
allowed-tools: Read, Grep, Glob, Bash(curl *), WebFetch, WebSearch
argument-hint: "[file-path]"
---

# Blog Review Skill

Review the technical blog post at `$ARGUMENTS`.

If `$ARGUMENTS` is empty, ask the user for the file path. If the path looks like a directory, search it for Markdown (`.md`, `.mdx`) or HTML (`.html`) files and ask the user to confirm which file to review.

Read the entire file first. Then produce a structured review following the sections and methodology below. Do NOT rewrite content — provide findings and fixes only.

---

## Output Structure

Your review MUST follow this exact section order:

### 1. TL;DR

2-3 sentences summarizing overall quality. Include a count of issues by severity:

> **X** Critical | **Y** Important | **Z** Suggestions

### 2. Link Validation

Build a table of **every** URL in the document:

| Line | Link Text | URL | HTTP Status | Verdict |
|------|-----------|-----|-------------|---------|

**Verdict values:** `OK` | `Broken` | `Redirect → [target]` | `Timeout` | `Rate-limited` | `Anchor unverifiable`

**Process:**
- Run `curl -sI --max-time 10 <url>` against every URL to get HTTP status
- If a request times out or returns HTTP 429, note it and move on — do not retry excessively
- For relative URLs, resolve them against the document's base URL if known; otherwise flag as "relative URL, cannot validate without base"
- Confirm the linked page actually covers the topic claimed in surrounding text (topical match)
- Note that `curl -I` returns 200 for base pages but **cannot verify #anchor fragments** — flag these as "Anchor unverifiable"
- Flag: GitHub repo paths that 404, inline code spans containing URLs that should be clickable hyperlinks, documentation links where the anchor is unverifiable

### 3. Findings

Group findings by severity. Each finding MUST use this exact format:

```
**[Issue title]** — `filename:line_number`

> Quoted text from the document

[Explanation of what's wrong and WHY it matters — not just "this is wrong" but "this could cause X"]

**Fix**: [Specific actionable correction]
```

#### Severity Levels

| Level | Icon | Criteria |
|-------|------|----------|
| Critical | 🔴 | Factual errors, broken links, information that would mislead or cause harm (wrong command syntax, security-relevant inaccuracies) |
| Important | 🟡 | Inaccuracies that don't cause immediate harm but reduce trust (undocumented claims presented as fact, misleading descriptions, incomplete information) |
| Suggestions | 🟢 | Style, clarity, consistency, and structural improvements |

### 4. Verified Claims

Include a table of claims you checked and found **accurate**:

| Line | Claim | Source | Status |
|------|-------|--------|--------|
| 42 | "Claude supports tool use" | docs.anthropic.com/... | Confirmed |

This shows review thoroughness and gives the author confidence in passing sections.

### 5. Strengths

Call out specific, non-generic positives. Each strength should be actionable — tell the author what to **keep doing**, not just "good job."

Bad: "Well written article"
Good: "Effective preamble — establishes motivation, scope, and audience before diving into technical content"

### 6. Recommendations

Prioritized action list. Order by severity (critical first), then by reader impact.

---

## Content Validation Rules

### Technical Claims

For every technical claim (command behavior, flag syntax, feature availability):

1. Identify the relevant official documentation page
2. Check whether the claim is **confirmed**, **contradicted**, or **unverifiable** from that source
3. Report unverifiable claims explicitly — do NOT assume they are wrong, but flag them as lacking doc support

### Code Blocks

For fenced code blocks in the post:

- Verify the language tag matches the actual syntax (e.g., `bash` vs `shell` vs `zsh`)
- Check command examples for correct syntax (flags, arguments, quoting)
- Flag code that would error or produce unexpected results if copy-pasted
- Do NOT run code blocks — validate by inspection only

### Claim Verification Scope

For dense technical posts, prioritize verifying:

1. Claims that directly affect reader behavior (commands to run, configurations to set)
2. Version-specific or feature-availability claims
3. Security-relevant statements
4. Quantitative claims (performance numbers, limits, counts)

If a post contains more claims than can be reasonably verified, note which categories you checked and which remain unverified.

### Common Issues to Watch For

- **Deprecated features** listed as current
- **Nonexistent commands** or flags
- **Incomplete syntax** (missing required arguments or suffixes)
- **Wrong scope** (per-machine vs per-process vs per-session)
- **Conflated mechanisms** (two distinct features described as one)
- **Unverified claims** (features described from community sources without official doc support)
- **Misleading descriptions** (omitting important caveats or prerequisites)
- **Editorial advice mixed with technical detail** (opinions in what readers treat as a reference)
- **Marketing language in technical context** (vague superlatives instead of concrete descriptions)
- **Stale terminology** (terms not found in current docs)

### DRY Violations

Check for information repeated across sections:

- Same command appearing in multiple tables with different details
- Descriptions re-explaining what was already covered elsewhere
- Reference tables duplicating inline links
- Notes sections repeating constraints already stated in table rows

### KISS Violations

- Repetitive verbose syntax in table columns when the pattern was documented once
- Over-detailed descriptions in reference table cells
- Too many links chained on a single line (5+ doc links with separators)

### Flow and Structure

- Section ordering should match reader priority (daily-use features before niche ones)
- No orphaned subsections without contextual lead-in
- No grab-bag "Notes" sections mixing unrelated topics
- Important warnings (deprecation notices) should not be buried between tables
- Consistent linking (if some table entries are linked, all comparable ones should be, or state why)

---

## Rules

- **DO** reference specific line numbers for every finding
- **DO** quote the problematic text
- **DO** explain impact (not just what's wrong, but what harm it causes)
- **DO** provide concrete fixes, not "consider revising"
- **DO** validate every link with HTTP status check
- **DO** verify technical claims against official documentation
- **DO** check for DRY and KISS violations
- **DO** call out specific strengths

- **DO NOT** rewrite content — provide fixes, not rewrites
- **DO NOT** evaluate subjective writing quality or "engagement"
- **DO NOT** flag formatting unless it affects rendering (e.g., missing blank line before `---` causing setext heading)
- **DO NOT** suggest adding content the author hasn't attempted to cover
- **DO NOT** second-guess the author's scope or audience decisions
- **DO NOT** give generic praise — every strength callout must be specific and actionable
