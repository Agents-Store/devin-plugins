---
name: workspace-overview
description: OpenClaw workspace architecture and file system overview — directory structure, file loading mechanics, character limits, scan categories (A-J), and subfolder organization patterns. Use this skill whenever the user asks about how the workspace is structured, what files get loaded automatically, character limits, what goes where, or how to organize their workspace. This is the foundational skill for workspace content — use it first when the user is new to OpenClaw or asks broad questions about workspace organization, even before more specific skills like agents-md or soul-md.
---

# OpenClaw Workspace Architecture

This skill covers the structure, loading mechanics, and organization of an OpenClaw agent workspace.
Fleet-level questions (which instances exist, their mounts, ports, health) belong to `fleet-model`;
this skill starts where an instance has already been resolved.

## Instance Directory Structure

**Standard layout**: `~/.openclaw/` (single instance). A named profile (`OPENCLAW_PROFILE`) uses
`~/.openclaw-<profile>/`, with the workspace under it.

**Docker fleet layout**: each instance has its own **state directory** on the host, `<data-root>/<instance>/`,
mounted into the container as the OpenClaw state directory, and a separate **source directory**,
`<compose-root>/<project>/`, holding the compose file and the deployment layer.

### State dir vs source dir

| Concept | Placeholder | Holds |
|---------|-------------|-------|
| **State dir** (runtime) | `<data-root>/<instance>/` | `openclaw.json`, `workspace/`, `agents/`, `state/`, `credentials/` |
| **Source dir** (deployment) | `<compose-root>/<project>/` | compose file, deployment layer, whatever the image is built or pulled from |

Never assume these paths. Read them from the live mount table (`fleet.py discover --json` →
`paths`, or `/openclaw-ops:status`), and resolve the instance with the selector grammar from
`fleet-model`. A workspace edit lands durably only inside a mounted path; a write outside a mount lives
until the next recreate.

All paths below are relative to the state dir.

```
./                              # State dir (<data-root>/<instance>/)
├── workspace/                  # Workspace files (injected)
│   ├── AGENTS.md               # Operating rules, procedures, local tool notes (## Tools)
│   ├── SOUL.md                 # Persona, tone, boundaries
│   ├── USER.md                 # User profiles, preferences (own 4,000-char cap)
│   ├── IDENTITY.md             # Agent name, emoji, avatar
│   ├── MEMORY.md               # Curated long-term memory
│   ├── BOOT.md                 # Gateway start instructions (boot-md hook)
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
│   └── <agent-id>/
│       └── agent/
│           └── openclaw-agent.sqlite   # sessions, transcripts, memory index, auth profiles
├── state/
│   └── openclaw.sqlite         # shared state: automations (cron), registries, plugin state
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

Two retired workspace files you may still meet on an older workspace: `TOOLS.md` (its content now lives
in the `## Tools` section of `AGENTS.md`) and `HEARTBEAT.md` (heartbeat instructions now live in the
heartbeat monitor's scratch; the runtime never reads the file). See the `tools-md` and `heartbeat-md`
skills.

The runtime keeps **all** of its state in SQLite — sessions, transcripts, the memory index, automation
jobs and auth profiles. Older installs may still carry `sessions.json`, `*.jsonl` transcripts, a jobs
file or a standalone memory database; those are legacy migration inputs, not live data.

### Shared Resources

**Standard paths:**
```
~/.openclaw/skills/*/SKILL.md               # Managed/local skills
```

**Fleet deployments** mount shared trees read-only into every instance:
```
<shared-skills-dir>/*/SKILL.md              # Shared skills
<shared-plugins-dir>/*/                     # Shared plugins
```
Their host locations come from discovery (`shared_skills`, `shared_plugins` in `paths`); the
`shared-assets` skill owns deduplicating, promoting and registering them.

Additional skill directories via `skills.load.extraDirs` in openclaw.json.

**ClawHub** (clawhub.com) is the public registry for discovering and sharing skills and plugins.

## Scan Categories (A–J + Shared)

| Cat | Target | Path | Mode |
|-----|--------|------|------|
| A | Auto-injected workspace files (core) | `./workspace/AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `MEMORY.md` | Read + Write |
| A+ | BOOT.md (hook-executed, not injected) | `./workspace/BOOT.md` (optional, persistent) | Read + Write |
| A++ | BOOTSTRAP.md (auto-injected when present) | `./workspace/BOOTSTRAP.md` (temporary, deleted after bootstrap) | Read + Write |
| B | Memory files | `./workspace/memory/*.md` + `./workspace/MEMORY.md` | Read + Write |
| C | Instance skills | `./workspace/skills/*/SKILL.md` | Read only |
| D | Subfolders (on-demand) | `./workspace/docs/**/*.md` + `./workspace/workflows/**/*.prose` | Read + Write |
| E | Config | `./openclaw.json` | Read; change only through `config-surgery` |
| F | Sessions | per-agent database — read through `openclaw sessions --json`, never by opening the database | Read only |
| G | Memory index | per-agent database — read through `openclaw memory status --agent <id>` (`--deep` adds the provider probe; `--index` **reindexes** a dirty store, so it is not a read) | Read only |
| H | Automations (cron) | shared state database — read through `openclaw automations list --all` | Read only |
| I | Logs | gateway log (dated files under the OS temp dir by default, or container output) — read through `/openclaw-ops:logs` | Read only |
| J | Canvas | `./workspace/canvas/` | Read + Write |
| — | Managed skills | `~/.openclaw/skills/*/SKILL.md` (standard) or `<shared-skills-dir>` (fleet) | Read only |
| — | Extra skill dirs | Paths from `skills.load.extraDirs` in openclaw.json | Read only |

**Write scope**: workspace content is edited in `./workspace/` — an R2 change, shown as a diff first,
with the previous text kept for rollback. A new file takes the owner of its siblings (check `ls -ln`
first and fix that one file); ownership is never changed recursively over a state directory, and never
as an automatic step after an edit. `openclaw.json` changes go through the `config-surgery` procedure.
Everything else is read-only for analysis.

## DO NOT SCAN — Excluded Directories

These contain sensitive/internal data (OAuth tokens, session state, device pairing, certs) — reading them risks exposing secrets in LLM context. Do not scan:

- `./credentials/` — channel and provider credentials, pairing allowlists
- `./telegram/` — Telegram session state
- `./devices/` — device pairing data
- `./subagents/` — internal subagent state
- `./completions/` — LLM completion cache
- `./delivery-queue/` — message delivery queue
- `./media/` — media file cache
- `./identity/` — certificates and identity data
- `./config.yaml` — internal gateway config
- `./*.bak*` — backup files
- `./state/` and `./agents/*/agent/` — the SQLite databases (and their `-wal` / `-shm` files). They hold
  transcripts and **OAuth tokens in clear**; do not open, copy or archive them casually, and treat any
  copy of the state directory as a credential artifact (mode 0600, never in a shared folder, rotate on
  leak)

## Auto-Injected Files (loaded every session)

These files are injected into the agent's context window on every turn — they consume tokens constantly. The `bootstrapMaxChars` and `bootstrapTotalMaxChars` limits apply to them.

| File | Purpose | Injection Scope |
|------|---------|-----------------|
| `AGENTS.md` | Operating rules, priorities, local tool notes | Every session |
| `SOUL.md` | Persona, tone, boundaries, values | Main sessions |
| `USER.md` | User identity, preferences, context | Main sessions, separate 4,000-char cap |
| `IDENTITY.md` | Agent name, vibe, emoji, avatar | Main sessions |
| `MEMORY.md` | Curated long-term memory | Main sessions only (never in groups) |

Spawned sub-agents receive a reduced subset of these files to keep their context small; confirm the
exact set on the instance (`/context` shows raw versus injected sizes per file).

## BOOTSTRAP.md — Auto-Injected When Present (Temporary)

BOOTSTRAP.md **IS auto-injected** into the agent's context while it exists. It is created for brand-new workspaces during `openclaw onboard` and deleted after the bootstrap ritual completes. While present, it counts toward `bootstrapMaxChars` / `bootstrapTotalMaxChars` limits like any other auto-injected file.

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `BOOTSTRAP.md` | First-run onboarding ritual | Auto-injected when present. Created during `openclaw onboard`. Deleted after bootstrap completes. Counted toward char limits while present. |

**Scanning behavior**:
- BOOTSTRAP.md missing → good (means bootstrap completed successfully)
- BOOTSTRAP.md present → warning (bootstrap hasn't finished — the agent should complete or remove it)
- Automatic creation of bootstrap files can be skipped: `--dev` flag or `agents.defaults.skipBootstrap: true` in openclaw.json. That key stops *creation* of the files; it does not stop injection of files that already exist

## BOOT.md — Hook-Executed, NOT Auto-Injected

BOOT.md is NOT injected into the session context window. It is executed through an agent run by the bundled `boot-md` hook when the gateway starts. It is NOT counted toward character limits.

| File | Purpose | Lifecycle |
|------|---------|-----------|
| `BOOT.md` | Gateway start instructions | Optional. Executed by the `boot-md` hook (ships disabled — `openclaw hooks enable boot-md`). Persistent — runs on every gateway start. Never deleted. Not injected into session context. |

**Scanning behavior**:
- BOOT.md missing → normal (optional file, user creates if needed)

## Character Limits

These limits apply ONLY to the auto-injected files listed above. Other files in `workspace/` (agent-created files, docs/ subfolders, etc.) are NOT counted toward these limits and are NOT loaded into context automatically.

- **Per file**: `bootstrapMaxChars` = 20,000 characters (default); `USER.md` keeps its own 4,000-character cap, which the setting can only lower
- **Total across all auto-injected files**: `bootstrapTotalMaxChars` = 60,000 characters (default)
- Files exceeding limits are **truncated**; the agent sees a short notice, the details stay in `/context`
- BOOT.md is NOT counted (not auto-injected — hook-executed only)
- BOOTSTRAP.md IS counted while present (auto-injected on new workspaces, deleted after bootstrap)
- Override in `./openclaw.json` (per agent: `agents.entries.<id>.bootstrapMaxChars` and `bootstrapTotalMaxChars`):
  ```json
  {
    "agents": {
      "defaults": {
        "bootstrapMaxChars": 30000,
        "bootstrapTotalMaxChars": 90000
      }
    }
  }
  ```
  Raising a limit spends tokens on every turn. Prefer moving content to `docs/` first.

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

- `BOOT.md` — executed via hook on gateway start, not injected
- `memory/YYYY-MM-DD.md` — daily memory logs (accessed via memory tools)
- `docs/**/*.md` — documentation subfolders (read when referenced from AGENTS.md)
- `workflows/*.prose` — workflow files
- `canvas/` — canvas UI files
- `skills/` — instance-specific skills (injected as a compact list; full SKILL.md loaded on demand when triggered)
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

Only the `workspace/` folder belongs in that repository — never the state directory around it, which
holds the databases and credentials listed under DO NOT SCAN.

## Customization Workflow

The recommended approach for workspace optimization:

1. **Scan** — read all current workspace files, check for gaps
2. **Interview** — understand goals, users, tasks, channels, success criteria
3. **Analyze** — identify missing rules, conflicts, unused tools, pain points
4. **Security audit** — check for secrets, prompt injection risks, missing safety rules (the `security-audit` skill owns exposure checks)
5. **Optimize** — generate improved files following best practices
6. **Apply** — show diffs, get approval, write changes to `./workspace/`
7. **Validate** — run `openclaw doctor --lint --severity-min info` (read-only) and compare against the baseline; the repair mode is a separate, planned R4 operation, never a post-edit step
8. **Iterate** — start short, add rules when problems are observed

## SOUL.md Size Rule

Keep SOUL.md under **2,000 words**. Every word costs tokens on EVERY interaction since it's injected into every prompt. Be concise — personality doesn't need a novel.

## Memory Security

MEMORY.md is loaded **only in main private sessions**, never in group chats. This prevents data leakage across shared contexts. Design AGENTS.md group chat rules accordingly.
