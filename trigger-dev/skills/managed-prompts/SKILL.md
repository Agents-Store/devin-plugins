---
name: managed-prompts
description: Version and override Trigger.dev managed prompts via MCP — list, inspect, promote code versions, create dashboard overrides, hotfix, and revert. Use when the user asks about "trigger.dev prompt", "managed prompts", "prompt version", "prompt override", "hotfix prompt", "promote prompt version", "list prompts", or "revert prompt override".
---

# Managed Prompts

Trigger.dev ships a **Managed Prompts** system: prompts are declared in code, shipped with the worker version, and can receive dashboard overrides that take effect without a redeploy. Seven MCP tools expose the full lifecycle.

> **Note:** the `/docs/prompts` page was not published as of 2026-04-24. This skill documents the feature from the MCP tool schemas (introspected directly from the running MCP server). When the official SDK docs publish, update `references/managed-prompts-reference.md` with the code side.

## Model

Each managed prompt has:

- **`slug`** — stable identifier (`customer-reply`, `summarizer-v2`).
- **Versions** — monotonically increasing integers. Each version carries:
  - `source`: `"code"` (committed with a worker deploy) or `"dashboard"` (created via the UI or an override tool)
  - `model`: the model string
  - `content`: the prompt text
  - `labels`: zero or more of `current`, `override`, `latest`

## Resolution Rules

At runtime the prompt resolver picks the content in this order:

1. **Active dashboard override** (a version whose `labels` include `"override"`), if present.
2. Otherwise, the **current code version** (labels include `"current"`).

- `remove_prompt_override(slug)` — delete the active override, revert to the code current.
- `reactivate_prompt_override(slug, version)` — bring back a historical dashboard version as the active override. Only works on `source: "dashboard"` versions.
- `promote_prompt_version(slug, version)` — re-point the `current` label to a different `source: "code"` version. Does **not** touch overrides; if an override is active it still wins at runtime.

## MCP Tools

All 7 tools take the standard scope arguments (`environment`, `projectRef`, `configPath`, `branch`).

### list_prompts

```
list_prompts({ environment: "prod" })
→ [{ slug, currentVersion, overrideActive, versionCount }, …]
```

First call in any prompt workflow.

### get_prompt_versions

```
get_prompt_versions({ slug: "customer-reply", environment: "prod" })
→ [
  { version: 4, labels: ["current", "latest"], source: "code",      model: "gpt-4o-mini", content: "…" },
  { version: 5, labels: ["override"],          source: "dashboard", model: "gpt-4o",      content: "…" }
]
```

Inspect which version is active, whether an override is in play, and what historical dashboard versions exist.

### promote_prompt_version

```
promote_prompt_version({ slug: "customer-reply", version: 4, environment: "prod" })
```

Makes `version=4` the `current` code version. Requires `source: "code"` — dashboard-sourced versions go through the override tools.

### create_prompt_override

```
create_prompt_override({
  slug:          "customer-reply",
  textContent:   "You are a support agent. Be concise and cite the ticket number…",
  model:         "gpt-4o",            // optional — overrides task default
  commitMessage: "Hotfix tone issue, ticket OPS-1234",
  environment:   "prod"
})
```

Creates a new dashboard-sourced version, marks it as the active override. Next runs pick it up immediately.

### update_prompt_override

```
update_prompt_override({
  slug:          "customer-reply",
  textContent:   "Revised copy v2",
  model:         "gpt-4o",
  commitMessage: "Follow-up tweak"
})
```

Mutates the currently active override (creates a new dashboard version). Fails if no override is active — use `create_prompt_override` first.

### remove_prompt_override

```
remove_prompt_override({ slug: "customer-reply", environment: "prod" })
```

Drops the override. Runtime resolution falls back to the `current` code version.

### reactivate_prompt_override

```
reactivate_prompt_override({ slug: "customer-reply", version: 5, environment: "prod" })
```

Re-enables a prior dashboard-sourced version as the active override. Useful for rolling back a bad override tweak without re-typing the content.

## Common Workflows

### Inspect what's running in prod

```
1. list_prompts(environment="prod")
2. get_prompt_versions(slug="<slug>", environment="prod")
```

### Hotfix a live prompt

```
1. list_prompts(environment="prod")                                                    → find slug
2. get_prompt_versions(slug, environment="prod")                                       → confirm no override active
3. create_prompt_override(slug, textContent="…revised copy…",
                          commitMessage="Hotfix for incident 2026-04-24")              → override active
4. (iterate) update_prompt_override(slug, textContent="…",
                                    commitMessage="Tighten instructions")
5. Verify on subsequent runs (list_runs, get_span_details for the LLM span)
6. Once the code fix lands and is promoted:
   remove_prompt_override(slug, environment="prod")                                    → revert to code
```

### Roll back a bad override

```
1. get_prompt_versions(slug, environment="prod")                                       → find last good dashboard version
2. reactivate_prompt_override(slug, version=<older>, environment="prod")
```

### Promote a code version after a deploy

```
1. deploy(environment="prod")                                                          → ships new worker
2. list_prompts(environment="prod")
3. get_prompt_versions(slug, environment="prod")                                       → find newly-added code version
4. promote_prompt_version(slug, version=<new>, environment="prod")                     → set new `current`
```

> A dashboard override, if active, still wins at runtime after `promote_prompt_version`. Call `remove_prompt_override` to let the new code version take effect.

## Safety Notes

- Prompt overrides are **scoped to an environment + branch**. Always double-check the `environment` argument before calling a write tool — a `prod` override can't be undone on `dev`.
- `commitMessage` is optional on `create_prompt_override` but required discipline — the dashboard version list is your audit trail.
- `update_prompt_override` fails loudly if no override is active; treat that as a signal to use `create_prompt_override` instead.
- Use `--readonly` on the MCP install to block prompt write tools in agent-only setups (along with `deploy`, `trigger_task`, `cancel_run`).
- When iterating heavily via code, prefer `promote_prompt_version` over overrides — it keeps source-of-truth in git.

## SDK Usage

The SDK surface for declaring managed prompts in code is not yet publicly documented (the `/docs/prompts` page is 404 as of 2026-04-24). When Trigger.dev publishes the reference, update `references/managed-prompts-reference.md` with the `@trigger.dev/sdk` side (`prompt()` / `definePrompt()` helper, task integration, tool metadata for AI SDKs, etc.). Until then, this skill anchors on the MCP tool schemas — those are the authoritative source for agents.

## Deeper Reference

- @references/managed-prompts-reference.md — full parameter schemas, input/output examples, worked walkthroughs
- Sibling skills: **mcp-patterns** (Managed Prompts section in the tool catalogue), **observability** (inspect LLM cost/tokens per prompt via `llm_metrics`)
