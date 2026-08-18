---
name: read-logs
description: "This skill should be used whenever the user wants to read, tail, stream, or search Dokploy logs — application runtime logs, Docker Compose stack logs (every container), database logs, or deployment build logs — and especially to diagnose why something failed. Triggers: \"read the logs\", \"show me the dokploy logs\", \"tail the logs\", \"compose logs\", \"all containers' logs\", \"container logs\", \"why is my app crashing\", \"why did my deploy fail — check the logs\", \"grep the logs for an error\", \"runtime logs\", \"build logs\". Use it instead of telling the user logs aren't available over the API — since Dokploy v0.29.0 they are."
---

# Read Dokploy Logs (runtime + build, every container)

Dokploy (since **v0.29.0**; current **v0.29.14**) exposes container logs over the REST API and the `@dokploy/mcp` server. There are four log sources, each with its own tool. The single most common mistake — and the reason multi-container Compose debugging fails — is calling `compose-readLogs` **without a `containerId`**. A Compose stack has many containers; you must enumerate them and read each one.

> **Do not** tell the user "Dokploy doesn't expose runtime logs via REST / use SSH or Beszel." That was true before [issue #3719](https://github.com/Dokploy/dokploy/issues/3719) was resolved. Since v0.29.0, `application-readLogs`, `compose-readLogs`, and every `{db}-readLogs` return **live container stdout/stderr** with `tail` / `since` / `search` filtering. SSH/Beszel is a last resort only (container not Dokploy-managed, or API unreachable).

---

## Step 0 — Decide which log you need

```
What are you debugging?
 ├─ The BUILD failed (image never built)        → deployment build log   → §3
 ├─ A standalone APP is crashing / erroring      → application runtime log → §1
 ├─ A COMPOSE stack (multi-container)            → per-container loop      → §2   ← the important one
 └─ A DATABASE service                           → database runtime log    → §4
Then optionally hand the text to AI triage       → §5
```

All runtime-log tools share three optional filters:

| Param | Meaning | Values |
|---|---|---|
| `tail` | How many recent lines | integer `1`–`10000` (default `100`). Use `1000`+ when hunting an intermittent error |
| `since` | Time window | `all` (default) or `<n><unit>` where unit ∈ `s m h d` — e.g. `30s`, `15m`, `2h`, `7d` |
| `search` | Substring filter (server-side grep) | up to 500 chars, e.g. `search: "error"` or `search: "ECONNREFUSED"` |

---

## §1 — Application runtime logs

A standalone application is one container. Read it directly:

```
mcp__dokploy__application-readLogs
  → { applicationId: "<id>", tail: 200, since: "1h", search?: "error" }
```

- Get `applicationId` from `application-one` / `application-search` / `project-all`.
- Returns the container's stdout/stderr. If it's empty, the container may not be running — check state with `docker-getContainersByAppLabel { appName, type: "standalone" }` (note: `type` is **required**; use `"swarm"` for cluster apps).

---

## §2 — Compose stack: read EVERY container

This is the workflow the user means by "read all the logs of all containers." A Compose stack runs N services; `compose-readLogs` is **per container** (`containerId` is required), so you must enumerate first, then loop.

**1. Resolve the stack identity.**

```
mcp__dokploy__compose-one → { composeId: "<id>" }
   ↳ read .appName        (the Docker name prefix Dokploy assigns)
   ↳ read .composeType    ("docker-compose" | "stack")
```

(If you only have a name, find the `composeId` with `compose-search { q: "<name>" }`.)

**2. Enumerate the containers** — pick the discovery tool by `composeType`:

| `composeType` | Discovery tool | Call |
|---|---|---|
| `docker-compose` | `docker-getContainersByAppNameMatch` | `{ appName, appType: "docker-compose" }` |
| `stack` (Swarm) | `docker-getStackContainersByAppName` | `{ appName }` |
| _unsure / fallback_ | `docker-getContainers` then filter by name containing `appName` | `{}` (lists all host containers) |

Each returned container is `{ containerId, name, state, status }` — e.g. `{ containerId: "a1b2c3d4e5f6", name: "my-stack-ab12cd-app-1", state: "running", status: "Up 5 days (healthy)" }`. **Save the `containerId` of every container** (the short Docker id) — that's what you pass next. Note which containers are `exited` / `restarting` / unhealthy; those are your prime suspects.

**3. Read logs for EACH container** (loop — do not stop at the first):

```
for each container c in the enumerated list:
  mcp__dokploy__compose-readLogs
    → { composeId: "<id>", containerId: c.containerId, tail: 200, since: "1h", search?: "error" }
```

The response `.data` is a single newline-joined string where each line is prefixed with an RFC3339 timestamp, e.g. `2026-06-04T09:14:16.979Z Error: Failed to find Server Action ...`. Split on `\n` and scan the tail for the §6 patterns.

**4. Aggregate and diagnose.** Print one section per container (`### <service/containerId> — <state>`), surface error lines first (see §6 patterns), and call out the container(s) that are down. A stack is only as healthy as its sickest container — a crashed `db` container makes the `web` container throw `ECONNREFUSED`, so reading *all* of them is what reveals the real root cause.

The `/dokploy-dev:compose-logs <compose>` command runs this entire loop for you.

---

## §3 — Deployment (build) logs

The build log explains why an image failed to build (before any container starts).

```
1. Find the deployment:
   mcp__dokploy__deployment-all { applicationId }   # or { composeId } / { serverId }
   mcp__dokploy__deployment-allCentralized          # if you don't know which resource
   ↳ pick the most recent row with status: "error"; save deploymentId

2. Read it:
   mcp__dokploy__deployment-readLogs { deploymentId: "<id>", tail: 500 }
```

`deployment-readLogs` takes only `deploymentId` + `tail` (no `since`/`search` — it's one finite artifact). Use this for build-time failures; use §1/§2 for run-time failures.

> **If `deployment-readLogs` is not a registered tool in your session, read the build log over REST instead — do not conclude it's unavailable.** Some MCP builds expose only a subset of Dokploy's endpoints, so the tool list / `ToolSearch` won't find `deployment-readLogs` even though the instance (v0.29.0+) serves it. The REST endpoint is always there:
> ```bash
> curl -s -G "$DOKPLOY_URL/api/deployment.readLogs" \
>   -H "x-api-key: $DOKPLOY_API_KEY" \
>   --data-urlencode "deploymentId=<id>" --data-urlencode "tail=500"
> ```
> Build logs carry `\r` progress noise — pipe through `tr '\r' '\n'` before grepping. The response is a JSON string. This MCP-tool-missing → REST-fallback move works for any endpoint; confirm exact paths/params with `settings-getOpenApiDocument` (large — dump to a file and grep). The CLI is an equivalent fallback: `dokploy deployment read-logs --deploymentId <id> --tail 500` (same endpoint, no curl quoting). Diagnosing a build failure from indirect signals when the real log is one `curl` away leads to wrong root causes.

---

## §4 — Database runtime logs

Each database type has its own `readLogs` with the same filters:

```
mcp__dokploy__postgres-readLogs { postgresId, tail, since, search }
mcp__dokploy__mysql-readLogs    { mysqlId,    tail, since, search }
mcp__dokploy__mariadb-readLogs  { mariadbId,  tail, since, search }
mcp__dokploy__mongo-readLogs    { mongoId,    tail, since, search }
mcp__dokploy__redis-readLogs    { redisId,    tail, since, search }
mcp__dokploy__libsql-readLogs   { libsqlId,   tail, since, search }
```

Get the id from `{type}-one` / `{type}-search`. Typical hunts: `search: "FATAL"` (Postgres auth/startup), `search: "Out of memory"`, `search: "Access denied"` (MySQL/MariaDB creds).

---

## §5 — Hand the logs to AI triage (optional)

If an AI provider is configured, let it summarize the text you just fetched. **`ai-analyzeLogs` does NOT take a `deploymentId`** — you pass the actual log text:

```
1. aiId  = first enabled provider from  mcp__dokploy__ai-getEnabledProviders
           (if empty → AI not configured; skip, or wire one up via the ai-assist skill)
2. logs  = the log text returned by readLogs in §1–§4 (truncate very large logs)
3. context = "build"   for §3 deployment logs
             "runtime" for §1 / §2 / §4 logs

mcp__dokploy__ai-analyzeLogs → { aiId, logs, context }
   ↳ returns a natural-language root cause + suggested fix
```

See the `ai-assist` skill for provider setup. Read the AI's answer critically — it only sees the log you gave it, not the codebase.

---

## §6 — Error patterns to surface first

When formatting any log output, grep (case-insensitive) for these and show matching lines at the top:

| Signal | Likely meaning |
|---|---|
| `error`, `fatal`, `panic`, `traceback`, `exception` | application-level failure |
| `exited`, `exit code`, `killed`, `OOMKilled`, `out of memory` | container died / resource limit |
| `ECONNREFUSED`, `connection refused`, `getaddrinfo`, `ENOTFOUND` | service can't reach a dependency (DB/cache/another container) |
| `denied`, `unauthorized`, `403`, `401`, `authentication failed` | credential / token problem |
| `no space left on device` | disk full → run `/dokploy-dev:cleanup` |
| `EADDRINUSE`, `address already in use`, `bind` | port collision |
| `timeout`, `timed out`, `deadline exceeded` | slow dependency / health-check failing |

If you find one, suggest the next step: `/dokploy-dev:analyze` (AI triage) or `/dokploy-dev:debug <id>` (full decision tree).

---

## §7 — Last resort (only if the API can't serve the log)

Use these **only** when a container is not managed by Dokploy, or the Dokploy API itself is unreachable:

- SSH to the server: `docker logs --tail 500 <containerId>` (get `<containerId>` from `docker-getContainers`).
- Beszel, if installed, can read the on-disk log files under `/etc/dokploy/logs/<appName>/`.

These are fallbacks, not the default. For any Dokploy-managed app/compose/database, §1–§4 are the correct path.

---

## Examples

<example>
User: "My app `web-api` keeps restarting — show me what's wrong."
1. `application-one { applicationId }` (or resolve via `application-search { q: "web-api" }`) → confirm it exists, grab `appName`.
2. `application-readLogs { applicationId, tail: 300, since: "30m" }`.
3. Grep the result: a `panic: runtime error: invalid memory address` line appears near the end.
4. Report the panic + stack frame, note the crash loop, and offer `/dokploy-dev:analyze` for an AI root-cause.
</example>

<example>
User: "Read all the logs for my `n8n-stack` compose project, something's broken."
1. `compose-search { q: "n8n-stack" }` → `composeId`; `compose-one { composeId }` → `appName: "n8n-stack-xxxx"`, `composeType: "docker-compose"`.
2. `docker-getContainersByAppNameMatch { appName: "n8n-stack-xxxx", appType: "docker-compose" }` → 3 containers: `n8n` (running), `postgres` (restarting), `redis` (running).
3. Loop `compose-readLogs { composeId, containerId, tail: 200 }` for ALL THREE.
4. The `postgres` container log shows `FATAL: database files are incompatible with server`. The `n8n` log shows `ECONNREFUSED postgres:5432` — a downstream symptom. Report postgres as the root cause; n8n is fine once the DB is fixed.
</example>

<example>
User: "Why did the last deploy of `landing` fail?"
1. `deployment-all { applicationId }` → most recent row `status: "error"`, save `deploymentId`.
2. `deployment-readLogs { deploymentId, tail: 500 }`.
3. Log shows `error: failed to solve: failed to read dockerfile`. Report: wrong `dockerContextPath` / missing Dockerfile; fix via `application-saveBuildType` then `application-redeploy`.
</example>

---

## See also

- `/dokploy-dev:compose-logs <compose>` — one-shot "read every container" command (this skill's §2, automated)
- `/dokploy-dev:logs <resource>` — unified single-resource log reader
- [`debug-deploy`](../debug-deploy/SKILL.md) — full failure decision tree (uses these log calls)
- [`ai-assist`](../ai-assist/SKILL.md) — configure a provider for `ai-analyzeLogs`
