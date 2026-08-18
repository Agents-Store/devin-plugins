---
name: wrap-up
description: >
  Use this skill when the user says "wrap up", "end session", "done for today",
  "session review", "what should go into the template", "template improvements",
  "save template learnings", "review what we did for the template", "plugin
  improvements", "what should go into the plugin", or at the end of a work session
  to review what discoveries should be pushed up to parent templates or plugins.
disable-model-invocation: true
---

# End-of-Session Unified Wrap-Up

Review the current session, identify improvements that should be pushed to parent templates OR plugins, process any captured backlog items, and apply or record them.

## Phase 0: Process Captured Items

Check if `.claude/improvement-backlog.md` exists in the current project root. If yes:

1. Read all captured items from the backlog
2. Present them to the user as a numbered list
3. Include them alongside conversation-discovered items in Phase 1
4. After all items are processed (Phase 3), clear the backlog file

If the backlog file does not exist or is empty, skip to Phase 1.

## Phase 1: Session Review

Analyze the current conversation and list:

1. **Template files modified** — Skills, commands, rules, CLAUDE.md, docs, configs that were created or changed during this session
2. **Workarounds discovered** — Manual fixes that should be documented in the template (gotchas, edge cases, missing env vars)
3. **New skills/commands created** — Generic enough to benefit all projects using this stack
4. **Missing environment variables** — Vars that had to be added during the session
5. **Documentation gaps** — Architecture, code style, or API conventions that were unclear
6. **Safety rules discovered** — Patterns that should be prevented in all projects
7. **Dependency additions** — Libraries added that should be available by default
8. **Configuration fixes** — Settings, Docker configs, build configs that needed tweaking
9. **Plugin issues** — Agents Store plugins that produced incorrect output, were missing knowledge, or required manual workarounds
10. **Backlog items** — Items captured via `/capture` during the session (from Phase 0)

Present as:

```
## Session Review

**Current project:** {project-name} (Level {N})
**Parent templates:** {Level 1 parent} → {Level 0 parent}
**Backlog items processed:** {N from Phase 0, or "none"}

### Improvements Found

#### Push to Plugins
🔌 {plugin-name}: {description of tool knowledge improvement}

#### Push to Level 0 (all stacks)
✅ {description of universal improvement}

#### Push to Level 1 (this stack only)
✅ {description of stack-specific improvement}

#### Project-only (skip)
⏭️ {description of project-specific change — not for template}
```

## Phase 2: Categorize Findings

For each finding, classify:

- **Target:** Plugin (`{plugin-name}`) / Level 0 (universal) / Level 1 (stack-specific) / project-only (skip)
- **Category:** skill, command, agent, rule, CLAUDE.md, .env.example, docs, config, script, dependency
- **Priority:** Must-have (blocks future projects) / Nice-to-have (convenience improvement)

### Classification Rules

Push to **Plugin** if:
- It's about how a specific tool's API, SDK, or CLI works
- It references a specific Agents Store plugin skill that produced wrong output
- It's about MCP tool usage patterns or error handling
- A matching plugin exists in `$PLUGINS_PUBLIC_SOURCE_DIR` or `$PLUGINS_PRIVATE_SOURCE_DIR`
- The knowledge helps ALL projects using that tool, regardless of stack

Push to **Level 0** if:
- It benefits ALL stacks regardless of technology (process skills, safety rules, generic commands)
- It's a fix to a core template file (sync script, generic docs structure)

Push to **Level 1** if:
- It depends on specific technologies (Next.js patterns, Directus SDK usage)
- It's a stack-specific gotcha or workaround
- It adds stack-specific environment variables or dependencies

Keep **project-only** if:
- It contains client resource IDs, names, or credentials
- It's domain-specific business logic
- It's a one-off customization

When unsure, use the `template-architect` agent to decide.

## Phase 3: User Decision

Present the categorized findings and ask:

> "Found {N} improvements ({P} plugin, {T0} Level 0, {T1} Level 1). Should I:
> (a) Apply all fixes (plugins + templates) and commit
> (b) Apply template fixes only (skip plugins)
> (c) Apply plugin fixes only (skip templates)
> (d) Create GitHub Issues for everything
> (e) Just record in this project's LEARNINGS.md
> (f) Skip"

### For plugin fixes:
Invoke `/plugin-creator:feedback` via the Skill tool for each plugin improvement. Pass the plugin name, skill name (if known), what happened, what should happen, and severity so the feedback skill can pick up context.

If `/plugin-creator:feedback` is not available (plugin-creator not installed), fall back to creating GitHub Issues or recording in LEARNINGS.md.

### For template fixes:
Delegate to the `feedback` skill for each item. Read the feedback skill at `${CLAUDE_PLUGIN_ROOT}/skills/feedback/SKILL.md`.

When fixing multiple items in the same target (same plugin or same parent template), apply all fixes before committing — create one commit per target with a summary message, not one commit per fix.

### For option (b) — GitHub Issues:
Create ONE grouped issue per parent template:

```bash
gh issue create \
  --repo "stackmakers-ai/$PARENT_NAME" \
  --title "Template improvements from session $(date +%Y-%m-%d)" \
  --label "template-feedback" \
  --body "$GROUPED_FINDINGS_MARKDOWN"
```

### For option (c) — Record only:
Append to the current project's `LEARNINGS.md` with a `TEMPLATE FEEDBACK` marker:

```markdown
## [DATE] — TEMPLATE FEEDBACK: Session wrap-up

**Target:** {parent-template-name} (Level {N})
**Findings:**
1. {description} — {category} — {priority}
2. ...

**Status:** Recorded, not yet applied to parent template.
```

## Phase 4: Suggest New Skills

If the session revealed missing capabilities in the template:

> "During this session you manually created a '{skill-name}' workflow. Should I add this as a skill to {parent-template-name}?"

If the user agrees, delegate to the `feedback` skill with the skill creation details.

## Phase 5: Summary

```
Session wrap-up complete:

  Plugins:
    - Fixed {N} skills in {plugin-name} (committed to {public/private})
    - Created {N} Issues for {plugin-name}

  Templates:
    - Applied {N} fixes to {L0-parent} (committed)
    - Applied {N} fixes to {L1-parent} (committed)
    - Created {N} GitHub Issues

  Backlog: Cleared {N} captured items
  Recorded: {N} items in LEARNINGS.md
  Suggested: {N} new skills

Child projects that should merge from updated templates:
  - {list}
```

If the backlog file was processed, clear it:
```bash
rm -f .claude/improvement-backlog.md
```
