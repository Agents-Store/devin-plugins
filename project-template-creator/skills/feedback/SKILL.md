---
name: feedback
description: >
  Use this skill when the user says "this should be in the parent template",
  "fix the template", "add this to project-template", "send feedback to parent",
  "improve the base template", "this skill belongs in the template", "update the
  parent", "push this up to the template", "the template needs this", "this is
  missing from the template", or discovers any issue while working in a child
  project that should be fixed in a parent template (Level 0 or Level 1).
disable-model-invocation: true
---

# Send Feedback to Parent Template

Record a problem or improvement found while working in a child project and apply the fix to the parent template's source.

## Prerequisites

Template repos are stored in a shared directory:

- **`$PROJECT_TEMPLATES_DIR`** — directory containing all template repos (e.g., `/path/to/STACKMAKERS/`)

Each template is a separate git repo named by convention: `project-template`, `project-directus-nextjs`, `demo-directus-nextjs`, etc.

If `$PROJECT_TEMPLATES_DIR` is not set, display:
> "Set PROJECT_TEMPLATES_DIR in ~/.claude/settings.json env to the directory containing your template repos."

## Step 1: Identify the Improvement

Ask the user (skip questions already answered from conversation context):

1. **What needs to change?** — Describe the improvement or fix
2. **Which file category?** — skill, command, agent, rule, CLAUDE.md, .env.example, README, docs, config, script, library/dependency
3. **Which parent should it go to?** — Level 0 (universal base) or Level 1 (stack-specific)?
   - If the improvement benefits ALL stacks → Level 0 (`project-template`)
   - If the improvement is specific to THIS stack → Level 1 (`project-{stack}`)
   - If unsure, use the `template-architect` agent to decide
4. **Why should this be in the template?** — Confirm it's not project-specific (resource IDs, client logic, specific credentials are project-specific and should NOT go to the parent)
5. **Severity** — Critical / Major / Minor

If the current conversation already contains the problem context (e.g., the user just struggled with something), extract answers from history instead of asking.

## Step 2: Read stack.json

Read `stack.json` from the current project root to determine:

```bash
cat stack.json
```

Extract:
- `level` — current template level (1, 1.5, or 2)
- `parent` — name of the parent template (e.g., `"project-template"` or `"project-directus-nextjs"`)
- `stack` — stack identifier for context

If targeting Level 0 and the current project is Level 2 (parent is a Level 1), resolve the grandparent: read the Level 1 template's `stack.json` to get `parent: "project-template"`.

## Step 3: Locate Parent Template

Search for the parent template directory using this fallback chain:

1. **`$PROJECT_TEMPLATES_DIR/{parent-name}/`** — primary location
2. **Sibling of current project** — `../{parent-name}/` relative to current project
3. **Clone from GitHub** — offer to clone: `git clone git@github.com:stackmakers-ai/{parent-name}.git "$PROJECT_TEMPLATES_DIR/{parent-name}"`

```bash
PARENT_NAME="project-template"  # from stack.json

# Check primary location
if [ -d "$PROJECT_TEMPLATES_DIR/$PARENT_NAME" ]; then
  PARENT_DIR="$PROJECT_TEMPLATES_DIR/$PARENT_NAME"

# Check sibling directory
elif [ -d "../$PARENT_NAME" ]; then
  PARENT_DIR="../$PARENT_NAME"

else
  echo "Parent template '$PARENT_NAME' not found locally."
  echo "Clone it? git clone git@github.com:stackmakers-ai/$PARENT_NAME.git"
fi
```

Verify the found directory is a git repo and contains `stack.json`.

## Step 3.5: Verify Before Editing

Before making any changes, check whether the improvement already exists in the parent template. This prevents duplicate edits when the user's child project is simply out of sync with its parent.

1. **Read the target file** in the parent template (the file the user wants to change)
2. **Check if the content already exists** — the variable, skill, rule, gotcha, or config the user is requesting may already be there
3. **If already present**, inform the user:
   > "The parent template already has this. Your project may be out of sync — consider merging from the parent instead."
   Offer to help sync the child project instead of editing the parent.
4. **If not present**, proceed to Step 4

This verification step is critical — users often discover "missing" content that was added to the parent after their project was forked. Skipping this leads to duplicate entries or no-op commits.

## Step 4: Apply the Fix

Open the appropriate file in the parent template and make targeted edits. Route by category:

### Skills (`.claude/skills/{name}/SKILL.md`)
- Create a new skill directory and SKILL.md, or edit an existing one
- Include proper frontmatter (name, description with trigger phrases)
- Use imperative form in the body
- Generalize: ensure the skill works for ANY project using this template, not just the one where the issue was discovered

### Commands (`.claude/commands/{name}.md`)
- Create or update with proper frontmatter (description, argument-hint, allowed-tools)
- Keep commands generic — no project-specific paths or IDs

### Agents (`.claude/agents/{name}.md`)
- Create or update with frontmatter (name, description with examples, model)
- Include clear system prompt with responsibilities

### Rules (`.claude/rules/{name}.md`)
- Create or update rule files
- Include a WHY explanation for every restrictive rule

### CLAUDE.md
- Update the relevant section (Tech Stack, Quick Commands, Gotchas, Critical Rules, Installed Plugins)
- Keep total under 100 lines
- Remove any placeholder text being replaced

### .env.example
- Add new environment variables with descriptive comments
- Keep variables grouped by layer (Data / Logic / Interface / External)
- At Level 0: add commented out; at Level 1: uncomment if relevant to the stack

### README.md
- Update documentation, setup instructions, or usage guides
- Keep consistent with CLAUDE.md content

### docs/ (architecture.md, code-style.md, api-conventions.md)
- Update the relevant documentation file
- At Level 0: keep generic with placeholders
- At Level 1: fill with stack-specific content

### .mcp.json.example
- Update MCP connection templates
- Use placeholder URLs only — never real credentials

### scripts/
- Add or fix utility scripts
- Ensure they work cross-platform (use /bin/bash or /bin/sh)

### Dependencies (package.json, etc.)
- Add libraries that should be available by default in all projects from this template
- Prefer exact versions for reproducibility

### Settings (`.claude/settings.local.json.example`)
- Update example settings for Claude Code / Cursor

### Principles
- **Generalize** — ensure the fix covers the common case, not just the reported scenario
- **Minimal change** — fix only what is needed, preserve everything else
- **Preserve structure** — maintain existing formatting and conventions
- **No project-specific content** — resource IDs, client names, real credentials must NOT go to parent templates

## Step 5: Record in LEARNINGS.md

Append to `$PARENT_DIR/LEARNINGS.md` (create if doesn't exist):

```markdown
## [DATE] — [category]: Brief description

**Problem:** What was missing or wrong in the template
**Fix:** What was changed and in which file(s)
**Source:** Discovered in {child-project-name} (Level {N})
**Affected files:** List of changed files
**Severity:** Critical / Major / Minor
```

## Step 6: Commit

```bash
cd "$PARENT_DIR"
git add -A  # or specific files
git commit -m "fix({category}): {brief description}

Discovered in {child-project-name} (Level {N}).
Improves template for all derivative projects."
```

Ask before pushing: "Changes committed locally to {parent-name}. Push to remote? (y/n)"

## Step 7: Note Child Projects

After committing to the parent template, list which child projects should merge from the parent:

> "Fix applied to **{parent-name}**. The following child projects should pull/merge to pick up this change:
> - {list of known children in $PROJECT_TEMPLATES_DIR that have this template as parent}"

To find children, scan directories in `$PROJECT_TEMPLATES_DIR` and check each `stack.json` for `"parent": "{parent-name}"`.

Do NOT automatically propagate changes to children — the user decides when and how to merge.

## Step 8: Alternative — GitHub Issue

If the parent template cannot be edited directly (permissions, not cloned locally, etc.), create a GitHub Issue:

```bash
gh issue create \
  --repo "stackmakers-ai/$PARENT_NAME" \
  --title "Template improvement: {brief description}" \
  --label "template-feedback" \
  --body "## Category: {category}

**Problem:** {what was missing or wrong}
**Suggested fix:** {what should be changed}
**Source:** Discovered in {child-project-name} (Level {N})
**Severity:** {severity}
**Affected files:** {list}"
```
