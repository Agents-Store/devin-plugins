---
name: fleet-model
description: Use when work touches an OpenClaw gateway instance or several of them on one host — inventory, status, health, logs, provider auth, config, secrets, memory, shared skills, upgrades, cloning — or when an instance is named or selected, or when the alternative would be a hand-written docker exec, a guessed path, or a remembered version or model name.
---

# OpenClaw fleet model

The model every other skill and command here assumes. Load a reference only when the task needs that depth; the routing table says which.

## Shape: source is not state

- One host, N instances. Each instance is one Docker Compose project named `<project_prefix><name>`.
- Source (compose project, image) and state (the mounted state tree) are separate. Recreating a container keeps state; anything written inside the container outside a mount dies with it.
- Paths come from the live mount table, never from memory. Container-side destinations are fixed by upstream; the host side is whatever `docker inspect` reports for this instance.
- Isolation is per instance on state dir, config path, workspace and gateway port. Credential directories are not on that list and may deliberately be shared.
- The gateway listens on one container port; each instance publishes its own host port, normally on loopback. Paths and mounts: `references/layout.md`.

## Config

Operator-owned, outside this repo, mode 0600. Ladder, first hit wins: `$OPENCLAW_OPS_CONFIG` → `./.openclaw-ops.json` → `~/.config/openclaw-ops/fleet.json` → `/etc/openclaw-ops/fleet.json`.
It holds only what discovery cannot infer: `project_prefix`, `reference`, `policy.canary`, `policy.update_channel`, `policy.soak_days`, `policy.stale_log_hours`, `policy.snapshot_dir`, and per instance `manage`, `role`, `criticality`, `aliases`, `secrets` (names and ids, never values).
A `host_fingerprint` mismatch forces read-only — the file describes another machine. With no config discovery still works and mutations do not. Fields: `references/fleet-config.md`.

## Selector

`fleet.py resolve <selector>` owns the grammar; nothing else reimplements it.

| Selector | Means |
|---|---|
| empty, `managed` | every managed instance (`manage:true`, not alien) |
| `all` | everything, alien and unmanaged included — READ ONLY |
| `@reference`, `@canary`, `@<role>` | the configured reference, the canary, every instance in a role |
| `a,b` · `web-*` · `managed,-b` | explicit list (aliases accepted) · glob · subtraction |

A mutation must name its targets: empty and `all` are refused, because a selector that widens as the fleet grows turns a one-instance fix into a fleet-wide incident.

## Exec

Every CLI call goes through `${CLAUDE_PLUGIN_ROOT}/scripts/ocexec.py <instance> [--mode auto|hot|cold] [--json] -- <openclaw args…>`. Never hand-write `docker exec`; never call a site wrapper for what the CLI already does.
- **hot** — `compose exec -T` into the gateway through the secret-injection wrapper. The normal path.
- **cold** — one-off container over the state dir. Only while the instance is down, and only for `setup`, `qa`, `database`.
- Refusals are contract: alien instance · `--accept-capabilities` · `--probe` against a live gateway · cold over a running state dir · R3/R4 argv, which belong to a command that builds a plan.
- Both streams are redacted; `--json` parses stdout only. Exit 64 refused · 65 unknown instance · 66 no docker. Modes and standing bans: `references/exec-contract.md`.

## States

| State | Evidence | Allowed |
|---|---|---|
| `ok` | running, config present, log moving, CLI answers | everything |
| `degraded` | up and green but a subsystem is dead: auth check non-zero, empty config, silent log, mute CLI | reads, targeted repair; batch mutations need confirmation |
| `down` | no container, not running, or restart loop | host side only: files, compose logs, cold container |
| `alien` | failed the layout fingerprint, or `manage:false` | inventory row; every mutation refused |

A deep battery downgrades `ok` to `degraded` and never the reverse. Nothing is hidden: an object that looks like an instance and fails the fingerprint is still listed.

## Dry-run and --yes

- A mutation is anything after which observable state differs. The word `status` in a name proves nothing.
- Every mutation prints eight blocks first: TARGET · PRECHECK · CHANGE · BACKUP · IMPACT · VALIDATE · ROLLBACK · APPLY. R3 and R4 add IRREVERSIBLE · CONFIRM. ROLLBACK is an executable command; prose is a bug.
- `--yes` applies — never in the same turn the command was first proposed, and never because the user approved something earlier.
- R3 needs a backup that already exists, R4 a typed phrase, anything past the canary a separate confirmation. Good→changed batches fail fast; broken→repair batches continue and report.

## Routing

| Symptom or task | Go to |
|---|---|
| first run on this host · the daily picture | `/openclaw-ops:init` · `/openclaw-ops:status [--deep]` |
| something is wrong, cause unknown | skill `fleet-diagnostics`, then `/openclaw-ops:audit` |
| a finding that already has an id | `/openclaw-ops:repair <sel> --issue <id>` — the only repair funnel |
| logged out, empty or expired tokens, one account across instances | skill `provider-auth` · `/openclaw-ops:auth` |
| editing the instance config, the model chain, a cron entry | skill `config-surgery` |
| version drift, upgrading, what a release added | skill `instance-upgrade` · `/openclaw-ops:update` · `:features` |
| dead embeddings, paused vector search, bloated state DB | skill `memory-ops` |
| shared skills or plugins empty, duplicated, shadowed | skill `shared-assets` · `/openclaw-ops:shared-sync` |
| missing env keys, plaintext env file, secret delivery | skill `secrets-infisical` |
| exposure, permissions, gateway tokens, trust boundary | skill `security-audit` |
| a new instance from the reference | skill `instance-clone` · `/openclaw-ops:clone` |
| logs across instances · one raw CLI call | `/openclaw-ops:logs` · `/openclaw-ops:exec` |
| any claim about versions, flags or model names | skill `docs-research` first — no live source, no recommendation |
