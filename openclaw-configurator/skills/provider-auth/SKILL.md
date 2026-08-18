---
name: provider-auth
description: How to authenticate OpenClaw model providers — API key vs OAuth vs CLI backend — with a cost-saving, OAuth/CLI-first bias for Claude and Codex. Use whenever the user is setting up or changing model-provider credentials, asks to "stop paying per-token for chat", wants OAuth keys for Claude/Codex, mentions auth-profiles.json, the Claude CLI backend, `openclaw models auth`, or "which auth method should I use". Pairs with the /provider-setup command.
---

# Model Provider Authentication

How OpenClaw authenticates to model providers, and how to pick the cheapest working method. Auth methods change between releases — **always re-verify the current recommended path via the docs-research skill** (`/gateway/authentication`, `/providers/anthropic`, `/providers/openai`, `/concepts/oauth`, `/concepts/model-providers`, `/gateway/cli-backends`) before recommending a change.

## Decision Principle — cost first

OpenClaw can talk to a provider in two ways:

- **Embedded API** — OpenClaw sends HTTP requests directly using an API key or token. Billed as **metered API tokens** (pay-as-you-go).
- **CLI backend** — OpenClaw shells out to a locally installed provider CLI (`claude`, `codex`, `gemini`). The CLI owns its own OAuth session and refreshes tokens automatically. Usage bills against that **CLI subscription session**, not metered API tokens.

**Prefer a CLI backend (or provider OAuth) for chat models** so you don't pay per-token for everyday agent conversations. **Reserve API keys for the places that genuinely need programmatic API access** — embedding/memory providers, batch jobs, and skills/plugins whose tools call an API directly. Those exceptions stay as `.env`/SecretRef values.

> When a working, bug-free local CLI login exists on the gateway host, route chat through it. Fall back to an API key only when the CLI path is unavailable or broken.

## Auth-Method Matrix

| Provider | Preferred (cheap) | Fallback | Model ref |
|----------|-------------------|----------|-----------|
| Anthropic / Claude | **Claude CLI backend** (reuse `claude` login) | API key | `anthropic/claude-opus-4-7` + runtime `claude-cli` |
| OpenAI / Codex | **ChatGPT OAuth** (`openai-codex`) | API key | `openai/gpt-5.5` (native Codex harness) |
| Google / Gemini | Gemini CLI backend / OAuth | API key | `google/gemini-*` (+ runtime `google-gemini-cli`) |
| OpenRouter & others | API key / `paste-token` | — | `openrouter/<model>` |

### Anthropic / Claude — Claude CLI backend (preferred)

Reuse an existing Claude Code CLI login on the gateway host (no separate API key, automatic token refresh):

```bash
# On the gateway host:
claude auth login                 # interactive — run via the ! prefix or your own shell
claude auth status --text         # confirm logged in
openclaw models auth login --provider anthropic --method cli --set-default
openclaw models set anthropic/claude-opus-4-7   # canonical model ref
```

Keep the model ref **canonical** (`anthropic/claude-opus-4-7`) and select the CLI backend separately via a model-scoped runtime: `agentRuntime.id: "claude-cli"`. Legacy `claude-cli/*` refs migrate back to canonical (doctor records the runtime separately). If `claude` is not on `PATH`, set `agents.defaults.cliBackends.claude-cli.command` to the real binary path.

*API key (only when a function/skill needs the embedded API):*

```bash
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
# or, to register an env-provided key:
openclaw models auth add --provider anthropic --method api-key
```

Store the key as `ANTHROPIC_API_KEY` in `~/.openclaw/.env` (or via SecretRef) — never inline in `openclaw.json`.

### OpenAI / Codex — ChatGPT OAuth (preferred)

```bash
openclaw models auth login --provider openai-codex   # PKCE OAuth; browser → callback http://127.0.0.1:1455/auth/callback
# headless host: paste the full redirect URL when prompted
openclaw models set openai/gpt-5.5
```

Configure `openai/gpt-5.5`: `openai/*` agent turns select the native Codex app-server harness by default (the usual ChatGPT/Codex subscription setup). Legacy `openai-codex/<model>` and `codex-cli/*` refs are rewritten to `openai/*` by `openclaw doctor`. OpenClaw refreshes the OAuth token automatically before expiry.

### Google / Gemini, OpenRouter, others

```bash
openclaw models auth add --provider google --method api-key   # reads GOOGLE_API_KEY
openclaw models auth paste-token --provider openrouter        # manual token entry
openclaw models set google/gemini-3.1-pro
```

Gemini also supports a CLI backend (runtime `google-gemini-cli`) analogous to `claude-cli`.

## auth-profiles.json — the token sink

OpenClaw stores provider credentials in `~/.openclaw/agents/main/agent/auth-profiles.json` (Docker multi-instance: `/root/.openclaw-{name}/agents/main/agent/auth-profiles.json`). One entry per profile, e.g.:

```json
{
  "anthropic:claude-cli": {
    "type": "token",
    "provider": "anthropic",
    "managedBy": "claude-cli"
  }
}
```

**Switching gotcha:** if a previous embedded-API token profile exists (`mode: "token"`, e.g. `auth.profiles.anthropic:claude`), OpenClaw **prefers the embedded API over the CLI backend** while it exists. To fully switch to the CLI backend, remove it:

```bash
openclaw config unset auth.profiles.anthropic:claude
openclaw config unset agents.defaults.cliBackends.anthropic   # let plugin defaults take over
```

**Security:** read `auth-profiles.json` to learn *which* profiles and modes exist — never print or copy token **values** into chat context.

## models.json / models.providers — only for custom providers

Built-in providers (Anthropic, Codex, Google, etc.) need **no** `models.providers` config — just set auth + pick a model ref. Use `models.json` / `models.providers` only to add **custom** providers or OpenAI/Anthropic-compatible proxies.

## Verification

```bash
openclaw models status                              # shows profiles + credential type (oauth/api-key) + expiry
openclaw models list --provider anthropic           # confirms the model is available
openclaw models auth list --provider openai-codex   # confirms a usable Codex OAuth profile
openclaw config get agents.defaults.model --json    # confirms default model + runtime
openclaw doctor                                      # surfaces routing/legacy issues (Docker: openclaw-{name} doctor)
```

## Cross-links

- Apply any `openclaw.json` edits with the **openclaw-config** safeguards (diff → confirm → backup → validate JSON → run doctor).
- OAuth credentials and CLI tokens live in OpenClaw's **encrypted store / auth-profiles.json**, NOT in Infisical — see **infisical-migration** (out of scope for Infisical; only `.env`/SecretRef API keys are migrated).
- Auth changes are a frequent **upgrade** surface — see **release-migration**.
- Fetch all docs via **docs-research**.
