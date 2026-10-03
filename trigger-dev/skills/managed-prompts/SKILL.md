---
name: managed-prompts
description: Define, version and override Trigger.dev managed prompts — prompts.define() in code, resolve() at runtime, and MCP tools to list, inspect, promote code versions, create dashboard overrides, hotfix, and revert. Use when the user asks about "trigger.dev prompt", "managed prompts", "prompts.define", "prompt version", "prompt override", "hotfix prompt", "promote prompt version", "list prompts", or "revert prompt override".
---

# Managed Prompts

Trigger.dev ships a **Managed Prompts** system: prompts are declared in code with `prompts.define()`, shipped with the worker version, and can receive dashboard overrides that take effect without a redeploy. Seven MCP tools expose the full lifecycle, and the `prompts` namespace of the SDK exposes the same operations from code.

> **Version note:** declaring prompts in code (`prompts.define()`, `resolve()`, `toAISDKTelemetry()`) is documented at https://trigger.dev/docs/ai/prompts and requires SDK and server ≥ 4.5.0 (the feature shipped in v4.5.0). The MCP tools below exist in the CLI from 4.4.4, but they only manage prompts the server knows about.

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
- Run the MCP server with `trigger.dev mcp --readonly` to hide the five prompt write tools in agent-only setups (along with `deploy`, `trigger_task`, `cancel_run` and the other write tools). `install-mcp` has no such flag.
- When iterating heavily via code, prefer `promote_prompt_version` over overrides — it keeps source-of-truth in git.

## SDK Usage (requires SDK and server ≥ 4.5.0)

```ts
import { prompts } from "@trigger.dev/sdk";
import { z } from "zod";

// Declared in code; deploy versions it automatically (the id becomes the slug)
export const supportPrompt = prompts.define({
  id: "customer-support",
  description: "System prompt for customer support interactions",
  model: "<model id>",
  config: { temperature: 0.7 },
  variables: z.object({ customerName: z.string(), issue: z.string() }),
  content: `You are a support agent.
Customer: {{customerName}}
Issue: {{issue}}`,
});
```

Templates use `{{variable}}` placeholders and `{{#flag}}...{{/flag}}` conditionals. Resolve at runtime:

```ts
const resolved = await supportPrompt.resolve({ customerName: "Alice", issue: "Billing page" });
resolved.text;      // compiled prompt
resolved.version;   // e.g. 3
resolved.model;
resolved.labels;    // ["current"] or ["override"]

// Standalone, typed by the handle
const same = await prompts.resolve<typeof supportPrompt>("customer-support", { customerName: "Alice", issue: "Billing page" });

// A specific version or label
await supportPrompt.resolve(vars, { version: 2 });
await supportPrompt.resolve(vars, { label: "current" });
```

Without options `resolve()` returns the active **override** if one exists, otherwise the **current** version. With the AI SDK, spread `...resolved.toAISDKTelemetry()` into `generateText` / `streamText` so generations link to the prompt in the dashboard (token usage, cost and latency per prompt version).

The `prompts` namespace also manages prompts from code: `prompts.list()`, `prompts.versions(slug)`, `prompts.promote(slug, version)`, `prompts.createOverride(slug, { textContent, model, commitMessage })`, `prompts.updateOverride(slug, body)`, `prompts.removeOverride(slug)`, `prompts.reactivateOverride(slug, version)`. For `chat.agent`, store the resolved prompt with `chat.prompt.set(resolved)` and spread `chat.toStreamTextOptions({ registry })` into `streamText` (see the **ai-chat-agents** skill).

## Deeper Reference

- @references/managed-prompts-reference.md — full parameter schemas, input/output examples, worked walkthroughs
- Sibling skills: **mcp-patterns** (Managed Prompts section in the tool catalogue), **observability** (inspect LLM cost/tokens per prompt via `llm_metrics`)
