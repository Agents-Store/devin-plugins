---
name: sync
description: >
  Use this skill when the user says "sync from parent", "pull template changes",
  "merge parent template", "update from project-template", "my project is out of
  sync", "get latest template changes", "sync template", or needs to propagate
  improvements from a parent template (Level 0 or Level 1) down to a child project.
disable-model-invocation: true
---

# Sync Child Project from Parent Template

Pull improvements from a parent template into the current child project. This is the counterpart to the `feedback` skill — feedback pushes changes UP, sync pulls changes DOWN.

## When to Use

- After the `feedback` skill commits changes to a parent template
- When a child project was forked before recent parent improvements
- When the user notices their template files are outdated compared to the parent
- Periodically, to keep child projects aligned with the latest template conventions

## Prerequisites

- **`$PROJECT_TEMPLATES_DIR`** — directory containing all template repos
- The current project must have a `stack.json` with a `parent` field
- The parent template must be available locally (or cloneable from GitHub)

## Step 1: Identify Parent and Current Level

Read `stack.json` from the current project:

```bash
cat stack.json
```

Extract: `level`, `parent`, `stack`. If `parent` is null (Level 0), there is nothing to sync from — inform the user and stop.

## Step 2: Locate Parent Template

Use the same fallback chain as the `feedback` skill:

1. `$PROJECT_TEMPLATES_DIR/{parent}/`
2. `../{parent}/`
3. Offer to clone from `git@github.com:stackmakers-ai/{parent}.git`

## Step 3: Compare Files

Compare key template files between parent and child. Focus on files that are inherited (not project-specific):

### Files to Compare

| Category | Files |
|----------|-------|
| Process skills | `.claude/skills/brainstorming/`, `planning/`, `tdd/`, `debugging/`, `verification/` |
| Core commands | `.claude/commands/commit.md`, `pr.md`, `plan.md`, `review.md`, `retro.md`, `sync.md`, `fix-issue.md`, `init-stack.md` |
| Rules | `.claude/rules/safety.md`, `search-before-building.md`, `project-conventions.md` |
| Agent | `.claude/agents/code-reviewer.md` |
| Settings template | `.claude/settings.local.json.example` |
| Docs structure | `docs/architecture.md`, `docs/code-style.md`, `docs/api-conventions.md` |
| Scripts | `scripts/sync-context.sh` |
| Editor config | `.editorconfig` |

### Files to Skip (project-specific)

Do NOT sync these — they contain project-specific content:
- `stack.json` (different level and parent)
- `CLAUDE.md` (customized per project)
- `.env.example` (may have project-specific additions)
- `project-config/SKILL.md` (contains resource IDs)
- Any domain-specific skills, agents, or rules

### How to Compare

For each file in the comparison list:

```bash
# Check if file exists in both
PARENT_FILE="$PARENT_DIR/$FILE_PATH"
CHILD_FILE="./$FILE_PATH"

if [ -f "$PARENT_FILE" ] && [ -f "$CHILD_FILE" ]; then
  # Compare content
  diff "$PARENT_FILE" "$CHILD_FILE"
elif [ -f "$PARENT_FILE" ] && [ ! -f "$CHILD_FILE" ]; then
  echo "NEW in parent: $FILE_PATH"
elif [ ! -f "$PARENT_FILE" ] && [ -f "$CHILD_FILE" ]; then
  echo "ONLY in child: $FILE_PATH (may be project-specific)"
fi
```

## Step 4: Present Diff Summary

Show the user what changed:

```
## Sync Report: {child-project} ← {parent-template}

### New in Parent (not in your project)
- .claude/skills/new-skill/SKILL.md — {description from skill frontmatter}
- .claude/rules/new-rule.md

### Modified in Parent (your version differs)
- .claude/commands/commit.md — {brief description of changes}
- .claude/rules/safety.md — {brief description of changes}
- scripts/sync-context.sh — {brief description of changes}

### Unchanged
- .claude/skills/brainstorming/SKILL.md — identical
- (... list of identical files)

### Skipped (project-specific)
- stack.json, CLAUDE.md, .env.example, project-config/SKILL.md
```

## Step 5: User Decision

For each changed file, ask the user:

> "How should I handle each difference?
> (a) **Accept parent** — overwrite your version with the parent's version
> (b) **Keep yours** — keep your project's version unchanged
> (c) **Merge** — manually merge the changes (I'll show both versions)
> (d) **Skip all** — don't sync anything"

For new files from the parent, default to accepting them (they're new capabilities).
For modified files, show the diff and let the user decide per file.

## Step 6: Apply Changes

For each file the user chose to accept or merge:

1. Copy the parent version to the child project (or apply the merge)
2. Track which files were synced

## Step 7: Check .env.example and CLAUDE.md

These project-specific files are skipped from automatic sync, but may have relevant additions in the parent. Compare them separately and suggest manual updates:

> "The parent template's `.env.example` has new variables that your project doesn't have:
> - `VERCEL_PROJECT_ID` (added in parent on 2026-03-28)
>
> Want me to add these to your `.env.example`? (Your existing values won't be affected.)"

For CLAUDE.md, highlight new sections or gotchas added to the parent:

> "The parent template's CLAUDE.md has a new Gotchas section. Want me to add these gotchas to your CLAUDE.md?"

## Step 8: Summary

```
Sync complete: {child-project} ← {parent-template}
  - Accepted: {N} files from parent
  - Kept: {N} files as-is
  - Merged: {N} files manually
  - New additions: {N} files
  - .env.example: {updated/skipped}
  - CLAUDE.md: {updated/skipped}
```
