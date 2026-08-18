# Dokploy REST API — Schedules, Patches, Volume Backups & Preview Deployments

REST endpoint reference for the four routers introduced/expanded in Dokploy v0.29+. Tool names use the same `{tag}.{operationName}` shape.

## Contents
- [Schedule Router](#schedule-router)
- [Patch Router](#patch-router)
- [Volume Backups](#volume-backups)
- [Preview Deployments](#preview-deployments)

---

## Schedule Router

Cron-like scheduled tasks. A schedule fires a command on a target at every cron tick.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/schedule.list` | List schedules — params: `id` (target resource id), `scheduleType` (`application`\|`compose`\|`server`\|`dokploy-server`), both required |
| GET | `/api/schedule.one` | Read one schedule by `scheduleId` |
| POST | `/api/schedule.create` | Create a schedule |
| POST | `/api/schedule.update` | Update a schedule |
| POST | `/api/schedule.delete` | Remove a schedule |
| POST | `/api/schedule.runManually` | Trigger the schedule immediately |

### `schedule.create` fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Human-readable name |
| `cronExpression` | string | Standard 5-field cron (e.g. `"0 3 * * *"`) |
| `command` | string | Shell command to execute |
| `applicationId` | string | Bind to an app — runs inside the app container |
| `composeId` | string | Bind to a compose stack — pair with `serviceName` |
| `serviceName` | string | Compose service name (required when `composeId` is set) |
| `serverId` | string | Bind to a remote server — runs on the host |
| `dokployServer` | boolean | If true, runs on the Dokploy host itself |
| `enabled` | boolean | Toggle without deleting |
| `timezone` | string | Timezone for the cron schedule |

Exactly one of `applicationId` / `composeId` / `serverId` / `dokployServer: true` must be set. Since v0.29.8, Dokploy-host schedules are organization-scoped (`organizationId`, formerly `userId`).

### Common use cases

- DB maintenance — nightly `VACUUM ANALYZE` on a Postgres compose service.
- Cache warm — re-prime a Redis cache from a stale source.
- Health pings — `curl` an external monitor.
- Cert-renewal hooks — chain a script after Traefik's renewal cycle.

### Curl: schedule a nightly Postgres vacuum

```bash
curl -s -X POST "$DOKPLOY_URL/api/schedule.create" \
  -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "json": {
      "name": "Nightly VACUUM",
      "cronExpression": "0 3 * * *",
      "command": "psql -U postgres -d main -c \"VACUUM ANALYZE;\"",
      "composeId": "comp_abc123",
      "serviceName": "postgres",
      "enabled": true
    }
  }'
```

---

## Patch Router

File-level overlays applied at deploy time. Each patch is a small git-backed workspace that Dokploy materialises and merges over the source tree before building.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/patch.one` | Read one patch by `patchId` |
| GET | `/api/patch.byEntityId` | List patches for an entity (`id`, `type` — both required) |
| POST | `/api/patch.create` | Create a patch record (`filePath`, `content` required) |
| POST | `/api/patch.update` | Update patch metadata (`patchId`) |
| POST | `/api/patch.delete` | Remove a patch (`patchId`) |
| POST | `/api/patch.toggleEnabled` | Enable/disable without deleting (`patchId`, `enabled`) |
| POST | `/api/patch.ensureRepo` | Materialise the patch's workspace (`id`, `type`) |
| POST | `/api/patch.cleanPatchRepos` | GC orphan patch workspaces (optional `serverId`) |
| GET | `/api/patch.readRepoDirectories` | List directories inside the patch workspace (`id`, `type`, `repoPath`) |
| GET | `/api/patch.readRepoFile` | Read a file from the patch workspace (`id`, `type`, `filePath`) |
| POST | `/api/patch.saveFileAsPatch` | Save a modified file as a patch overlay (`id`, `type`, `filePath`, `content`, `patchType`) |
| POST | `/api/patch.markFileForDeletion` | Mark a file for deletion during patch apply (`id`, `type`, `filePath`) |

### `patch.create` fields

| Field | Type | Notes |
|---|---|---|
| `filePath` | string | Required — path of the file the patch overrides |
| `content` | string | Required — the file content |
| `type` | string | `"application"` or `"compose"` |
| `applicationId` / `composeId` | string | The entity this patch applies to |
| `enabled` | boolean | Whether to apply on next deploy |

Repo-workspace operations address the entity via `id` (applicationId/composeId) + `type` — not `patchId`.

### Workflow

1. `patch.create` registers the patch record.
2. `patch.ensureRepo` materialises a git workspace.
3. `patch.readRepoDirectories` / `patch.readRepoFile` to explore.
4. `patch.saveFileAsPatch` (or `patch.markFileForDeletion`) to record the override.
5. `patch.toggleEnabled` to activate.
6. Next deploy applies the overlay before the build step.

### Use cases

- Override a config file in an upstream image without forking.
- Inject an extra env file at a specific path the app expects.
- Remove a debug file shipped in the source tree before production builds.

---

## Volume Backups

Raw Docker volume snapshots — distinct from the `backup` router which understands database-level dumps.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/volumeBackups.list` | List volume backup configs — params: `id` (resource id), `volumeBackupType`, both required |
| GET | `/api/volumeBackups.one` | One config by `volumeBackupId` |
| POST | `/api/volumeBackups.create` | Configure a recurring volume backup |
| POST | `/api/volumeBackups.update` | Update config |
| POST | `/api/volumeBackups.delete` | Remove config |
| POST | `/api/volumeBackups.runManually` | One-off backup outside the schedule |

### `volumeBackups.create` fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Human-readable name |
| `volumeName` | string | Docker volume name (find via `docker.getConfig` Mounts section) |
| `destinationId` | string | Pre-configured `destination-*` (S3, R2, etc.) |
| `cronExpression` | string | Schedule (e.g. `"0 2 * * 0"` — weekly Sundays at 02:00) |
| `applicationId` / `composeId` / `serverId` | string | Resource binding (exactly one) |
| `enabled` | boolean | Toggle without deleting |

### When to use

- Non-database persistent state — user uploads, ML models, build artifacts.
- Anything where `docker run --volumes-from` is the natural backup path rather than `pg_dump` / `mysqldump`.

For DB-aware dumps (Postgres logical, Mongo bson, etc.), use the `backup-*` router (see `api-server-settings.md`).

---

## Preview Deployments

Ephemeral per-PR / per-branch deploys spawned alongside the main application. Trigger mechanism differs between Cloud (direct exec) and self-hosted (queue).

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/previewDeployment.all` | List preview deployments (`applicationId` required) |
| GET | `/api/previewDeployment.one` | One preview by `previewDeploymentId` |
| POST | `/api/previewDeployment.redeploy` | Force a fresh build |
| POST | `/api/previewDeployment.delete` | Tear down a preview environment |

Preview deployments inherit the main app's build config, env, and domain pattern (Dokploy generates a unique subdomain per preview). They're typically triggered automatically by Git webhook on PR open/sync — the MCP/REST surface above is for inspection and manual lifecycle.

### Common lifecycle

1. PR opened → webhook → Dokploy creates preview deployment.
2. PR pushed → webhook → Dokploy calls `previewDeployment.redeploy` internally.
3. PR closed → webhook → Dokploy calls `previewDeployment.delete` automatically.

Manual cleanup:

```bash
curl -s -X POST "$DOKPLOY_URL/api/previewDeployment.delete" \
  -H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json" \
  -d "{\"json\":{\"previewDeploymentId\":\"$ID\"}}"
```
