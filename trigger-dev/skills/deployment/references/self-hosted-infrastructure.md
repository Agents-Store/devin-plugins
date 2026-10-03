# Self-Hosted Infrastructure

## Architecture (v4)

Trigger.dev v4 self-hosted consists of two Docker Compose stacks (or the Helm chart, see the end):

### Webapp Stack (`hosting/docker/webapp/`)
- **webapp** — Dashboard UI, API server, background workers
- **PostgreSQL** — Primary database
- **Redis** — Queue and caching layer
- **ClickHouse** — Analytics store, required for TRQL queries, dashboards, metrics and LLM cost data. Needs ClickHouse 25.8 or newer; the bundled image is the official `clickhouse/clickhouse-server` (26.2 at the time of writing)
- **Electric** — Realtime sync service
- **s2** (plus the one-shot `s2-init`) — Realtime streams v2 (the default; powers AI-agent token streaming and run streams); fall back to Redis streams with `REALTIME_STREAMS_DEFAULT_VERSION=v1`
- **Container Registry** — Built-in registry for deployed task images
- **MinIO** — S3-compatible object storage for task packets and artifacts

### Worker Stack (`hosting/docker/worker/`)
- **supervisor** — Manages task execution containers (replaces v3 coordinator+provider)
- **Docker Socket Proxy** — Secure Docker access (security improvement over direct socket)

Task events (timeline, logs, spans) are stored in PostgreSQL by default. For production set `EVENT_REPOSITORY_DEFAULT_STORE=clickhouse_v2` on the webapp so the `TaskEvent` table does not grow without bound; it affects new runs only.

## Quick Start

```bash
# Clone the repo
git clone --depth=1 https://github.com/triggerdotdev/trigger.dev
cd trigger.dev/hosting/docker

# Create .env and generate every required secret (no shared defaults since 4.5.6).
# Safe to re-run: it never overwrites a value you already set.
cp .env.example .env
./generate-secrets.sh

# Start webapp (includes all dependencies)
cd webapp && docker compose up -d

# Start worker (supervisor)
cd ../worker && docker compose up -d

# Combined (same machine), from hosting/docker
docker compose -f webapp/docker-compose.yml -f worker/docker-compose.yml up -d
```

`.env.example` leaves `SESSION_SECRET`, `MAGIC_LINK_SECRET`, `ENCRYPTION_KEY`, `MANAGED_WORKER_SECRET` and the Postgres, ClickHouse, registry and MinIO passwords empty; the stack does not boot until they are set. Rotating the encryption key or session secret later invalidates sessions and encrypted data.

Instances installed before 4.5.6 may still use the old published defaults. Before upgrading to 4.5.6 or later, set unique values — or set `ALLOW_INSECURE_DEFAULT_SECRETS=true` to keep booting while you migrate (temporary).

## Worker Token

When webapp and worker run on separate machines, a worker token is required (the combined stack bootstraps it automatically):

1. First start of webapp prints the token in logs (once):
   ```
   TRIGGER_WORKER_TOKEN=tr_wgt_xxxxxxxxxxxxx
   ```
2. Set in worker's `.env`:
   ```
   TRIGGER_WORKER_TOKEN=tr_wgt_xxxxxxxxxxxxx
   ```
3. Set `MANAGED_WORKER_SECRET` on the worker to the **same** value as on the webapp, and `TRIGGER_API_URL` / `OTEL_EXPORTER_OTLP_ENDPOINT` to the public webapp URL. Do **not** run `generate-secrets.sh` on the worker host: it would create a mismatched secret and the worker could not authenticate
4. Restart worker: `docker compose down && docker compose up -d`

## Container Registry

Task deployments build Docker images locally (on the developer or CI machine) and push them to the instance's built-in registry. The Trigger.dev CLI discovers the registry URL from the server automatically but relies on **Docker's own credentials store** for auth — you must `docker login` once per machine (or provide non-interactive login in CI).

### Instance-side env vars (compose `.env` on the host)

The same `.env` feeds the webapp and the supervisor. The webapp compose maps `DOCKER_REGISTRY_URL` to its `DEPLOY_REGISTRY_HOST` and `DOCKER_REGISTRY_NAMESPACE` to `DEPLOY_REGISTRY_NAMESPACE`; the supervisor reads `DOCKER_REGISTRY_*` to pull images.

| Var | Required | Default | Notes |
|-----|----------|---------|-------|
| `DOCKER_REGISTRY_URL` | Yes | `localhost:5000` | Public hostname — e.g. `registry.your-domain.com` |
| `DOCKER_REGISTRY_USERNAME` | Yes | `registry-user` | Basic-auth user in `auth.htpasswd` |
| `DOCKER_REGISTRY_PASSWORD` | Yes | none (empty in `.env.example`) | Filled by `generate-secrets.sh`, which also writes the matching bcrypt `registry/auth.htpasswd` |
| `DOCKER_REGISTRY_NAMESPACE` | Optional | `trigger` | Final image: `{host}/{namespace}/{project-ref}:{tag}`. On Docker Hub use your username |

### Client side (developer + CI)

The Trigger.dev CLI does **not** read `DOCKER_REGISTRY_*` — it only uses Docker's own credentials store, so `docker login` is mandatory on every machine that runs `deploy`. Reusing the same variable names in `.env` / Infisical / Vault keeps the creds in one place and makes `docker login` reproducible:

```bash
DOCKER_REGISTRY_URL=registry.your-domain.com
DOCKER_REGISTRY_USERNAME=registry-user
DOCKER_REGISTRY_PASSWORD=<strong-password>
DOCKER_REGISTRY_NAMESPACE=trigger
```

### Interactive login (dev laptop, one-time)

```bash
docker login -u registry-user registry.your-domain.com
# enter password when prompted
# → Login Succeeded
```

Credentials are saved to `~/.docker/config.json` or the OS keychain; no need to re-login until the password changes.

### Non-interactive login (CI, scripts)

```bash
echo "$DOCKER_REGISTRY_PASSWORD" | docker login \
  "$DOCKER_REGISTRY_URL" \
  -u "$DOCKER_REGISTRY_USERNAME" \
  --password-stdin
```

`--password-stdin` keeps the secret out of process lists and shell history.

### Rotating the registry password

Shipped stacks have no default password (4.5.6+); `generate-secrets.sh` creates one. Instances that still use the old published default must replace it. To rotate:

```bash
# 1. Generate new htpasswd entry (bcrypt)
docker run --rm -it httpd:alpine htpasswd -nbB registry-user 'new-strong-password'
# → registry-user:$2y$05$...

# 2. Replace the line in hosting/docker/registry/auth.htpasswd

# 3. Update DOCKER_REGISTRY_PASSWORD in the webapp .env to the plaintext password

# 4. Restart the registry container
docker compose restart registry

# 5. docker logout + docker login on every machine that deploys
```

### Verify registry is reachable

```bash
curl -s -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/"                      # → {} (HTTP 200)

curl -s -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/_catalog"              # → {"repositories":["trigger/proj_xxx", ...]}
```

## MinIO Object Storage

- UI available at port 9001
- Ensure `packets` bucket exists (created automatically on first start)
- Root credentials come from `OBJECT_STORE_ACCESS_KEY_ID` / `OBJECT_STORE_SECRET_ACCESS_KEY` in the webapp `.env` (the secret is filled by `generate-secrets.sh`); for production create a separate user scoped to the `packets` bucket
- Used for task payloads, outputs, and artifacts

## Version Locking

Pin Docker image versions for stability. The default tag is `latest`; use the version you actually run:

```bash
# In .env
TRIGGER_IMAGE_TAG=v4.7.2
```

Lock the CLI and SDK to the same version (see the **deployment** skill). Only the latest version line receives patches, so plan upgrades. 4.5.0 is the last server version that officially supports v3 (SDK v3) tasks: 4.5.1 and later reject v3 triggers and deploys, so pin exactly `v4.5.0` or migrate to v4 first. Bundled services have their own tags (`CLICKHOUSE_IMAGE_TAG`, `POSTGRES_IMAGE_TAG`, `REDIS_IMAGE_TAG`, ...); bring-your-own ClickHouse (`CLICKHOUSE_URL`) must be 25.8 or newer.

## Upgrading

```bash
# 1. Pull new images
docker compose pull

# 2. Restart services (migrations run automatically)
docker compose down && docker compose up -d

# 3. Redeploy tasks with a CLI at the new server version
npx trigger.dev@<server-version> deploy --env prod
```

### Upgrade notes by version (4.4.4 to 4.7.x)

The server must be at least as new as the SDK version a feature is documented for; the plugin baseline is 4.4.4, so check these before moving a self-hosted instance forward.

| Version | What changes |
|---------|--------------|
| 4.4.5 | Server-side gate on deploys from the v3 CLI (`DEPRECATE_V3_CLI_DEPLOYS_ENABLED`); regenerating an API key gives a 24-hour grace period. Session tables added |
| 4.5.0 | Last server version that officially supports v3 (SDK v3) tasks. Chat agents, Sessions, managed prompts in the SDK, `dev --branch`, `skills` command. AI SDK v4 no longer supported (`ai` `^5`, `^6` or `>=7`) |
| 4.5.1-4.5.5 | v3 tasks are no longer supported (the docs say 4.5.1 onward rejects v3 triggers and deploys); the v3 CLI `dev` was removed in 4.5.3-4.5.4 and an old v3 realtime endpoint in 4.5.5 |
| 4.5.6 | No shared default credentials; unique secrets required, `ALLOW_INSECURE_DEFAULT_SECRETS=true` is a temporary bypass |
| 4.5.7 | `runtime` accepts `node-24` and `node-26`; the `experimental-` aliases are deprecated |
| 4.5.12 | External deployment ids (`deploy --external-id`): version skew protection replaces automatic atomic deployments |
| 4.6.0 | Zod 3.25.56 minimum and Zod 4 by default; reading a session's `.in` stream needs the secret key; `hydrateMessages` deprecated; session snapshot format v2 (rolling back to an old SDK cannot read it). **4.6.0-4.6.3 have a warm-start defect with Zod 3: use 4.6.4 or later** |
| 4.6.2 | Public tokens minted through the JWT endpoint are limited to the key's rights and 24 hours |
| 4.7.0 | `concurrency` option, `concurrencyLimit()`, `concurrencyLimits.*`; `queue.concurrencyLimit` and `queues.overrideConcurrencyLimit` deprecated; `queues.list` / `retrieve` return `version` V1 or V2; MCP `submit_feedback` |
| 4.7.2 | `runtime: "node"` (or unset) follows the current Node.js LTS |

## Creating Additional Worker Groups

```bash
api_url=http://localhost:8030
admin_pat=tr_pat_...

curl -X POST "$api_url/admin/api/v1/workers" \
  -H "Authorization: Bearer $admin_pat" \
  -H "Content-Type: application/json" \
  -d '{"name": "gpu-workers"}'
```

Requires admin privileges (`ADMIN_EMAILS` env var).

## Health Checks

```bash
# Webapp
docker compose ps
curl -s http://localhost:8030/healthcheck

# Registry
curl -s http://localhost:5000/v2/

# MinIO
curl -s http://localhost:9000/minio/health/live

# Supervisor logs
docker compose logs supervisor --tail=20
```

## Telemetry Opt-Out

```yaml
services:
  webapp:
    environment:
      TRIGGER_TELEMETRY_DISABLED: 1
```

## Resource Requirements

| Component | Min vCPU | Min RAM | Recommended |
|-----------|----------|---------|-------------|
| Webapp machine | 3 | 6 GB | 4+ vCPU, 8+ GB |
| Worker machine | 4 | 8 GB | 4+ vCPU, 8+ GB |

The webapp machine hosts: webapp, PostgreSQL, Redis, ClickHouse, Electric, s2, registry, MinIO.
The worker machine hosts: supervisor and spawned task containers.

## What self-hosted does not have

Warm starts, auto-scaling and checkpoints exist only on Trigger.dev Cloud. On self-hosted a run that waits stays `EXECUTING` and keeps holding its container and its concurrency slot; there is no checkpoint-and-release. See the **task-development** skill (Waits).

## Kubernetes (Helm)

A Helm chart is published as an OCI chart: `oci://ghcr.io/triggerdotdev/charts/trigger` (chart releases are tagged `helm-v<version>`). The evaluation install runs everything in-cluster with default values; a production install points the chart at external PostgreSQL, Redis, ClickHouse and object storage and supplies your own secrets. Unset application and datastore secrets are generated on first install and retained across `helm upgrade`. See https://trigger.dev/docs/self-hosting/kubernetes and `helm show values oci://ghcr.io/triggerdotdev/charts/trigger`.
