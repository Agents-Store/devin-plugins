---
name: config-validation
description: Validates openclaw.json against official OpenClaw documentation and checks for latest features, deprecated settings, and security issues. Use this skill whenever the user wants to verify their configuration is correct, check if they're using the latest OpenClaw features, audit their openclaw.json for problems, or compare their config against best practices. Also applies when the user says things like "is my config OK", "what am I missing in my setup", or "check my OpenClaw configuration".
---

# openclaw.json Configuration Validation

Validate `openclaw.json` against the official OpenClaw documentation and check for latest features, deprecated settings, and optimal configurations.

## Official Documentation Sources

When validating configuration, fetch the latest information using the **docs-research** skill — it holds the tool-priority ladder (Firecrawl → Exa → Perplexity → Jina → context7 → WebFetch) and the canonical OpenClaw documentation URL map (docs site, source/changelog, skills examples).

Always verify against official docs before recommending changes. OpenClaw evolves — features may be added or deprecated.

## Validation Checklist

### 1. Structure Validation

Verify top-level sections exist and are well-formed:

```
{
  "agents": { ... },        // Required
  "channels": { ... },      // At least one channel needed
  "tools": { ... },         // Recommended
  "plugins": { ... },       // Optional
  "session": { ... }        // Optional
}
```

### 2. agents.defaults

| Field | Check | Severity |
|-------|-------|----------|
| `model` | Is it set? Is the model name valid and current? | HIGH |
| `workspace` | Defaults to `./workspace` — verify path exists | MEDIUM |
| `bootstrapMaxChars` | Default 20000. Warn if > 50000 (token cost) | LOW |
| `bootstrapTotalMaxChars` | Default 150000. Warn if > 300000 | LOW |
| `userTimezone` | Is it set? Valid IANA timezone? | MEDIUM |
| `timeoutSeconds` | Default 600. Warn if > 1800 | LOW |
| `maxConcurrent` | Default 3. Check based on usage | LOW |
| `contextTokens` | Should match model's context window | MEDIUM |
| `thinkingDefault` | Valid values: off/minimal/low/medium/high/adaptive | LOW |

### 3. agents.defaults.heartbeat

| Field | Check | Severity |
|-------|-------|----------|
| `every` | Is interval reasonable? (5m-1h typical) | MEDIUM |
| `model` | Using a cheap model? (gpt-4o-mini, haiku recommended) | MEDIUM |
| `lightContext` | Should be `true` for token efficiency | LOW |
| `isolatedSession` | Recommended `true` to avoid session pollution | LOW |

### 4. agents.defaults.compaction

| Field | Check | Severity |
|-------|-------|----------|
| `memoryFlush` | Should be `true` for agents with memory | MEDIUM |
| `reserveTokensFloor` | 8000 is recommended minimum | LOW |

### 5. agents.list[]

| Field | Check | Severity |
|-------|-------|----------|
| `id` | Each agent has a unique ID? | HIGH |
| `default` | Exactly one agent is default? | HIGH |
| `identity` | Name, emoji set? | LOW |
| `sandbox.mode` | Set for untrusted environments? | MEDIUM |

### 6. channels.*

For each configured channel (telegram, discord, whatsapp):

| Field | Check | Severity |
|-------|-------|----------|
| `enabled` | Is it intentionally enabled/disabled? | MEDIUM |
| `botToken` / `token` | Uses SecretRef pattern? (see security-audit skill) | CRITICAL |
| `dmPolicy` | Not `"open"` in production? Prefer `"allowlist"` | HIGH |
| `allowFrom` | Matches USER.md profiles? | MEDIUM |
| `groups` / `guilds` | Per-group config set for each group? | LOW |
| `historyLimit` | Reasonable value? (20-100) | LOW |

### 7. tools

| Field | Check | Severity |
|-------|-------|----------|
| `profile` | Appropriate for use case? `full` needs justification | MEDIUM |
| `deny` | Dangerous tools blocked? | MEDIUM |
| `exec.timeoutSec` | Not too high (< 3600 recommended) | LOW |
| `loopDetection.enabled` | `true` for production | HIGH |

### 8. plugins

| Field | Check | Severity |
|-------|-------|----------|
| `enabled` | Plugin system active? | LOW |
| `entries` | Each plugin has valid config? | MEDIUM |
| `entries.*.env` | Uses env vars for secrets? | HIGH |

### 9. session

| Field | Check | Severity |
|-------|-------|----------|
| `dmScope` | Appropriate? Options: `main/per-peer/per-channel-peer/per-account-channel-peer` | LOW |
| `reset.mode` | Set to `"daily"`? (only valid value) | LOW |
| `reset.atHour` | Reasonable reset hour? (default 4) | LOW |
| `reset.idleMinutes` | Reasonable idle timeout? | LOW |
| `resetTriggers` | Includes `/new` or `/reset`? | LOW |
| `maintenance.mode` | `"warn"` or `"enforce"`? | LOW |

## Cross-Validation with Workspace Files

| openclaw.json | Workspace File | Check |
|---------------|---------------|-------|
| `channels.*.allowFrom` IDs | USER.md | Every ID in allowFrom has a profile in USER.md |
| `agents.defaults.model` | TOOLS.md | Model-specific tool notes exist |
| `channels.telegram.groups` | AGENTS.md | Group chat rules exist for each group |
| `agents.defaults.heartbeat` | HEARTBEAT.md | Heartbeat config aligns with HEARTBEAT.md tasks |
| `agents.defaults.userTimezone` | USER.md | Timezone matches user profile |
| `plugins.entries` | AGENTS.md | Plugin-specific behavior rules exist |

## Feature Freshness Check

After fetching latest docs, check for:

1. **New config fields** not present in current config
2. **Deprecated fields** that should be migrated
3. **New channel types** available but not configured
4. **New tool profiles** or options
5. **New compaction strategies** or memory features
6. **Model updates** — newer models available

## Validation Report Template

```markdown
# openclaw.json Validation Report

## Config Summary
- Model: [primary model]
- Channels: [list of enabled channels]
- Tools profile: [profile]
- Heartbeat: [interval] with [model]

## Validation Results

### CRITICAL
- [ ] [Issue + recommendation]

### HIGH
- [ ] [Issue + recommendation]

### MEDIUM
- [ ] [Issue + recommendation]

### LOW / Suggestions
- [ ] [Optional improvement]

## Cross-Validation
- [ ] USER.md ↔ allowFrom: [match/mismatch]
- [ ] HEARTBEAT.md ↔ heartbeat config: [aligned/misaligned]
- [ ] AGENTS.md ↔ group configs: [covered/missing]

## Feature Freshness
- [ ] Current version features: [all used / N missing]
- [ ] Deprecated settings: [none / list]
- [ ] Recommended additions: [list]
```

## Best Practices

1. Always validate after editing openclaw.json
2. Run `openclaw doctor --fix` after changes (Docker multi-instance: `openclaw-{name} doctor --fix`)
3. Check official docs for latest features quarterly
4. Keep model names current — use `provider/model` format (e.g. `anthropic/claude-sonnet-4-20250514`)
5. Use `allowlist` dmPolicy in production
6. Enable loopDetection for stability
7. Set heartbeat to a cheap model, configure `heartbeat.target`
8. Match userTimezone to primary user's location
9. Verify `agent.skipBootstrap` path (singular `agent`, NOT `agents.defaults.skipBootstrap`)
10. Cron jobs are managed via CLI, config only has `cron.enabled`
