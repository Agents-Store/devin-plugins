# openclaw.json Key Fields Reference

Complete reference for the most important openclaw.json configuration fields.

---

## agents.defaults

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `workspace` | string | `./workspace` | Agent workspace path (relative to instance root) |
| `model` | string/object | — | Primary LLM model. Format: `"provider/model"`. Object: `{ primary: "provider/model", fallbacks: ["provider/model"] }` |
| `imageModel` | string/object | — | Model for image analysis |
| `bootstrapMaxChars` | number | 20000 | Max chars per workspace file |
| `bootstrapTotalMaxChars` | number | 150000 | Max total chars across all files |
| `userTimezone` | string | — | IANA timezone, e.g., `"America/New_York"` |
| `timeFormat` | string | `"auto"` | `"auto"` / `"12"` / `"24"` |
| `timeoutSeconds` | number | 600 | Session timeout |
| `maxConcurrent` | number | 3 | Max parallel sessions |
| `thinkingDefault` | string | — | `"off"` / `"minimal"` / `"low"` / `"medium"` / `"high"` / `"adaptive"` |
| `contextTokens` | number | 200000 | Context window size |
| `imageMaxDimensionPx` | number | 1200 | Max dimension for image analysis |

## agents.defaults.heartbeat

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `every` | string | — | Interval: `"5m"`, `"10m"`, `"1h"`, `"0m"` to disable |
| `target` | string | — | Delivery target: `"last"` / `"whatsapp"` / `"telegram"` / `"discord"` / `"none"` |
| `model` | string | — | Model for heartbeats (use cheap one) |
| `lightContext` | boolean | — | Minimal context loading |
| `isolatedSession` | boolean | — | Separate session for heartbeats |
| `prompt` | string | — | Custom heartbeat prompt |

## agents.defaults.compaction

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | string | — | Compaction strategy |
| `reserveTokensFloor` | number | — | Reserved tokens before compaction |
| `memoryFlush` | boolean | — | Enable memory flush before compaction |

## agents.defaults.sandbox

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | string | `"off"` | Sandbox mode: `"off"` / `"non-main"` / `"all"` |
| `scope` | string | — | Sandbox scope: `"session"` / `"agent"` / `"shared"` |

## agent (top-level)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skipBootstrap` | boolean | false | Skip workspace file loading. Also available via `--dev` CLI flag |

> **Note**: This is `agent.skipBootstrap` (singular `agent` at root), NOT `agents.defaults.skipBootstrap`.

## agents.list[]

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable agent identifier (required) |
| `default` | boolean | Is this the default agent? |
| `name` | string | Display name |
| `workspace` | string | Override workspace path |
| `model` | string/object | Override model |
| `identity` | object | `{ name, theme, emoji, avatar }` |
| `sandbox` | object | `{ mode }` for sandboxing |

---

## channels.telegram

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | — | Enable Telegram channel |
| `botToken` | string/SecretRef | — | Bot token (use SecretRef: `{ source, provider, id }`) |
| `dmPolicy` | string | — | `"pairing"` / `"allowlist"` / `"open"` / `"disabled"` |
| `allowFrom` | string[] | — | User IDs: `["tg:USER_ID"]` |
| `groups` | object | — | Per-group config (see below) |
| `historyLimit` | number | 50 | Messages to load per session |
| `streaming` | string | — | `"off"` / `"partial"` / `"block"` / `"progress"` |

### channels.telegram.groups[groupId]

| Field | Type | Description |
|-------|------|-------------|
| `requireMention` | boolean | Only respond when @mentioned |
| `allowFrom` | string[] | Allowed users in this group |
| `systemPrompt` | string | Group-specific system prompt |
| `topics` | object | Per-topic configuration |

## channels.discord

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | — | Enable Discord |
| `token` | string/SecretRef | — | Bot token (use SecretRef) |
| `dmPolicy` | string | — | Same as Telegram |
| `allowFrom` | string[] | — | User IDs |
| `guilds` | object | — | Per-guild config |
| `historyLimit` | number | 20 | Messages per session |
| `textChunkLimit` | number | 2000 | Max message length |

## channels.whatsapp

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dmPolicy` | string | — | Access policy |
| `allowFrom` | string[] | — | Phone numbers: `["+15555550123"]` |
| `groupPolicy` | string | — | `"allowlist"` / `"open"` / `"disabled"` |
| `textChunkLimit` | number | 4000 | Max message length |

---

## tools

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `profile` | string | — | `"minimal"` / `"coding"` / `"messaging"` / `"full"` |
| `allow` | string[] | — | Allowed tools (wildcards ok) |
| `deny` | string[] | — | Denied tools |

### tools.exec

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeoutSec` | number | 1800 | Execution timeout |
| `backgroundMs` | number | 10000 | Background task timeout |

### tools.loopDetection

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | false | Enable loop detection |
| `warningThreshold` | number | 10 | Warning trigger count |
| `criticalThreshold` | number | 20 | Critical stop count |

**Tool groups** for `allow`/`deny` lists: `group:runtime`, `group:fs`, `group:sessions`, `group:memory`, `group:web`, `group:ui`, `group:automation`, `group:messaging`, `group:nodes`, `group:openclaw`

---

## plugins

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | true | Enable plugin system |
| `allow` | string[] | — | Plugin allowlist |
| `deny` | string[] | — | Plugin blocklist |
| `load.paths` | string[] | — | Additional plugin load paths |

### plugins.entries[pluginId]

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Enable/disable this plugin |
| `config` | object | Plugin-specific configuration |
| `env` | object | Plugin-scoped environment variables |

**Plugin types**: Native plugins ship `openclaw.plugin.json` and run in-process. Bundle plugins are content packs from Codex/Claude/Cursor ecosystems mapped to native features. Key limitation: Claude `hooks/hooks.json` and `agents` in bundles are **detected but NOT executed**.

**CLI**: `openclaw plugins list/install/enable/disable/inspect`

---

## session

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dmScope` | string | `"main"` | `"main"` / `"per-peer"` / `"per-channel-peer"` / `"per-account-channel-peer"` |
| `mainKey` | string | `"main"` | Default session key identifier |
| `reset.mode` | string | `"daily"` | Session reset mode: `"daily"` |
| `reset.atHour` | number | 4 | Hour to reset (local time on gateway host, 0-23) |
| `reset.idleMinutes` | number | — | Idle window — reset if no activity for this many minutes |
| `resetTriggers` | string[] | `["/new", "/reset"]` | Commands that trigger session reset |
| `maintenance.mode` | string | `"warn"` | `"warn"` (log warnings) / `"enforce"` (auto-prune) |
| `maintenance.pruneAfter` | string | `"30d"` | Prune sessions older than this |
| `maintenance.maxEntries` | number | 500 | Max session entries before pruning |

---

## skills

| Field | Type | Description |
|-------|------|-------------|
| `allowBundled` | string[] | Which bundled skills to enable |
| `load.extraDirs` | string[] | Additional skill directories |
| `entries` | object | Per-skill configuration |

---

## hooks

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `hooks.internal.enabled` | boolean | false | Enable internal hooks (required for BOOT.md execution via `boot-md` hook) |
| `hooks.internal.entries.<name>.enabled` | boolean | true | Enable/disable a specific internal hook by name |

Internal hooks trigger on gateway lifecycle events (e.g., `gateway:startup`). When enabled, BOOT.md is executed on every gateway restart via the `boot-md` hook.

**Bundled hooks**: `session-memory` (saves context on `/new`), `bootstrap-extra-files` (injects extra files during `agent:bootstrap`), `command-logger` (logs commands), `boot-md` (runs BOOT.md on startup).

**Native hook system**: OpenClaw also has a native hook system using `HOOK.md` + `handler.ts` files, discovered from `workspace/hooks/`, `~/.openclaw/hooks/`, and bundled locations. Events: `command:*`, `session:*`, `agent:*`, `gateway:*`, `message:*`. Manage via CLI: `openclaw hooks list/info/enable/disable`.

---

## cron

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `cron.enabled` | boolean | — | Enable/disable the cron system |

> **Note**: `openclaw.json` only contains `cron.enabled`. Cron jobs are managed via the CLI (`openclaw cron add/edit/rm/list/enable/disable/run`) and persisted in `./cron/jobs.json`, NOT in openclaw.json.

**Job format in `./cron/jobs.json`**: Each job has `schedule.kind` (`"at"` / `"every"` / `"cron"`), `schedule.value`, `delivery.mode`, and `prompt`.

---

## gateway

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `gateway.port` | number | 18789 | Gateway HTTP port |
| `gateway.host` | string | — | Bind address |
| `gateway.reload.mode` | string | `"hybrid"` | Config reload mode: `"hybrid"` / `"hot"` / `"restart"` / `"off"` |
| `gateway.auth.token` | string | — | Authentication token for the Gateway API |

Gateway-level configuration. Changes to `gateway.*` fields require a restart (unlike most other fields which hot-reload).

---

## memory

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `memory.embedding.provider` | string | auto | Embedding provider: `"openai"` / `"gemini"` / `"voyage"` / `"mistral"` / `"ollama"` / `"gguf"` |
| `memory.embedding.model` | string | — | Specific embedding model |
| `memory.search.hybrid` | boolean | true | Enable hybrid BM25 + vector search |

The memory system uses hybrid BM25 + vector search with auto-selected embedding provider. Indexes both MEMORY.md and daily logs for semantic retrieval.

---

## env

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `env.vars` | object | — | Inline environment variables (key-value pairs) |
| `env.shellEnv.enabled` | boolean | — | Import shell environment variables into the gateway process |

---

## Config Features

### $include
Split config into multiple files: `"$include": "channels.json"` or `"$include": ["channels.json", "tools.json"]`. Up to 10 levels deep.

### Env var substitution
Use `${VAR_NAME}` in config string values. Only uppercase variable names are matched.

### Schema validation
Strict validation — unknown keys cause Gateway to refuse to start. Only `$schema` is allowed as a non-schema root key.

---

## SecretRef Pattern

For any field containing a secret (tokens, API keys), use:

```json
{
  "source": "env",
  "provider": "default",
  "id": "ENV_VAR_NAME"
}
```

Place actual values in the `.env` file at the instance root. Never put raw secrets inline.
