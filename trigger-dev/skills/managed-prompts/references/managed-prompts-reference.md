# Managed Prompts — MCP Reference

Complete parameter schemas for the 7 Managed Prompts MCP tools (introspected from the live `trigger.dev@latest mcp` server as of v4.4.4).

All tools accept the standard scope parameters (omitted from the per-tool tables below):

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `environment` | `"dev"` \| `"staging"` \| `"prod"` \| `"preview"` | `"dev"` | Which environment to target |
| `projectRef` | string (`proj_xxx`) | auto-detected | From trigger.config.ts or `--project-ref` |
| `configPath` | string | auto | Path to trigger.config.ts — needed in monorepos |
| `branch` | string | — | Only for `environment="preview"` |

---

## list_prompts

List managed prompts.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| (scope only) | — | — | — |

```
Input: { "environment": "prod" }

Output: [
  { slug: "customer-reply", currentVersion: 4, overrideActive: false, versionCount: 7 },
  { slug: "summarizer-v2",  currentVersion: 2, overrideActive: true,  versionCount: 3 }
]
```

---

## get_prompt_versions

List all versions for a single prompt.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |

```
Input: { "slug": "customer-reply", "environment": "prod" }

Output: [
  {
    version: 4,
    labels:  ["current", "latest"],
    source:  "code",
    model:   "gpt-4o-mini",
    content: "You are a helpful support agent…"
  },
  {
    version: 5,
    labels:  ["override"],
    source:  "dashboard",
    model:   "gpt-4o",
    content: "You are a helpful support agent. Be concise…"
  }
]
```

Label meanings:
- `current` — active code version (the one that would resolve if no override existed)
- `override` — active dashboard override (wins at runtime over `current`)
- `latest` — highest version number regardless of source

---

## promote_prompt_version

Make a code-sourced version the `current` one.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |
| `version` | integer > 0 | ✔ | Version to promote (must be `source: "code"`) |

```
Input: { "slug": "customer-reply", "version": 4, "environment": "prod" }

Output: { slug: "customer-reply", currentVersion: 4 }
```

Error cases: version not found; version is `source: "dashboard"` (use override tools instead).

---

## create_prompt_override

Create a new dashboard override. Becomes the active override immediately.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |
| `textContent` | string | ✔ | Full prompt text |
| `model` | string | ✖ | Optional model override |
| `commitMessage` | string | ✖ | Audit-trail note |

```
Input: {
  "slug":          "customer-reply",
  "textContent":   "You are a support agent. Be concise and cite the ticket number.",
  "model":         "gpt-4o",
  "commitMessage": "Hotfix tone for incident OPS-1234",
  "environment":   "prod"
}

Output: { slug: "customer-reply", overrideVersion: 5, source: "dashboard" }
```

---

## update_prompt_override

Mutate the currently active override. Creates a new dashboard version each time.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |
| `textContent` | string | ✖ | New text (leave out to keep current) |
| `model` | string | ✖ | New model |
| `commitMessage` | string | ✖ | Audit-trail note |

```
Input: {
  "slug":          "customer-reply",
  "textContent":   "Revised copy v2",
  "commitMessage": "Follow-up tweak"
}

Output: { slug: "customer-reply", overrideVersion: 6 }
```

Error case: no override currently active → use `create_prompt_override`.

---

## remove_prompt_override

Remove the active override; revert to the code `current` version.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |

```
Input: { "slug": "customer-reply", "environment": "prod" }

Output: { slug: "customer-reply", overrideActive: false }
```

---

## reactivate_prompt_override

Reactivate a prior dashboard-sourced version as the active override.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `slug` | string | ✔ | Prompt slug |
| `version` | integer > 0 | ✔ | Dashboard-sourced version to reactivate |

```
Input: { "slug": "customer-reply", "version": 5, "environment": "prod" }

Output: { slug: "customer-reply", overrideVersion: 5 }
```

Error case: target version has `source: "code"` → use `promote_prompt_version`.

---

## Worked Example — Incident Hotfix

Scenario: production task is replying too aggressively. Ticket OPS-1234 demands an immediate tone change while the engineering fix is still in review.

```
# 1. Find the slug
list_prompts(environment="prod")
→ [ { slug: "customer-reply", currentVersion: 4, overrideActive: false, versionCount: 7 } ]

# 2. Inspect current state
get_prompt_versions(slug="customer-reply", environment="prod")
→ [ { version: 4, labels: ["current", "latest"], source: "code", … } ]

# 3. Apply the hotfix
create_prompt_override({
  slug:          "customer-reply",
  textContent:   "You are a calm, empathetic support agent. Always acknowledge the customer's frustration first…",
  commitMessage: "OPS-1234 hotfix — calmer tone",
  environment:   "prod"
})
→ { overrideVersion: 8, source: "dashboard" }

# 4. Verify on next runs
list_runs(environment="prod", tag="customer-reply", period="15m")
get_span_details(runId=<first>, spanId=<llm span>)
→ confirm `trigger.llm.model` and response text

# 5. Iterate copy if needed
update_prompt_override({
  slug: "customer-reply",
  textContent: "…tightened copy…",
  commitMessage: "OPS-1234 refinement"
})

# 6. Engineering PR lands, deploy + promote the proper fix
deploy(environment="prod")
promote_prompt_version(slug="customer-reply", version=9, environment="prod")   # new code version

# 7. Remove the temporary override so the code version takes over
remove_prompt_override(slug="customer-reply", environment="prod")
```

---

## TODO — SDK Side

The SDK-facing surface for declaring managed prompts in code (likely `prompt(...)` / `definePrompt(...)` from `@trigger.dev/sdk`, plus a helper for task integration and an AI SDK tool metadata format) is not yet publicly documented. This section will be filled in when Trigger.dev publishes the `/docs/prompts` page. Until then:

- The MCP tools above are the authoritative agent-facing interface.
- To introduce a new prompt into your project, ship it via a normal deploy once the SDK helper is known.
- LLM cost / token usage per prompt can be queried today via the `llm_metrics` TRQL table (see the **observability** skill).
