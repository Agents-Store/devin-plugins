# Dokploy REST API — AI Router, Debugging & Recovery

REST endpoint reference for the AI router, debugging-oriented endpoints across multiple routers, and recovery actions. Pair this with the `debug-deploy` and `ai-assist` skills.

All endpoints follow `{METHOD} /api/{tag}.{operationName}` with `x-api-key` auth.

## Contents
- [AI Router](#ai-router)
- [Deployment Inspection](#deployment-inspection)
- [Application / Compose Log Endpoints](#application--compose-log-endpoints)
- [Docker Introspection](#docker-introspection)
- [Recovery Actions](#recovery-actions)
- [Rollback](#rollback)
- [Settings — Health & Cleanup](#settings--health--cleanup)
- [Common Diagnostic Curl Recipes](#common-diagnostic-curl-recipes)

---

## AI Router

Dokploy v0.29+ provider-agnostic LLM integration.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/ai.getEnabledProviders` | List currently-enabled providers (empty = AI unavailable) |
| GET | `/api/ai.getAll` | All providers (enabled and disabled) |
| GET | `/api/ai.get` | One provider (input: `aiId`) |
| GET | `/api/ai.one` | Same as `get` (alias) |
| GET | `/api/ai.getModels` | Models advertised by a candidate endpoint. Input: `apiUrl`, `apiKey` (NOT `aiId`) |
| GET | `/api/ai.getCustomProviders` | List org custom provider presets (v0.29.13+) |
| POST | `/api/ai.saveCustomProviders` | Save org custom provider presets. Input: `providers` (v0.29.13+) |
| POST | `/api/ai.create` | Add a provider: `name`, `apiKey`, `apiUrl`, `model`, `isEnabled` |
| POST | `/api/ai.update` | Update provider config |
| POST | `/api/ai.delete` | Remove a provider |
| POST | `/api/ai.testConnection` | Pre-save validation. Input: `apiUrl`, `apiKey`, `model` (NOT `aiId`) |
| POST | `/api/ai.deploy` | Deploy AI orchestrator side-service (admin) |
| POST | `/api/ai.analyzeLogs` | **Headline:** AI-summarise log text. Input: `aiId`, `logs` (the text from a `*.readLogs` call), `context` (`"build"` or `"runtime"`). **Not** `deploymentId` |
| POST | `/api/ai.suggest` | Open-ended recommendations. Input: `aiId`, `input` (question text), optional `serverId` |

### `apiUrl` examples

All providers must speak the OpenAI chat-completions shape:

| Provider | `apiUrl` |
|---|---|
| OpenAI | `https://api.openai.com/v1` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Groq | `https://api.groq.com/openai/v1` |
| Gemini (OpenAI-compatible) | `https://generativelanguage.googleapis.com/v1beta/openai` |
| Anthropic (via OAI proxy) | proxy URL |
| Ollama (self-hosted) | `http://<host>:11434/v1` |

---

## Deployment Inspection

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/deployment.all` | List deployments for an application — filter by `applicationId` (required; only param) |
| GET | `/api/deployment.allByCompose` | Deployments for a compose stack (`composeId`) |
| GET | `/api/deployment.allByServer` | Deployments for a remote server (`serverId`) |
| GET | `/api/deployment.allByType` | Filter by resource: `id`, `type` |
| GET | `/api/deployment.allCentralized` | Every deployment across the instance |
| GET | `/api/deployment.queueList` | Inspect the live deployment queue |
| POST | `/api/deployment.killProcess` | Kill a deployment process by `deploymentId` |
| POST | `/api/deployment.removeDeployment` | Remove a deployment record |

The deployment object includes `status`, `startedAt`, `finishedAt`, `logPath`, `errorMessage`, `triggerType`, and `version` — everything `debug-deploy` Step 1 needs.

---

## Log Endpoints (v0.29.0+ — runtime logs are first-class)

All `readLogs` endpoints are **GET** with query params (URL-encode the `input`). Two kinds of log:

| Method | Endpoint | Params | Returns |
|---|---|---|---|
| GET | `/api/deployment.readLogs` | `deploymentId` (req), `tail` | **Build log** for one deployment |
| GET | `/api/application.readLogs` | `applicationId` (req), `tail`, `since`, `search` | App container **runtime** stdout/stderr |
| GET | `/api/compose.readLogs` | `composeId` (req), **`containerId` (req)**, `tail`, `since`, `search` | **One** compose container's runtime logs |
| GET | `/api/{db}.readLogs` | `{db}Id` (req), `tail`, `since`, `search` | DB container runtime logs (`{db}` ∈ postgres/mysql/mariadb/mongo/redis/libsql) |
| GET | `/api/application.readAppMonitoring` | `applicationId` | CPU / memory / network for an application |
| GET | `/api/application.readTraefikConfig` | `applicationId` | Traefik router/service entries |
| POST | `/api/application.updateTraefikConfig` | `applicationId`, `traefikConfig` | Overwrite Traefik config |

Param ranges: `tail` 1–10000 (default 100); `since` is `all` or `<n>{s|m|h|d}` (e.g. `30m`, `2h`); `search` is a substring filter. The response `.data` is a newline-joined string, each line prefixed with an RFC3339 timestamp.

> **Reading a compose stack = read every container.** `compose.readLogs` is per-container (`containerId` required). Enumerate first via `docker.getContainersByAppNameMatch?appName=<>&appType=docker-compose` (or `docker.getStackContainersByAppName` for swarm), then call `compose.readLogs` once per returned `containerId`. The old [issue #3719](https://github.com/Dokploy/dokploy/issues/3719) "runtime logs not in REST" gap is closed — no SSH/Beszel needed.

---

## Docker Introspection

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/docker.getContainers` | All containers on the host (each `{ containerId, name, state, status }`) |
| GET | `/api/docker.getContainersByAppLabel` | Standalone-app containers by label. Params: `appName`, `type` (**req**: `standalone`/`swarm`) |
| GET | `/api/docker.getContainersByAppNameMatch` | Compose-stack containers by name. Params: `appName`, `appType` (`stack`/`docker-compose`) |
| GET | `/api/docker.getServiceContainersByAppName` | Swarm service containers (`appName`) |
| GET | `/api/docker.getStackContainersByAppName` | Compose/Swarm stack service containers (`appName`) |
| GET | `/api/docker.getConfig` | Full container config (env, command, mounts, network) |
| POST | `/api/docker.startContainer` | Start by `containerId` |
| POST | `/api/docker.stopContainer` | Graceful stop |
| POST | `/api/docker.restartContainer` | Restart in place |
| POST | `/api/docker.killContainer` | SIGKILL |
| POST | `/api/docker.removeContainer` | Hard-delete |
| POST | `/api/docker.uploadFileToContainer` | One-off file push (does NOT survive redeploy) |

---

## Recovery Actions

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/application.killBuild` | Abort the running builder process |
| POST | `/api/application.cancelDeployment` | Cancel queued/in-flight deploy |
| POST | `/api/application.cleanQueues` | Clear the application's stuck queue |
| POST | `/api/application.clearDeployments` | Wipe deployment history (destructive) |
| POST | `/api/application.dropDeployment` | Drop a single deployment record |
| POST | `/api/application.markRunning` | Force `running` status (cosmetic only) |
| POST | `/api/compose.killBuild` | Abort compose builder |
| POST | `/api/compose.cancelDeployment` | Cancel compose deploy |
| POST | `/api/compose.cleanQueues` | Clear compose queue |
| POST | `/api/compose.clearDeployments` | Wipe compose deployment history |
| POST | `/api/settings.cleanAllDeploymentQueue` | Clear stuck queues across every resource |

---

## Rollback

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/rollback.rollback` | Switch a resource to a previously-successful image. Input: `rollbackId` |
| POST | `/api/rollback.delete` | Remove a rollback record |

Rollback points live on the resource object — `application-one` and `compose-one` responses include a `rollbacks` array with `rollbackId`, `version`, `deploymentId`, `createdAt`, and `description`.

---

## Settings — Health & Cleanup

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/settings.health` | Liveness probe (no auth required) |
| GET | `/api/settings.checkInfrastructureHealth` | Docker + Traefik + disk + network composite check |
| GET | `/api/settings.checkGPUStatus` | GPU availability |
| GET | `/api/settings.getDockerDiskUsage` | Per-category disk usage |
| GET | `/api/settings.getLogCleanupStatus` | Log rotation status |
| GET | `/api/settings.getDokployVersion` / `.getReleaseTag` / `.getUpdateData` | Version metadata |
| GET | `/api/settings.getIp` / `.getDokployCloudIps` | Server IPs |
| GET | `/api/settings.getTraefikPorts` | Currently-bound Traefik ports |
| GET | `/api/settings.haveTraefikDashboardPortEnabled` | Dashboard exposure check |
| POST | `/api/settings.cleanDockerBuilder` | Clear BuildKit cache |
| POST | `/api/settings.cleanDockerPrune` | `docker system prune` equivalent |
| POST | `/api/settings.cleanStoppedContainers` | Remove exited containers |
| POST | `/api/settings.cleanUnusedImages` | Remove dangling images |
| POST | `/api/settings.cleanUnusedVolumes` | **Destructive** — orphan volumes |
| POST | `/api/settings.cleanMonitoring` | Reset monitoring data |
| POST | `/api/settings.cleanRedis` | Flush Dokploy's Redis cache |
| POST | `/api/settings.cleanAll` | Combined: builder + prune + monitoring + redis |
| POST | `/api/settings.updateLogCleanup` | Tune log rotation |
| POST | `/api/settings.reloadTraefik` / `.reloadServer` / `.reloadRedis` | Restart subsystems |

---

## Common Diagnostic Curl Recipes

### Find the latest failed deployment for an app

```bash
curl -s -G "$DOKPLOY_URL/api/deployment.all" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode "input={\"json\":{\"applicationId\":\"$APP_ID\"}}" \
  | jq '.result.data.json | map(select(.status=="error")) | sort_by(.startedAt) | last'
```

### Inspect the containers behind an app / compose stack

```bash
# standalone app (type is required)
curl -s -G "$DOKPLOY_URL/api/docker.getContainersByAppLabel" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode 'input={"json":{"appName":"my-app","type":"standalone"}}' \
  | jq '.result.data.json[] | {containerId, name, state, status}'

# compose stack — every service container
curl -s -G "$DOKPLOY_URL/api/docker.getContainersByAppNameMatch" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode 'input={"json":{"appName":"my-stack-ab12cd","appType":"docker-compose"}}' \
  | jq '.result.data.json[] | {containerId, name, state, status}'
```

### Read runtime logs

```bash
# app runtime logs (last 200 lines, last hour, filtered to "error")
curl -s -G "$DOKPLOY_URL/api/application.readLogs" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode 'input={"json":{"applicationId":"app123","tail":200,"since":"1h","search":"error"}}' \
  | jq -r '.result.data.json'

# one compose container's logs (containerId from getContainersByAppNameMatch above)
curl -s -G "$DOKPLOY_URL/api/compose.readLogs" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode 'input={"json":{"composeId":"cmp123","containerId":"a1b2c3d4e5f6","tail":200}}' \
  | jq -r '.result.data.json'
```

### AI-analyse logs (fetch text first, then analyse)

```bash
# 1) fetch the log text (build log here)
LOGS=$(curl -s -G "$DOKPLOY_URL/api/deployment.readLogs" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  --data-urlencode "input={\"json\":{\"deploymentId\":\"$DEPLOY_ID\",\"tail\":1000}}" \
  | jq -r '.result.data.json')

# 2) analyse it ($AI_ID from /api/ai.getEnabledProviders; context "build" or "runtime")
curl -s -X POST "$DOKPLOY_URL/api/ai.analyzeLogs" \
  -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
  -d "$(jq -nc --arg id "$AI_ID" --arg logs "$LOGS" '{json:{aiId:$id,logs:$logs,context:"build"}}')"
```

### Clean disk cache

```bash
for op in cleanDockerBuilder cleanStoppedContainers cleanUnusedImages; do
  curl -s -X POST "$DOKPLOY_URL/api/settings.$op" \
    -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" -d '{"json":{}}'
done
```

### Rollback

```bash
curl -s -X POST "$DOKPLOY_URL/api/rollback.rollback" \
  -H "x-api-key: $DOKPLOY_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"json\":{\"rollbackId\":\"$ROLLBACK_ID\"}}"
```
