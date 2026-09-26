---
name: capture
description: >
  Use this skill when the user says "capture this", "note this for later",
  "remember to fix this", "save this improvement", "add to backlog",
  "I'll fix this later", or wants to quickly jot down an improvement idea
  without interrupting their current work. Defers routing and application
  to the wrap-up session.
disable-model-invocation: true
---

# Quick-Capture Improvement Idea

Save an improvement idea to the backlog for later processing during wrap-up. No routing, no classification — just capture and continue.

## Step 1: Capture the Entry

Append to `.claude/improvement-backlog.md` in the current project root. Create the file if it doesn't exist.

### File format:

```markdown
# Improvement Backlog

## Captured: {YYYY-MM-DD HH:MM}
**Note:** {user's description — what needs improving}
**Context:** {what was being done when this was noticed — extract from recent conversation}

---
```

Each new entry is appended after existing entries, separated by `---`.

### What to include in Context:
- What task the user was working on when they noticed this
- Which file or tool was involved
- Any error messages or unexpected behavior
- Enough detail so the wrap-up skill can classify it later without the original conversation

### Example entry:

```markdown
## Captured: 2026-03-30 14:22
**Note:** directus-dev plugin missing cache: 'no-store' gotcha in sdk-patterns skill
**Context:** Was fetching Directus collections in a Server Component and got stale data. Had to manually add cache: 'no-store' to every fetch call. The directus-dev sdk-patterns skill should document this.

---
```

## Step 2: Confirm

Count the total entries in the backlog file and respond with a single line:

> Captured. {N} item(s) in backlog. Run `/wrap-up` to process.

Do not ask follow-up questions. Do not classify. Do not route. Return to the user's previous task immediately.
