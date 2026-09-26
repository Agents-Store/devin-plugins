---
name: improve
description: >
  Use this skill when the user says "improve", "this should be better",
  "fix this in the source", "this belongs in the plugin", "this belongs in the
  template", "push this upstream", "improve the plugin", "improve the template",
  or discovers any improvement while working in a child project that should go to
  either a plugin or a parent template. This is the unified entry point that
  auto-routes to the correct system.
disable-model-invocation: true
---

# Unified Improve — Route to Plugin or Template

Classify an improvement discovered during work and route it to the correct system: plugin source or parent template.

## Step 1: Understand the Improvement

From the user's description and conversation context, determine:

1. **What needs to change?** — The specific fix, addition, or improvement
2. **What kind of knowledge is it?**
   - **Tool knowledge** — how a specific tool's API, SDK, CLI, or MCP works (e.g., "Directus SDK needs `cache: 'no-store'`")
   - **Process knowledge** — how to work within a project regardless of tools (e.g., "add a pre-commit hook for linting")
   - **Stack knowledge** — how specific technologies integrate in this stack (e.g., "Next.js + Directus image loading needs `remotePatterns`")
   - **Project-specific** — resource IDs, client credentials, domain logic

If the current conversation already contains the problem context, extract answers from history instead of asking.

## Step 2: Classify — Plugin or Template?

Apply these rules in order:

### Route to Plugin if ANY are true:
- The improvement is about how a specific tool's API, SDK, or CLI works
- It would help ALL projects using that tool, regardless of which stack
- It's about MCP tool patterns, error handling, or API reference
- A matching plugin exists in `$PLUGINS_PUBLIC_SOURCE_DIR` or `$PLUGINS_PRIVATE_SOURCE_DIR`

**Verify plugin exists:**
```bash
PLUGIN_NAME="directus-dev"  # derived from the tool + process type
ls "$PLUGINS_PUBLIC_SOURCE_DIR/$PLUGIN_NAME" 2>/dev/null || ls "$PLUGINS_PRIVATE_SOURCE_DIR/$PLUGIN_NAME" 2>/dev/null
```

If the plugin exists, route to plugin. If not, tell the user no matching plugin was found and ask whether to create a template improvement instead.

### Route to Template Level 0 if ALL are true:
- The improvement works regardless of which technologies are in the stack
- It uses no technology-specific APIs, SDKs, or patterns
- ALL stack templates would benefit from it
- Examples: process skills, core commands, safety rules, generic conventions

### Route to Template Level 1 if ANY are true:
- The improvement references a specific technology
- It depends on a specific SDK, CLI, or API within the stack context
- It adds stack-specific environment variables or deployment config
- Examples: stack-specific gotchas in CLAUDE.md, stack-specific skills, Docker config

### Project-only — do NOT route if ANY are true:
- Contains client resource IDs, real credentials, or API keys
- Is client-specific business logic or domain knowledge
- Is a one-off customization unlikely to be reused

If project-only, inform the user:
> "This improvement is project-specific (contains resource IDs / client logic / credentials). It should stay in this project, not go to a parent template or plugin."

Stop here.

### When unsure:
Use the `template-architect` agent to decide. Provide it with the improvement description and let it classify.

## Step 3: Confirm Classification with User

Present the classification:

> **Improvement:** {description}
> **Routed to:** Plugin (`{plugin-name}`) / Template Level 0 (`project-template`) / Template Level 1 (`project-{stack}`)
> **Reason:** {one sentence}
>
> Proceed? (y/change)

If the user disagrees, reclassify.

## Step 4: Delegate to the Correct System

### If routed to Plugin:
Invoke `/plugin-creator:feedback` via the Skill tool. Pass the improvement details (plugin name, skill name if known, what happened, what should happen, severity) so the feedback skill can pick up context without re-asking.

If `/plugin-creator:feedback` is not available (plugin-creator not installed), display:
> "The `plugin-creator` plugin is not installed. To fix plugins, either:
> 1. Install plugin-creator and run `/plugin-creator:feedback`
> 2. Manually edit the plugin source at `$PLUGINS_PUBLIC_SOURCE_DIR/{plugin-name}/` or `$PLUGINS_PRIVATE_SOURCE_DIR/{plugin-name}/`"

### If routed to Template (Level 0 or Level 1):
Read and follow the feedback skill at `${CLAUDE_PLUGIN_ROOT}/skills/feedback/SKILL.md`. The feedback skill handles locating the parent template, applying the fix, recording in LEARNINGS.md, and committing.

Pass the pre-classified target level so the feedback skill doesn't need to re-ask.
