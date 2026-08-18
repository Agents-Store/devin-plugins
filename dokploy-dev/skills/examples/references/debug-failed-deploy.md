# Scenario: Debug a Failed Deployment

End-to-end walkthrough for diagnosing a failed Dokploy deployment. Mirrors the `debug-deploy` skill but with concrete inputs and expected outputs.

## Contents
- [Setup](#setup)
- [Step 1: Locate the failed run](#step-1-locate-the-failed-run)
- [Step 2: Read the build log](#step-2-read-the-build-log)
- [Step 3: Inspect the container](#step-3-inspect-the-container)
- [Step 4: Check the request path](#step-4-check-the-request-path)
- [Step 5: AI-summarise (optional)](#step-5-ai-summarise-optional)
- [Step 6: Recover and verify](#step-6-recover-and-verify)
- [Outcomes by failure class](#outcomes-by-failure-class)

---

## Setup

Scenario: a Next.js app called `marketing-site` in project `production` was working yesterday. Today's deploy reports `error` and the live domain returns 502. We start with one piece of info: the app name.

Tools you'll touch in this walkthrough:

```
project-all, application-one, deployment-all,
application-readLogs, docker-getContainersByAppLabel, docker-getConfig,
application-readTraefikConfig, ai-analyzeLogs,
settings-checkInfrastructureHealth, settings-getDockerDiskUsage,
application-killBuild, application-redeploy, rollback-rollback
```

---

## Step 0: Confirm the platform is healthy

```
mcp__dokploy__settings-health
mcp__dokploy__settings-checkInfrastructureHealth
mcp__dokploy__settings-getDockerDiskUsage
```

Expected: all three return ok and disk usage < 90%. If `getDockerDiskUsage` shows Images > 50GB or disk > 90% full, jump to the cleanup section before diagnosing the deploy — disk pressure causes silent build failures.

---

## Step 1: Locate the failed run

Resolve the app:

```
mcp__dokploy__project-all
   → find the "production" project
   → inside, find the application named "marketing-site"
   → save applicationId (e.g. app_aaa111)
```

List its deployments, most recent first:

```
mcp__dokploy__deployment-all
   → { applicationId: "app_aaa111" }
```

Find the most recent entry with `status: "error"`. Save:

- `deploymentId` — e.g. `deploy_bbb222`
- `logPath` — e.g. `/etc/dokploy/logs/marketing-site/marketing-site-2026-05-21T09-15-22.log`
- `errorMessage` — Dokploy's framing message (often generic — the real error is in the log file)
- `startedAt` / `finishedAt` — duration; very short = early build failure, very long = either runtime crash or hung step

---

## Step 2: Read the logs

The `status: error` here was a quick finish (~seconds), and the live site returns 502 — that points to a **runtime** crash (the build succeeded, the container won't stay up). Read the app's runtime log directly over MCP (v0.29.0+ — no SSH/Beszel):

```
mcp__dokploy__application-readLogs
   → { applicationId: "app_aaa111", tail: 300, since: "1h", search: "error" }
   → .data is a newline-joined, timestamp-prefixed string
```

(If this had been a *build* failure instead, you'd read that deployment's build log with `mcp__dokploy__deployment-readLogs { deploymentId: "deploy_bbb222", tail: 500 }`.)

Scan the log for these patterns first:

| If you see... | Then it's... |
|---|---|
| `no space left on device` | Disk full — go to cleanup |
| `failed to compute cache key` | Stale build cache — `killBuild` + `redeploy` |
| `Cannot find module` / `MODULE_NOT_FOUND` | Wrong build context or missing dependency |
| `Permission denied` while writing `/usr/...` | Container running as wrong user |
| `error: failed to solve` | Dockerfile error — read above for the failing layer |
| `unauthorized` on `git push` / `docker pull` | Credential issue |
| App starts then immediately exits | Runtime config / missing env var — go to Step 3 |

In our scenario, the log ends with:

```
> next start
  ▲ Next.js 14.2.0
  - Local:        http://0.0.0.0:3000
  Error: connect ECONNREFUSED postgres:5432
  ... (exit code 1)
```

**Interpretation:** the build succeeded; the app crash-loops because it can't reach the database. This is a runtime issue, not a build issue.

---

## Step 3: Inspect the container

```
mcp__dokploy__docker-getContainersByAppLabel
   → { appName: "marketing-site", type: "standalone" }   # type is required
```

You'll see a container with `state: "restarting"` — classic crash loop. Each entry is `{ containerId, name, state, status }`.

Get its full config:

```
mcp__dokploy__docker-getConfig
   → { containerId: "<id>" }
```

Look for:

- **`Networks`** — confirm the container is on `dokploy-network` so it can reach the `postgres` service.
- **`Env`** — does `DATABASE_URL` exist? Does it point at `postgres:5432` (the compose service name) or a different host?
- **`RestartPolicy`** — Dokploy sets `unless-stopped`; the loop confirms the app keeps exiting.

In our scenario, `DATABASE_URL=postgres://postgres:secret@db:5432/main` — but the actual DB service is called `postgres`, not `db`. The Next.js app was configured for a previous compose layout. We have the root cause.

---

## Step 4: Check the request path

Only relevant if the runtime *is* up but HTTP is broken. In our scenario the container never stays up long enough to serve HTTP, so the 502 the user sees is just Traefik failing to find a healthy backend. Skip Step 4.

(For completeness: if the container were stable but HTTP requests failed, run `application-readTraefikConfig` and verify the service URL points to the right port and the `dokploy-network` is shared.)

---

## Step 5: AI-summarise (optional)

If an AI provider is configured:

```
mcp__dokploy__ai-getEnabledProviders     # confirm non-empty → take an aiId
mcp__dokploy__ai-analyzeLogs
   → { aiId: "<enabled provider id>", logs: "<the runtime-log text from Step 2>", context: "runtime" }
```

Expected output (paraphrased):

> The build completed successfully. The runtime container exits because it cannot resolve the host `db` when connecting to PostgreSQL — `getaddrinfo ENOTFOUND db`. The DATABASE_URL points to `db:5432` but no service named `db` exists in the application's network. Fix: update DATABASE_URL to use the actual database hostname (likely `postgres` or the database resource's `appName`).

This matches our manual analysis from Step 3.

---

## Step 6: Recover and verify

Fix the env var:

```
mcp__dokploy__application-saveEnvironment
   → {
       applicationId: "app_aaa111",
       env: "DATABASE_URL=postgres://postgres:secret@postgres:5432/main\nNODE_ENV=production\nPORT=3000",
       buildArgs: "",
       buildSecrets: "",
       createEnvFile: false
     }
```

Trigger a redeploy:

```
mcp__dokploy__application-redeploy
   → { applicationId: "app_aaa111" }
```

Poll until done:

```
mcp__dokploy__deployment-all
   → { applicationId: "app_aaa111" }
   → wait until newest entry has status: "done"
```

Confirm the container is healthy:

```
mcp__dokploy__docker-getContainersByAppLabel
   → { appName: "marketing-site" }
   → State should be "running", Health "healthy"
```

Hit the endpoint:

```bash
curl -sI https://marketing-site.example.com
# Expected: HTTP/2 200
```

If the fix didn't work, **return to Step 1**. Do not chain more fixes — re-diagnose first.

---

## Outcomes by failure class

| Class | What you fix in Step 6 | Recovery call |
|---|---|---|
| Wrong env var (our scenario) | `application-saveEnvironment` | `application-redeploy` |
| Stale build cache | (none) | `application-killBuild` → `application-redeploy` |
| Wrong build type | `application-saveBuildType` | `application-redeploy` |
| Git credentials expired | `github-update` / `gitlab-update` / etc. | `application-redeploy` |
| Wrong domain port | `domain-update` | (no redeploy — Traefik picks up immediately) |
| Disk full | `/dokploy-dev:cleanup` | `application-redeploy` |
| Bad image overall | (none) | `rollback-rollback` to previous image |
| Stuck queue | `application-cleanQueues` | `application-redeploy` |
| Hung container | `docker-killContainer` | `application-redeploy` |
| Compose-mode mismatch (silent success) | (none) | `compose-deploy` on the compose resource |
