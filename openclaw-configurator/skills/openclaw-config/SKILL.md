---
name: openclaw-config
description: Comprehensive guide for openclaw.json — the central gateway configuration file controlling models, channels, tools, plugins, and sessions. Use this skill whenever the user needs to understand, modify, or troubleshoot their openclaw.json. Covers agent settings, Telegram/Discord/WhatsApp channel setup, tool profiles, plugin management, session behavior, secret handling with SecretRef, and model configuration. Even questions like "how do I add Telegram", "change the model", or "what does this config field do" need this skill.
---

# openclaw.json Configuration Guide

`openclaw.json` is the central gateway configuration file. Standard location: `~/.openclaw/openclaw.json`. In Docker multi-instance deployments, each instance has its own config at `~/.openclaw-{name}/openclaw.json` (e.g., `~/.openclaw-team/openclaw.json`). It controls models, channels, tools, plugins, sessions, and agent routing. Separate from workspace files — this is infrastructure configuration.

The config uses JSON5 format and has **strict schema validation** — unknown keys cause the Gateway to refuse to start. Only `$schema` is allowed as a non-schema root key.

## Official Documentation

Always verify configuration against official docs. To fetch them, follow the **docs-research** skill — it holds the tool-priority ladder (Firecrawl → Exa → Perplexity → Jina → context7 → WebFetch) and the canonical OpenClaw documentation URL map.

## Editing openclaw.json

The plugin CAN edit `./openclaw.json` with these mandatory safeguards:

1. **Show diff** — always display proposed changes before applying
2. **Ask permission** — require explicit user confirmation
3. **Back up** — `cp ./openclaw.json ./openclaw.json.bak` before any edit
4. **Validate JSON** — check syntax before writing
5. **Run doctor** — `openclaw doctor --fix` after editing (in Docker multi-instance: `openclaw-{name} doctor --fix`)
6. **Never delete sections** — only add or modify existing fields
7. **Fix permissions** — run Docker chown after edits (Docker deployments only)

## Key Sections

### agents — Agent Configuration

```json
{
  "agents": {
    "defaults": {
      "workspace": "./workspace",
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": ["openai/gpt-4o"]
      },
      "bootstrapMaxChars": 20000,
      "bootstrapTotalMaxChars": 150000,
      "userTimezone": "America/New_York",
      "timeFormat": "24",
      "timeoutSeconds": 600,
      "maxConcurrent": 3,
      "heartbeat": {
        "every": "5m",
        "model": "gpt-4o-mini",
        "lightContext": true
      }
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Main Agent",
        "identity": { "name": "Nova", "emoji": "star" }
      }
    ]
  }
}
```

**Key fields:**
- `model` — primary LLM in `provider/model` format (string or `{ primary: "provider/model", fallbacks: [...] }`)
- `bootstrapMaxChars` / `bootstrapTotalMaxChars` — workspace file limits
- `heartbeat.every` — heartbeat interval ("5m", "10m", "1h", "0m" to disable)
- `heartbeat.model` — cheaper model for heartbeats to save tokens
- `heartbeat.target` — heartbeat delivery target: `last | whatsapp | telegram | discord | none`
- `sandbox.mode` — sandbox mode: `off | non-main | all`
- `sandbox.scope` — sandbox scope: `session | agent | shared`

### channels — Communication Platforms

#### Telegram
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": { "source": "env", "provider": "default", "id": "TELEGRAM_BOT_TOKEN" },
      "dmPolicy": "allowlist",
      "allowFrom": ["tg:USER_ID"],
      "groups": {
        "-100GROUP_ID": {
          "requireMention": true,
          "allowFrom": ["tg:USER_ID", "tg:ANOTHER_USER_ID"]
        }
      }
    }
  }
}
```

#### Discord
```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": { "source": "env", "provider": "default", "id": "DISCORD_BOT_TOKEN" },
      "dmPolicy": "allowlist",
      "allowFrom": ["discord:USER_ID"],
      "guilds": {
        "GUILD_ID": {
          "requireMention": true
        }
      }
    }
  }
}
```

#### WhatsApp
```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "allowFrom": ["+15555550123"],
      "groupPolicy": "allowlist"
    }
  }
}
```

**Common channel fields:**
- `dmPolicy` — "pairing" | "allowlist" | "open" | "disabled"
- `allowFrom` — user ID allowlist (format: `"tg:ID"`, `"discord:ID"`, phone number)
- `groups` — per-group configuration with `requireMention`, `allowFrom`

### tools — Tool Access Control

```json
{
  "tools": {
    "profile": "full",
    "allow": ["*"],
    "deny": ["dangerous_tool"],
    "exec": {
      "timeoutSec": 1800,
      "backgroundMs": 10000
    },
    "loopDetection": {
      "enabled": true,
      "warningThreshold": 10,
      "criticalThreshold": 20
    }
  }
}
```

**Profiles:** `"minimal"` | `"coding"` | `"messaging"` | `"full"`

### plugins — Plugin Management

```json
{
  "plugins": {
    "enabled": true,
    "allow": ["plugin-a", "plugin-b"],
    "deny": [],
    "load": { "paths": ["/custom/plugin/path"] },
    "entries": {
      "my-plugin": {
        "enabled": true,
        "config": { "apiKey": { "source": "env", "provider": "default", "id": "PLUGIN_API_KEY" } }
      }
    }
  }
}
```

### session — Session Behavior

```json
{
  "session": {
    "dmScope": "main",
    "mainKey": "main",
    "reset": {
      "mode": "daily",
      "atHour": 4,
      "idleMinutes": 60
    },
    "resetTriggers": ["/new", "/reset"],
    "maintenance": {
      "mode": "warn",
      "pruneAfter": "30d",
      "maxEntries": 500
    }
  }
}
```

**dmScope options:** `"main"` | `"per-peer"` | `"per-channel-peer"` | `"per-account-channel-peer"`
**reset.mode:** `"daily"` — resets at `atHour` (default 4 AM local). `idleMinutes` is a separate idle window.
**maintenance.mode:** `"warn"` (log warnings) | `"enforce"` (auto-prune stale sessions)

## Secret Handling — SecretRef Pattern

**Never put raw secrets in openclaw.json.** Use the SecretRef pattern:

```json
{
  "source": "env",
  "provider": "default",
  "id": "ENV_VAR_NAME"
}
```

Place actual values in `.env` file at the instance root.

**Known issue**: `openclaw doctor` may show `unresolved SecretRef` errors when running outside gateway runtime. This is safe to ignore.

If inline secrets are found during audit, warn the user and recommend migration to SecretRef.

## Relationship to Workspace Files

| openclaw.json | Informs Which Workspace File |
|---------------|------------------------------|
| `agents.defaults.model` | TOOLS.md (model-specific tool notes) |
| `channels.telegram.groups` | AGENTS.md (group chat rules per group) |
| `channels.*.allowFrom` | USER.md (map IDs to user names) |
| `tools.profile` | TOOLS.md (available tool categories) |
| `plugins.entries` | AGENTS.md (plugin-specific behavior rules) |
| `agents.defaults.heartbeat` | HEARTBEAT.md (aligns with heartbeat config) |
| `agents.defaults.userTimezone` | USER.md (timezone), HEARTBEAT.md (quiet hours) |

## What to Check When Optimizing

1. **Model selection** — is the primary model appropriate for the domain?
2. **Channel configuration** — are all active channels properly configured?
3. **User allowlists** — do they match the users in USER.md?
4. **Heartbeat settings** — interval appropriate? Using cheap model?
5. **Tool profile** — "full" vs "minimal" based on agent's needs?
6. **Plugin entries** — are all needed plugins enabled?
7. **Bootstrap limits** — workspace files staying under limits?
8. **Secret handling** — all secrets use SecretRef pattern?
9. **Loop detection** — enabled for production stability?
10. **dmPolicy** — "allowlist" for production (not "open")?

See `references/config-reference.md` for the complete field reference.

## Config Splitting — $include

Split large configs into multiple files:

```json
{
  "$include": "channels.json"
}
```

Or include multiple files:
```json
{
  "$include": ["channels.json", "tools.json"]
}
```

Supports up to 10 levels of nesting.

## Env Var Substitution

Use `${VAR_NAME}` syntax in config string values. Only uppercase variable names are matched:

```json
{
  "agents": {
    "defaults": {
      "workspace": "${WORKSPACE_PATH}"
    }
  }
}
```

## Config Hot Reload

The Gateway watches `openclaw.json` for changes. Most fields hot-apply automatically. Gateway-level fields (`gateway.*`) require a restart. Default reload mode is `hybrid` — auto-restarts for critical changes only.

Configure reload behavior:
```json
{
  "gateway": {
    "reload": {
      "mode": "hybrid"
    }
  }
}
```

Modes: `"hybrid"` (default) | `"hot"` | `"restart"` | `"off"`

## Best Practices

1. Keep secrets (tokens, API keys) in env vars via SecretRef pattern
2. Use `allowlist` dmPolicy for production agents
3. Set `heartbeat.model` to a cheap model
4. Configure `userTimezone` to match primary user
5. Enable `loopDetection` for production stability
6. Review `maxConcurrent` based on usage patterns
7. Always back up before editing: `cp ./openclaw.json ./openclaw.json.bak`
8. Run `openclaw doctor --fix` after any changes (Docker multi-instance: `openclaw-{name} doctor --fix`)
9. Fix Docker permissions after edits (Docker deployments only)
10. Use `$include` to split large configs into separate files
11. Use `${VAR_NAME}` syntax for env var substitution in string values
