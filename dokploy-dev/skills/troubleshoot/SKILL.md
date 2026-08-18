---
name: troubleshoot
description: "This skill is the symptom-to-cause lookup reference for Dokploy problems — domains, databases, Docker, Traefik, MCP connection. Use for known-symptom diagnosis. For an end-to-end failed-deploy workflow, the canonical entry point is the `debug-deploy` skill and the `/dokploy-dev:debug` command. Triggers: \"dokploy 502\", \"domain not resolving\", \"database connection refused\", \"mcp tools not found\", \"dokploy api 401\", \"traefik dashboard\"."
---

# Dokploy Troubleshooting Reference

This is the **symptom-to-cause reference table** for common Dokploy problems. Match the user's symptom against the relevant section below, then apply the fix.

> **For a failed deployment, start here:** Run `/dokploy-dev:debug [resource]` (or load the `debug-deploy` skill). That runs the full decision tree — failed-run lookup, build log analysis, container/Traefik inspection, optional AI summary, and recovery — instead of just a symptom lookup. Use this skill when you already know the rough symptom and want the table entry.

---

## Quick Diagnostics Checklist

Run these checks first to understand the current state:

1. **Platform health:**
   ```
   mcp__dokploy__settings-health
   mcp__dokploy__settings-checkInfrastructureHealth
   mcp__dokploy__settings-getDockerDiskUsage
   ```

2. **Dokploy version:** Call `mcp__dokploy__settings-getDokployVersion`

3. **Recent deployments:** Call `mcp__dokploy__deployment-allCentralized`

4. **Docker containers:** Call `mcp__dokploy__docker-getContainers`

If the health check fails or `checkInfrastructureHealth` reports a problem, the server itself is unhealthy. Fix the server before investigating application-level issues.

---

## Domain Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Domain not resolving | DNS not pointed to server | Add an A record pointing to the server IP. Use `mcp__dokploy__server-publicIp` to get the IP |
| Domain resolves but returns 404 | Wrong port in domain config | Check the app's listening port (Next.js: 3000, Laravel: 8000). Update the domain config with the correct port |
| SSL certificate error | Domain added before DNS propagation | Delete the domain, wait for DNS propagation (up to 10 minutes), then re-add with HTTPS enabled |
| 502 Bad Gateway | App crashed or not listening on 0.0.0.0 | Check app logs. The app MUST listen on `0.0.0.0`, NOT `127.0.0.1`. This is the most common cause of 502s |
| traefik.me not working | Server blocks traefik.me DNS | Call `mcp__dokploy__domain-canGenerateTraefikMeDomains` to check support. If blocked, use a real domain instead |
| Mixed content errors | App serves HTTP behind HTTPS proxy | Set the app's `FORCE_SSL` or equivalent env var, or configure Traefik to handle HTTPS termination |

### Domain debugging steps

1. Verify DNS resolves to the correct IP:
   ```bash
   dig +short example.com
   ```

2. Check if Traefik is receiving the request:
   ```bash
   curl -vk https://example.com 2>&1 | head -30
   ```

3. Verify the domain configuration in Dokploy:
   Call `mcp__dokploy__application-one` with the applicationId and inspect the `domains` array.

4. Validate the domain:
   Call `mcp__dokploy__domain-validateDomain` with `domain` (the hostname string, NOT the domainId; optionally `serverIp`).

---

## Deployment Failures

> For a multi-step diagnosis instead of a single-row lookup, run `/dokploy-dev:debug` — it locates the failed run, reads the build log, inspects the container, and recommends a fix.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Build fails | Wrong build type | Check the build type matches the source. Use Nixpacks for auto-detect, Dockerfile if a Dockerfile exists in the repo |
| Build succeeds but app crashes | Missing environment variables | Check the environment config with `mcp__dokploy__application-one` and verify all required env vars are set |
| Deployment stuck in queue | Previous deployment blocking | Call `mcp__dokploy__application-cleanQueues` to clear the queue, or `mcp__dokploy__application-cancelDeployment` to cancel the blocking deployment |
| Git clone fails | Wrong repo URL or credentials | Verify the git provider config. Re-authenticate with the per-provider update tool: `mcp__dokploy__github-update`, `mcp__dokploy__gitlab-update`, `mcp__dokploy__bitbucket-update`, or `mcp__dokploy__gitea-update` |
| Nixpacks build fails | Unsupported language/framework | Check Nixpacks docs for supported runtimes. Alternatively, switch to Dockerfile build type |
| Build timeout | Large image or slow network | Increase build timeout or optimize the Dockerfile (use multi-stage builds, reduce layers) |
| Build fails with `no space left on device` | Server disk full (typically build cache or unused images) | Run `/dokploy-dev:cleanup`. Check `mcp__dokploy__settings-getDockerDiskUsage` — if Images > 70% of total, run `settings-cleanUnusedImages` and `cleanDockerBuilder` |
| Deploy reports `done` but production site unchanged | Compose-mode mismatch — the site runs from a compose service but `application-deploy` was called on the standalone app | Call `compose-deploy` on the matching compose resource. The `/dokploy-dev:deploy` and `/dokploy-dev:status` commands detect this and warn |
| Container runs but logs show `EADDRINUSE` or never accepts connections | App bound to `127.0.0.1` (loopback) instead of `0.0.0.0` | Fix the app's listen address. Most frameworks need an explicit `HOST=0.0.0.0` env var or CLI flag |
| Compose service unreachable from Traefik | Service not on `dokploy-network` | Every public-facing compose service must declare `networks: [dokploy-network]` and the network must be `external: true` at the top level |
| Compose service breaks Traefik (ports 80/443/8080 conflict) | Compose service exposes host ports directly (e.g. `ports: ["80:80"]`) | Remove the explicit host port mapping — Traefik routes via labels, not host bindings. If a host port is required, pick a non-Traefik one |
| Image pull fails with `unauthorized` | Registry creds missing or expired | `mcp__dokploy__registry-all` → `registry-update` with fresh credentials |
| Need to see runtime stdout/stderr | (v0.29.0+) Runtime logs ARE available over MCP/REST | App: `application-readLogs { applicationId, tail, since, search }`. Compose: enumerate containers then `compose-readLogs { composeId, containerId, tail, since, search }` per container (use `/dokploy-dev:compose-logs`). DB: `{type}-readLogs`. See the `read-logs` skill |
| Only one compose container's logs show / "compose-readLogs failed" | `compose-readLogs` requires a **`containerId`** — a stack has many containers | First `docker-getContainersByAppNameMatch { appName, appType: "docker-compose" }` (or `docker-getStackContainersByAppName` for swarm), then call `compose-readLogs` once **per** returned `containerId` |

### Deployment debugging steps

For full diagnosis, prefer `/dokploy-dev:debug <id>` over walking these manually — it chains them in the right order and also runs `ai-analyzeLogs` if a provider is configured.

1. **List deployments and find the latest:**
   ```bash
   curl -s -H "x-api-key: $DOKPLOY_API_KEY" \
     "$DOKPLOY_URL/api/deployment.all?applicationId=<id>" | python3 -m json.tool
   ```
   Or call `mcp__dokploy__deployment-all` with `applicationId` as the filter. Save the `deploymentId` of the failed run and its `logPath`.

2. **Read the logs (build vs runtime):**
   - Build failure → `mcp__dokploy__deployment-readLogs { deploymentId, tail: 500 }` (the build log for that run).
   - Runtime crash → `mcp__dokploy__application-readLogs { applicationId, tail, since, search }` for an app, or the per-container `compose-readLogs` loop for a stack. These return live container stdout/stderr (v0.29.0+ — no SSH/Beszel needed). See the `read-logs` skill.

3. **Check application status:**
   `mcp__dokploy__application-one` with the applicationId. Look at the `applicationStatus` field.

4. **Inspect the container:**
   `mcp__dokploy__docker-getContainersByAppLabel { appName }` for state and health. Drill down with `docker-getConfig { containerId }` to see env, command, mounts, network, and restart policy. If the container is in a restart loop, the exit code in `docker-getConfig` tells you why.

5. **Check Traefik routing (if HTTP errors):**
   `mcp__dokploy__application-readTraefikConfig` returns the router/service entries Traefik uses for this app. Confirm the service URL points at the right port and the host matches the domain the user is hitting.

6. **Summarise with AI (optional):**
   If `mcp__dokploy__ai-getEnabledProviders` returns a provider, fetch the log text (step 2) and run `mcp__dokploy__ai-analyzeLogs { aiId, logs, context: "build" | "runtime" }` for a natural-language root-cause + suggested fix. See the `ai-assist` skill for setup.

---

## Database Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cannot connect externally | No external port set | Call `mcp__dokploy__postgres-saveExternalPort` (or the mysql/mariadb/mongo/redis equivalent) to expose a port |
| Connection refused | Database not deployed | Call `mcp__dokploy__postgres-deploy` (or equivalent for other database types) to start the container |
| Authentication failed | Wrong credentials | Check the database password in Dokploy. Call `mcp__dokploy__postgres-one` to inspect the config |
| Connection string wrong | Missing host or port | The internal hostname is the container name. The external host is the server IP with the external port |
| Database too slow | No resource limits set | Set memory and CPU limits via the database advanced settings |

### Database connection string patterns

| Database | Internal connection string |
|----------|--------------------------|
| PostgreSQL | `postgresql://user:password@container-name:5432/dbname` |
| MySQL | `mysql://user:password@container-name:3306/dbname` |
| MariaDB | `mysql://user:password@container-name:3306/dbname` |
| MongoDB | `mongodb://user:password@container-name:27017/dbname` |
| Redis | `redis://default:password@container-name:6379` |

For external access, replace `container-name` with the server IP and use the external port.

---

## Docker / Compose Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Compose deploy fails | Invalid docker-compose.yml | Call `mcp__dokploy__compose-getConvertedCompose` to validate the file before deploying |
| Volume paths wrong | Relative paths incorrect | Docker Compose volumes in Dokploy use `../files/data:/var/lib/data` pattern for persistent data |
| Container keeps restarting | App crash loop | Check container logs, verify env vars, check resource limits with `mcp__dokploy__docker-getContainers` |
| Image pull fails | Wrong registry credentials | Verify registry auth with `mcp__dokploy__registry-all`. Re-add credentials if needed |
| Port conflicts | Two services on the same port | Check exposed ports across all apps. Use `mcp__dokploy__docker-getContainers` to find conflicts |
| Network issues between containers | Containers on different networks | Compose services share a network by default. Standalone apps need to be on the same Docker network |

### Compose debugging steps

1. Validate the compose file:
   Call `mcp__dokploy__compose-getConvertedCompose` with the composeId.

2. Check running services:
   Call `mcp__dokploy__compose-loadServices` with the composeId (defined services), and `mcp__dokploy__docker-getContainersByAppNameMatch { appName, appType: "docker-compose" }` for the actual running containers + their state.

3. Read each container's logs over MCP (no SSH needed):
   For every container returned in step 2, call `mcp__dokploy__compose-readLogs { composeId, containerId, tail, since, search }`. The `/dokploy-dev:compose-logs <name>` command runs this whole loop and highlights errors per container.

---

## MCP Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| MCP tools not found | Plugin not enabled or npx failed | Re-enable the plugin. Verify `npx -y @dokploy/mcp` works locally |
| MCP returns "Invalid URL" | `DOKPLOY_URL` env var not set or has wrong format | `DOKPLOY_URL` must be the **base URL without `/api`** (e.g. `https://dokploy.example.com`). Check `settings.local.json` `env` block. If MCP tools still fail, fall back to direct `curl` calls with `x-api-key` header (see Diagnostic Commands below) |
| MCP returns 401 | Invalid API key or wrong auth header | Dokploy API uses `x-api-key` header, NOT `Authorization: Bearer`. Regenerate the API key in the Dokploy dashboard (**Settings > API/Tokens**). Update `userConfig` |
| MCP returns connection refused | Wrong DOKPLOY_URL | The URL should be the base Dokploy URL (e.g. `https://dokploy.example.com`). API routes are at `/api/…` under it |
| Too many tools / context bloat | All 546 tools exposed | Set `DOKPLOY_ENABLED_TAGS` in `.mcp.json` `env` to a comma-separated category list (e.g. `project,application,domain,compose,postgres,settings,deployment`). `DOKPLOY_TOOL_PRESET` / `DOKPLOY_DISABLED_TAGS` are unreleased (merged upstream 2026-08-07, not in `@dokploy/mcp` 0.29.14 — silently ignored) |
| MCP timeout | Server overloaded or network latency | Check server health. Increase timeout in MCP client config if the server is slow |
| MCP returns 500 | Server-side error | Check Dokploy server logs. This usually indicates a bug or corrupt state |

---

## Diagnostic Commands

### Via curl

```bash
# Check Dokploy server health
curl -s "$DOKPLOY_URL/api/settings.health" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# Check Dokploy version
curl -s "$DOKPLOY_URL/api/settings.getDokployVersion" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# List all Docker containers
curl -s "$DOKPLOY_URL/api/docker.getContainers" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# Get server public IP
curl -s "$DOKPLOY_URL/api/server.publicIp" \
  -H "x-api-key: $DOKPLOY_API_KEY"

# List all projects with their applications
curl -s "$DOKPLOY_URL/api/project.all" \
  -H "x-api-key: $DOKPLOY_API_KEY"
```

### Via MCP tools

```
mcp__dokploy__settings-health
mcp__dokploy__settings-getDokployVersion
mcp__dokploy__docker-getContainers
mcp__dokploy__server-publicIp
mcp__dokploy__project-all
```

---

## When to Escalate

- **Traefik configuration issues** — Check the Traefik dashboard (usually at port 8080 on the server). Traefik misconfigurations are outside Dokploy's control.
- **Docker Swarm / cluster issues** — Check node status with `mcp__dokploy__cluster-getNodes`. Cluster problems require server-level debugging.
- **Persistent 502s after all checks pass** — Check server resources (CPU, memory, disk). The server may be under-provisioned.
- **Data corruption** — If database data is corrupted, restore from backups. Enumerate configured backups per resource and list backup files with `mcp__dokploy__backup-listBackupFiles` (`backup-all` was removed — backups are now resource-scoped).
- **Dokploy upgrade failures** — Check the Dokploy GitHub releases for known issues. Roll back to the previous version if needed.
- **Running < v0.29.13?** Upgrade — v0.29.13 fixed ~20 security issues (OS command injection in git/docker/db paths, cross-org IDORs, credential disclosure, unauthenticated WebSocket handlers).
