---
name: ai-assist
description: "This skill should be used when the user wants AI-powered deployment debugging on Dokploy — wiring up an LLM provider (OpenAI, Anthropic, Gemini, Ollama, OpenRouter, etc.), summarising build logs with AI, or asking Dokploy for a next-step suggestion. Triggers: \"analyze my failed deploy with AI\", \"ai analyze logs dokploy\", \"set up dokploy ai\", \"configure ai provider in dokploy\", \"why is dokploy not suggesting fixes\", \"dokploy ai-analyzeLogs\", \"dokploy ai-suggest\"."
---

# Dokploy AI Assistant Integration

Dokploy v0.29 introduced an **AI router** that lets the server call out to an LLM provider to (a) analyse a failed deployment's build log and (b) suggest next steps. The `ai-*` MCP tools are how plugins drive that integration.

This skill teaches: which providers Dokploy supports, how to wire one up, how to invoke the two flagship endpoints (`analyzeLogs` and `suggest`), and what to do when AI is **not** configured.

> The AI router calls run **on the Dokploy server**, not locally — Dokploy holds the provider credentials. The MCP tools just orchestrate.

---

## Tool inventory

| Tool | Purpose |
|---|---|
| `mcp__dokploy__ai-getEnabledProviders` | List provider integrations that are *both* configured and enabled. If empty, no AI is available |
| `mcp__dokploy__ai-getModels` | List models a candidate endpoint advertises. Takes `{ apiUrl, apiKey }` (NOT `aiId`) |
| `mcp__dokploy__ai-getAll` | List all configured providers (enabled or not) |
| `mcp__dokploy__ai-get` / `mcp__dokploy__ai-one` | Read one provider's config |
| `mcp__dokploy__ai-create` | Add a new provider (API key + model + endpoint) |
| `mcp__dokploy__ai-update` | Update an existing provider's config |
| `mcp__dokploy__ai-delete` | Remove a provider |
| `mcp__dokploy__ai-testConnection` | Validate a candidate payload BEFORE saving. Takes `{ apiUrl, apiKey, model }` (NOT `aiId`) |
| `mcp__dokploy__ai-getCustomProviders` | List org-defined custom provider presets (v0.29.13+) |
| `mcp__dokploy__ai-saveCustomProviders` | Save org custom provider presets: `{ providers }` |
| `mcp__dokploy__ai-deploy` | (Dokploy admin) deploy the AI orchestrator side-service |
| `mcp__dokploy__ai-analyzeLogs` | **Headline feature:** summarise log **text you pass in** with the configured LLM, return root-cause + suggested fix. Signature: `{ aiId, logs, context: "build"\|"runtime" }` — NOT `{ deploymentId }` |
| `mcp__dokploy__ai-suggest` | Ask the LLM for next-step recommendations. Signature: `{ aiId, input, serverId? }` — `input` is the question/state text |

---

## Step 1 — Check whether AI is already configured

Always do this first. If a provider already exists and is enabled, skip ahead to Step 3.

```
mcp__dokploy__ai-getEnabledProviders
```

| Response | Meaning |
|---|---|
| Non-empty array | At least one provider is live — record the `aiId` of the one you'll use |
| Empty array | No provider is enabled — either no provider exists, or all are disabled. Continue to Step 2 |

Cross-check with `ai-getAll` if the enabled list is empty — there may be providers configured but turned off (`isEnabled: false`).

---

## Step 2 — Configure a provider (only if none enabled)

Dokploy's AI router is provider-agnostic — anything that speaks the OpenAI chat-completions API works. Common choices:

| Provider | `apiUrl` value | Notes |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | Use models like `gpt-4o-mini` for cost/speed |
| Anthropic (via proxy) | `https://api.anthropic.com/v1` | Many users front Claude with an OpenAI-compatible proxy |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | OpenAI-compatible endpoint exposed by Google |
| OpenRouter | `https://openrouter.ai/api/v1` | Single key, many models — convenient for mixing |
| Groq | `https://api.groq.com/openai/v1` | Cheap & fast for log triage |
| Ollama (self-hosted) | `http://<host>:11434/v1` | No API key required; model must be pulled on the server |
| Self-hosted (vLLM, LM Studio, etc.) | provider-specific | Same shape — OpenAI-compatible |

### Test, then create the provider

`ai-testConnection` and `ai-getModels` take the **candidate payload** (`apiUrl` + `apiKey`), not an `aiId` — so test BEFORE saving:

```
1. mcp__dokploy__ai-testConnection
   → { apiUrl: "https://api.openai.com/v1", apiKey: "<secret>", model: "gpt-4o-mini" }
   → returns { ok: true/false, error?: string }

2. mcp__dokploy__ai-create        # only after the test passes
   → {
       name: "openai-prod",
       apiKey: "<secret>",
       apiUrl: "https://api.openai.com/v1",
       model: "gpt-4o-mini",
       isEnabled: true
     }
   → returns { aiId }

3. (optional) mcp__dokploy__ai-getModels
   → { apiUrl: "https://api.openai.com/v1", apiKey: "<secret>" }   # NOT aiId
   → returns the endpoint's model list; useful if you want to switch the chosen model
```

If `testConnection` returns `ok: false`, do not move on. Common causes:

- Wrong `apiUrl` (forgot `/v1`, used the wrong path).
- Invalid / expired API key.
- Self-hosted endpoint not reachable from the Dokploy server's network namespace.

Disable rather than delete a misconfigured provider with `ai-update` `{ aiId, isEnabled: false }` — that way audit history is preserved.

---

## Step 3 — Analyse a failed deployment

This is the canonical workflow used by the [`debug-deploy`](../debug-deploy/SKILL.md) skill and the `/dokploy-dev:analyze` command. **`ai-analyzeLogs` does not fetch logs for you — you fetch the text first** (via the [`read-logs`](../read-logs/SKILL.md) skill) and pass it in.

```
1. Pick an enabled provider
   aiId = first entry from  mcp__dokploy__ai-getEnabledProviders

2. Fetch the log text (read-logs skill)
   build failure   → mcp__dokploy__deployment-readLogs { deploymentId, tail: 1000 }   → context: "build"
   app runtime     → mcp__dokploy__application-readLogs { applicationId, tail: 500 }   → context: "runtime"
   compose runtime → loop compose-readLogs per container, concatenate                 → context: "runtime"

3. Analyse
   mcp__dokploy__ai-analyzeLogs
     → { aiId, logs: "<the text from step 2>", context: "build" | "runtime" }
     → returns a root-cause summary + suggested fix

4. Apply the suggested fix
   → Update env vars / build type / Dockerfile / domain config, then `application-redeploy` / `compose-redeploy`
```

The response is a free-form LLM summary. Read it critically — the LLM doesn't *know* your codebase, only the log text you sent. If the suggestion contradicts what the log clearly shows, trust the log.

### Cost / latency note

You control how much log goes to the LLM via the `tail` parameter when you fetch it. A stuck container restarting for hours can produce huge logs — keep `tail` modest (e.g. 500–1000) or use `search` to pre-filter to error lines before passing the text to `ai-analyzeLogs`, so you don't blow past the provider's context window.

---

## Step 4 — Open-ended suggestions

When there's no specific failure but you want guidance ("what should I tighten on this app before going to production?"):

```
mcp__dokploy__ai-suggest
  → { aiId: "<enabled provider>", input: "<the question / state description text>", serverId?: "<optional>" }
  → returns suggestions
```

`ai-suggest` differs from `ai-analyzeLogs` in that `input` is a free-form question or state description you compose (there is no `applicationId`/`prompt` form) — describe the app's config, env, and recent history in the `input` text. Use it for:

- "Is my health-check configured correctly?"
- "Should I switch this from Nixpacks to Dockerfile?"
- "Recommend env vars I might be missing for Next.js production."
- "Anything dangerous about my Traefik labels?"

---

## Fallback: when AI is not available

If you cannot enable a provider (offline server, no budget, policy), the debugging workflow still works without AI — it just falls back to the manual log-grep patterns in [`debug-deploy`](../debug-deploy/SKILL.md) Step 2.

Communicate this to the user explicitly:

> "Dokploy AI is not configured. I'll work through the build log manually. To enable AI-summarised analysis later, configure a provider via `ai-create` (see the `ai-assist` skill)."

Do not block on AI. The plugin must remain useful without it.

---

## Security / privacy considerations

- **Provider sends build logs externally** — build logs can contain env var values from `RUN echo $SECRET >> build.log`-style mistakes. Audit before sending sensitive logs to a third-party LLM.
- **Self-hosted Ollama / vLLM** is the most privacy-preserving option for regulated workloads.
- **API keys live in Dokploy** — `ai-getAll` returns them masked. Rotate via `ai-update` if you suspect leakage.
- **Audit log** — every `ai-analyzeLogs` / `ai-suggest` call is recorded in `auditLog-all`. Useful for cost attribution.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ai-getEnabledProviders` empty after `ai-create` | Provider created with `isEnabled: false` | `ai-update { aiId, isEnabled: true }` |
| `ai-testConnection` ok but `ai-analyzeLogs` times out | Log too large for provider context window | Switch to a larger-context model via `ai-update`, or truncate the log |
| `ai-analyzeLogs` returns generic advice | Log was empty or only contained Dokploy framing | Confirm the deployment actually produced output — check `deployment-all`'s `logPath` |
| 401 / 403 from `analyzeLogs` only | Provider key revoked or org rate-limited | Re-test with `ai-testConnection`; rotate key |
| Tool not found (`mcp__dokploy__ai-…`) | `DOKPLOY_ENABLED_TAGS` is filtering it out | Add `ai` to the tag list in `.mcp.json` `env` |
| Dokploy is older than v0.29 | AI router not yet present | Upgrade Dokploy server; the official `@dokploy/mcp` requires v0.29+ for the `ai` router. Custom provider presets (`ai-getCustomProviders`/`ai-saveCustomProviders`) need >= v0.29.13 |

---

## See also

- [`debug-deploy`](../debug-deploy/SKILL.md) — chains `ai-analyzeLogs` into the broader failure workflow
- [`api-reference/references/ai-and-debugging.md`](../api-reference/references/ai-and-debugging.md) — REST API surface for the `ai` router
- `/dokploy-dev:analyze` command — one-shot wrapper around `ai-analyzeLogs` for the most recent failed deploy
