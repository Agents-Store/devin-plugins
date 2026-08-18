---
name: codemap-review
description: >
  This skill should be used when the user asks to "review code", "check this file", "what's wrong with this code",
  "review my PR", "code quality check", "find issues in this code", or wants feedback on
  readability, style, security, or common beginner mistakes. Provides structured review
  with "why" explanations, not just "what" fixes. Also triggers when a developer asks
  "is this code okay", "what can I improve", or "check my work".
---

# Code Review for Beginners

## Step 0: Execution Mode (MANDATORY)

Before doing ANY work, ask the user:

> "Want me to delegate this to the **code-reviewer** agent (isolated, structured review), or proceed inline in this chat?"

- If user chooses agent → launch the **code-reviewer** agent with the target and context. STOP here — do not continue with the steps below.
- If user chooses inline → proceed with the methodology below.
- If user doesn't respond clearly → default to agent.

---

Review code with educational explanations. Every comment must explain **why** something matters, not just **what** to change.

## Review Process

1. **Read the target** — file, directory, or PR diff provided by user
2. **Identify the context** — what framework, what layer (data/logic/interface), what purpose
3. **Analyze across 5 dimensions** (see below)
4. **Group findings by file**, sorted by severity
5. **Write each finding** with: location, issue, why it matters, suggested fix, learning link

## Review Dimensions

### 1. Security (Critical)
- SQL injection, XSS, command injection (OWASP Top 10)
- Hardcoded secrets, exposed credentials
- Missing authentication/authorization checks
- Unvalidated user input at system boundaries

### 2. Correctness (Critical)
- Logic errors, off-by-one, null/undefined access
- Missing error handling at system boundaries
- Race conditions, data corruption risks
- Broken data isolation (missing user_id filter)

### 3. Readability (Warning)
- Unclear variable/function names — suggest better alternatives
- Functions doing too many things — suggest splitting point
- Deep nesting (3+ levels) — suggest early returns or extraction
- Missing context for non-obvious logic — suggest where a comment helps

### 4. Patterns & Conventions (Warning)
- Framework anti-patterns (e.g., circular imports, global state)
- Inconsistency with project's existing patterns
- Deprecated API usage
- Missing migrations after model changes

### 5. Beginner Pitfalls (Suggestion)
- Copy-paste code that should be extracted
- Over-engineering simple logic
- Missing edge cases that beginners commonly overlook
- Patterns that work now but break at scale

## Severity Levels

| Level | Label | When to use |
|-------|-------|-------------|
| Critical | `CRITICAL` | Security vulnerability, data loss risk, broken functionality |
| Warning | `WARNING` | Bug risk, bad pattern, maintainability problem |
| Suggestion | `SUGGESTION` | Style improvement, learning opportunity, minor optimization |

## Output Format

For each finding:

```
### [SEVERITY] Short title

**File**: `path/to/file.py:42`

**Issue**: What is happening in the code.

**Why this matters**: Explanation of the real-world consequence — what could go wrong, why this pattern is problematic. Use concrete examples, not abstract warnings.

**Fix**:
[code snippet showing the fix]

**Learn more**: One-sentence explanation of the underlying concept.
```

## Tone Rules

- **Patient, not condescending** — explain like a senior colleague, not a teacher grading homework
- **Concrete, not abstract** — "this SQL query is vulnerable to injection because user input goes directly into the query string" NOT "be careful with SQL"
- **Prioritized** — start with critical issues, don't bury security problems under style nitpicks
- **Encouraging** — note what's done well before listing issues
- **Proportional** — for a 20-line file, 2-3 findings is enough. Don't overwhelm.

## What NOT to Review

- Don't nitpick formatting if the project has a linter — the linter already enforces style, so duplicate comments waste the developer's attention
- Don't suggest type hints if the project doesn't use them — adding types piecemeal creates inconsistency and misleads readers about project conventions
- Don't recommend architectural overhauls in a file-level review — large structural changes require broader context and should be a separate discussion
- Don't flag things that are clearly intentional project conventions — contradicting established patterns confuses beginners about what the project actually expects

## Error Handling

- **File not found** → ask the user to verify the path
- **PR not found** → verify PR number, check if `gh` CLI is authenticated
- **Empty file or no code** → inform user, suggest a different target