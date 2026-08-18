---
name: workspace-overview
description: OpenClaw workspace architecture and file system overview — directory structure, file loading mechanics, character limits, scan categories (A-J), and subfolder organization patterns. Use this skill whenever the user asks about how the workspace is structured, what files get loaded automatically, character limits, what goes where, or how to organize their workspace. This is the foundational skill — use it first when the user is new to OpenClaw or asks broad questions about workspace organization, even before more specific skills like agents-md or soul-md.
---

# OpenClaw Workspace Architecture

This skill covers the structure, loading mechanics, and organization of an OpenClaw agent workspace.

## Instance Directory Structure

**Standard layout**: `~/.openclaw/` (single instance). Multi-profile via `OPENCLAW_PROFILE` env var creates `~/.openclaw/workspace-<profile>`.

**Docker multi-instance layout**: Each instance lives at `~/.openclaw-{name}/` (e.g. `~/.openclaw-nova/`). This is a deployment convention for running multiple OpenClaw instances, each with its own config and workspace.

### Instance dir vs Project dir

For Docker deployments these are two **different** directories:

| Concept | Env var | Typical path | Holds |
|---------|---------|--------------|-------|
| **Instance dir** (runtime) | `OPENCLAW_INSTANCE_DIR` | `~/.openclaw-{name}/` | `openclaw.json`, `workspace/`, `agents/`, `memory/`, `logs/` |
| **Project dir** (source) | `OPENCLAW_PROJECT_DIR` | `/docker/openclaw-{name}/` | git checkout, `docker-compose.yaml`, migrations |

**Resolution priority used by workspace-aware commands** (`workspace-scan`, `config-validate`, `workspace-optimize`, the permissions hook):

```
OPENCLAW_INSTANCE_DIR  >  OPENCLAW_PROJECT_DIR  >  $(pwd)
```

`OPENCLAW_PROJECT_DIR` alone is used by `instance-update` (git pull / rebuild) and as the `docker compose` working dir when fixing permissions. All other commands target the instance dir. When both are unset, the plugin falls back to CWD and the legacy single-instance layout still works.

All paths below are relative to the resolved instance dir.

```
./                              # Instance root (~/.openclaw-{name}/)
├── workspace/                  # Workspace files (auto-injected)
│   ├── AGENTS.md               # Operating rules, procedures
│   ├── SOUL.md                 # Persona, tone, boundaries
│   ├── USER.md                 # User profiles, preferences
│   ├── IDENTITY.md             # Agent name, emoji, avatar
│   ├── TOOLS.md                # Tool notes, priorities
│   ├── HEARTBEAT.md            # Background task checklist
│   ├── MEMORY.md               # Curated long-term memory
│   ├── BOOT.md                 # Gateway restart instructions
│   ├── BOOTSTRAP.md            # First-run ritual (deleted after)
│   ├── docs/                   # On-demand reference files
│   │   ├── rules/              # Extended rules
│   │   ├── procedures/         # Task-specific guides
│   │   ├── clients/            # Client profiles
│   │   └── standing-orders/    # Recurring autonomous tasks
│   ├── workflows/              # .prose workflow files
│   ├── canvas/                 # Canvas UI files (optional)
│   ├── memory/                 # Daily logs (auto-created)
│   └── skills/                 # Instance-specific skills
├── agents/
│   └── main/
│       └── sessions/
│           ├── sessions.json   # Session index
│           └── *.jsonl         # Session transcripts
├── memory/
│   └── main.sqlite             # Hybrid BM25 + vector search index (auto-built)
├── cron/
│   └── jobs.json               # Scheduled jobs
├── logs/
│   └── openclaw.log            # Gateway log
├── openclaw.json               # Central gateway configuration
├── credentials/                # DO NOT SCAN
├── telegram/                   # DO NOT SCAN
├── devices/                    # DO NOT SCAN
├── subagents/                  # DO NOT SCAN
├── completions/                # DO NOT SCAN
├── delivery-queue/             # DO NOT SCAN
├── media/                      # DO NOT SCAN
├── identity/                   # DO NOT SCAN
├── config.yaml                 # DO NOT SCAN
└── *.bak*                      # DO NOT SCAN
```

### Shared Resources

**Standard paths:**
```
~/.openclaw/skills/*/SKILL.md               # Managed/local skills
```

**Docker deployment paths** (deployment-specific, may vary):
```
/root/openclaw-skills/*/SKILL.md            # Shared public skills
/root/openclaw-private-skills/*/SKILL.md    # Shared private skills
/root/openclaw-plugins/packages/*/          # Shared public plugins
/root/openclaw-plugins-private/packages/*/  # Shared private plugins
```

Additional skill directories via `skills.load.extraDirs` in openclaw.json.

**ClawHub** (clawhub.com) is the public registry for discovering and sharing skills and plugins.

## Scan Categories (A–J + Shared)

| Cat | Target | Path | Mode |
|-----|--------|------|------|
| A | Auto-injected workspace files (7 core) | `./workspace/AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `MEMORY.md` | Read + Write |
| A+ | BOOT.md (hook-executed, not injected) | `./workspace/BOOT.md` (optional, persistent) | Read + Write |
| A++ | BOOTSTRAP.md (auto-injected when present) | `./workspace/BOOTSTRAP.md` (temporary, deleted after bootstrap) | Read + Write |
| B | Memory files | `./workspace/memory/*.md` + `./workspace/MEMORY.md` | Read + Write |
| C | Instance skills | `./workspace/skills/*/SKILL.md` | Read only |
| D | Subfolders (on-demand) | `./workspace/docs/**/*.md` + `./workspace/workflows/**/*.prose` | Read + Write |
| E | Config | `./openclaw.json` | Read + Write (with permission) |
| F | Sessions | `./agents/main/sessions/sessions.json` + `*.jsonl` | Read only |
| G | Memory index | `./memory/main.sqlite` | Read only (vector search index) |
| H | Cron | `./cron/jobs.json` | Read only |
| I | Logs | `./logs/openclaw.log` | Read only |
| J | Canvas | `./workspace/canvas/` | Read + Write |
| — | Managed skills | `~/.openclaw/skills/*/SKILL.md` (standard) or `/root/openclaw-skills/*/SKILL.md` (Docker) | Read only |
| — | Extra skill dirs | Paths from `skills.load.extraDirs` in openclaw.json | Read only |

**Write scope**: The plugin creates/edits files in `./workspace/` and `./openclaw.json` (with explicit user permission). Everything else is read-only for analysis.

## DO NOT SCAN — Excluded Directories

These contain sensitive/internal data (OAuth tokens, session state, device pairing, certs) — reading them risks exposing secrets in LLM context. Do not scan:

- `./credentials/` — OAuth tokens, API keys
- `./telegram/` — Telegram session state
- `./devices/` — device pairing data
- `./subagents/` — internal subagent state
- `./completions/` — LLM completion cache
- `./delivery-queue/` — message delivery queue
- `./media/` — media file cache
- `./identity/` — certificates and identity data
- `./config.yaml` — internal gateway config
- `./*.bak*` — backup files
- `./memory/main.sqlite-wal` — sqlite WAL (do not touch)
- `./memory/main.sqlite-shm` — sqlite shared memory (do not touch)

## Auto-Injected Files (loaded every session)

These 7 files are injected into the agent's context window on every turn — they consume tokens constantly. The `bootstrapMaxChars` and `bootstrapTotalMaxChars` limits apply to these files.

| File | Purpose | Injection Scope |
|------|---------|-----------------|
| `AGENTS.md` | Operating rules, priorities, behavioral guidance | Every session + sub-agents |
| `SOUL.md` | Persona, tone, boundaries, values | Main sessions only |
| `USER.md` | User identity, preferences, context | Main sessions only |
| `IDENTITY.md` | Agent name, vibe, emoji, avatar | Main sessions only |
| `TOOLS.md` | Local tool notes and environment-specific details | Every session + sub-agents |
| `HEARTBEAT.md` | Background task checklist | Heartbeat runs only |
| `MEMORY.md` | Curated long-term memory | Main sessions only (never in groups) |

Sub-agents only get `AGENTS.md` and `TOOLS.md` — other files are filtered out to keep sub-agent context small.

## BOOTSTRAP.md — Auto-Injected When Present (Temporary)

BOOTSTRAP.md **IS auto-injected** into the agent's context while it exists. It is created for brand-new workspaces during `openclaw onboard` and deleted after the bootstrap ritual completes. While present, it counts toward `bootstrapMaxChars` / `bootstrapTotalMaxChars` limits like any other auto-injected file.

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `BOOTSTRAP.md` | First-run onboarding ritual | Auto-injected when present. Created during `openclaw onboard`. Deleted after bootstrap completes. Counted toward char limits while present. |

**Scanning behavior**:
- BOOTSTRAP.md missing → good (means bootstrap completed successfully)
- BOOTSTRAP.md present → warning (bootstrap hasn't finished — the agent should complete or remove it)
- Can be skipped: `--dev` flag or `agent.skipBootstrap: true` in openclaw.json

## BOOT.md — Hook-Executed, NOT Auto-Injected

BOOT.md is NOT injected into the session context window. It is executed via the `boot-md` hook on `gateway:startup` event only. It is NOT counted toward character limits.

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `BOOT.md` | Gateway restart instructions | Optional. Executed via `boot-md` hook (requires `hooks.internal.enabled`). Persistent — runs on every gateway restart. Never deleted. Not injected into session context. |

**Scanning behavior**:
- BOOT.md missing → normal (optional file, user creates if needed)

## Character Limits

These limits apply ONLY to the 7 auto-injected files listed above. Other files in `workspace/` (agent-created files, docs/ subfolders, etc.) are NOT counted toward these limits and are NOT loaded into context automatically.

- **Per file**: `bootstrapMaxChars` = 20,000 characters (default)
- **Total across all auto-injected files**: `bootstrapTotalMaxChars` = 150,000 characters (default)
- Files exceeding limits are **truncated** with a marker
- BOOT.md is NOT counted (not auto-injected — hook-executed only)
- BOOTSTRAP.md IS counted while present (auto-injected on new workspaces, deleted after bootstrap)
- Override in `./openclaw.json`:
  ```json
  {
    "agents": {
      "defaults": {
        "bootstrapMaxChars": 30000,
        "bootstrapTotalMaxChars": 200000
      }
    }
  }
  ```

**The workspace/ folder can contain any files** — agents create files there during sessions (research notes, drafts, exports). These extra files are perfectly fine — they don't consume context tokens and don't count toward limits. If they're reference material the agent should access later, move them to `docs/` and reference from AGENTS.md.

## Warning Signs — When to Extract to Subfolders

- Auto-injected file **> 15K chars** → approaching the 20K truncation limit, move infrequently-used sections to `docs/`
- AGENTS.md contains **procedure sections** → extract to `docs/procedures/`
- AGENTS.md contains **client-specific rules** → extract to `docs/clients/`
- AGENTS.md contains **detailed security policies** → extract to `docs/rules/`
- Any **non-standard .md file in workspace/ root** → if it's reference material, move to `docs/` and add a reference in AGENTS.md

## Key Rule: SOUL vs AGENTS Separation

- **SOUL.md** = WHO the agent IS (persona, values, tone, boundaries)
- **AGENTS.md** = HOW the agent OPERATES (procedures, rules, memory management, group chat behavior)
- Never mix personality into AGENTS.md or procedures into SOUL.md

## Workspace Subfolders — On-Demand Reference Files

Only auto-injected files are loaded every session. Everything in subfolders is read on demand by the agent via the `read` tool — saving tokens when content is not relevant.

**Key rules**:
- If content is needed in >= 50% of sessions → keep in auto-injected files
- If content is needed in < 50% of sessions → move to docs/
- If content is critical for safety → keep in AGENTS.md or SOUL.md regardless
- One topic per file, lowercase-hyphen naming

See `references/subfolder-patterns.md` for detailed subfolder structure, templates, and examples.

## Files NOT Auto-Loaded

These exist in workspace/ but are NOT injected into context — the agent reads them on demand:

- `BOOT.md` — executed via hook on gateway restart, not injected
- `memory/YYYY-MM-DD.md` — daily memory logs (accessed via memory tools)
- `docs/**/*.md` — documentation subfolders (read when referenced from AGENTS.md)
- `workflows/*.prose` — workflow files
- `canvas/` — canvas UI files
- `skills/` — instance-specific skills (injected as compact XML list ~97 chars per skill; full SKILL.md loaded on demand when triggered)
- **Any other files** — agents can create arbitrary files in workspace/ during sessions (research, exports, drafts). These are stored but not loaded into context.

## Content Language

Write all workspace file content in English. This ensures consistency across multi-user setups, better compatibility with LLM models (which process English instructions more reliably), and clearer prompt engineering. Users may communicate with the agent in any language, but the workspace files themselves are always English.

## Referencing Subfolders from AGENTS.md

Since subfolders are NOT auto-loaded, reference them explicitly:

```markdown
## Reference Documents
Before starting a task, check if a relevant doc exists.
Read it with: read docs/<folder>/<file>.md

Available docs:
- docs/rules/         — security rules, data classification
- docs/procedures/    — step-by-step guides for specific task types
- docs/clients/       — client profiles, contracts, key facts
- docs/standing-orders/ — recurring tasks and schedules
```

## Version Control

Initialize git tracking for workspace files in a **private** repository. Exclude secrets:
```gitignore
.env
*.key
*.pem
secrets*
```

## Customization Workflow

The recommended approach for workspace optimization:

1. **Scan** — read all current workspace files, check for gaps
2. **Interview** — understand goals, users, tasks, channels, success criteria
3. **Analyze** — identify missing rules, conflicts, unused tools, pain points
4. **Security audit** — check for secrets, prompt injection risks, missing safety rules
5. **Optimize** — generate improved files following best practices
6. **Apply** — show diffs, get approval, write changes to `./workspace/`
7. **Fix permissions** — run chown + doctor in Docker after edits
8. **Iterate** — start short, add rules when problems are observed

## SOUL.md Size Rule

Keep SOUL.md under **2,000 words**. Every word costs tokens on EVERY interaction since it's injected into every prompt. Be concise — personality doesn't need a novel.

## Memory Security

MEMORY.md is loaded **only in main private sessions**, never in group chats. This prevents data leakage across shared contexts. Design AGENTS.md group chat rules accordingly.
