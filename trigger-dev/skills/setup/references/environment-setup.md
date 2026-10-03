# Environment Setup

Complete guide to environment variables and self-hosted configuration.

## Environment Variables

### Official (SDK / CLI)

| Variable | Description | Example |
|----------|-------------|---------|
| `TRIGGER_API_URL` | Self-hosted instance URL | `https://trigger.example.com` |
| `TRIGGER_ACCESS_TOKEN` | Personal access token for CI/CD and Management API | `tr_pat_xxx` |
| `TRIGGER_PREVIEW_BRANCH` | Preview branch name (optional) | `feature/my-task` |

### Per-Environment Secret Keys

Each environment has its own secret key. Use the environment-specific variable that matches your target:

| Variable | Environment | Format |
|----------|-------------|--------|
| `TRIGGER_DEV_SECRET_KEY` | Development | `tr_dev_xxx` |
| `TRIGGER_STAGE_SECRET_KEY` | Staging | `tr_dev_xxx` (different key than dev) |
| `TRIGGER_PROD_SECRET_KEY` | Production | `tr_prod_xxx` |

`TRIGGER_SECRET_KEY` is the variable the SDK reads by default. In this plugin's convention it holds the key of the environment you are working in (`TRIGGER_SECRET_KEY=$TRIGGER_DEV_SECRET_KEY` locally, the prod key in production); the three per-environment variables above are where all keys are stored side by side. Alternatively pass the appropriate key to the SDK via `configure()`:

```ts
import { configure } from "@trigger.dev/sdk";

configure({
  secretKey: process.env.TRIGGER_DEV_SECRET_KEY, // or STAGE/PROD depending on environment
});
```

### Project Ref (recommended convention)

| Variable | Description | Format |
|----------|-------------|--------|
| `TRIGGER_PROJECT_REF` | Project identifier from the dashboard | `proj_xxxxx` |

The SDK reads the project ref from `trigger.config.ts` (`project` field), not from env. Store it as `TRIGGER_PROJECT_REF` for CI/CD scripts and tooling, then reference it in config:

```ts
export default defineConfig({
  project: process.env.TRIGGER_PROJECT_REF ?? "proj_xxxxx",
  dirs: ["./src/trigger"],
  maxDuration: 300,   // required, seconds (at least 5)
});
```

Find your project ref in the dashboard under **Project Settings**.

### Key Formats

| Format | Environment | Usage |
|--------|-------------|-------|
| `tr_dev_xxx` | Development / Staging | Dev and staging environment tasks |
| `tr_prod_xxx` | Production | Production tasks |
| `tr_pat_xxx` | All environments | CI/CD, Management API |
| Deploy-only API key | One environment | CI deploys; create one per environment in Dashboard → API keys (preferred over a personal access token in CI) |
| `tr_wgt_xxx` | Worker | Worker token for separate machine setup |

### .env Example (all environments)

```bash
# Project
TRIGGER_PROJECT_REF=proj_xxxxx

# Per-environment secret keys
TRIGGER_DEV_SECRET_KEY=tr_dev_xxxxxxxxxxxxxx
TRIGGER_STAGE_SECRET_KEY=tr_dev_yyyyyyyyyyyyyy
TRIGGER_PROD_SECRET_KEY=tr_prod_zzzzzzzzzzzzzz

# Self-hosted instance URL (omit for cloud)
TRIGGER_API_URL=https://trigger.your-domain.com

# CI/CD deploy token
TRIGGER_ACCESS_TOKEN=tr_pat_xxxxxxxxxxxxxx
```

## Self-Hosted v4 Architecture

Trigger.dev v4 self-hosted has two main Docker Compose stacks:

### Webapp Stack
- **webapp** — Dashboard, API, background workers
- **PostgreSQL** — Primary database
- **Redis** — Queue and caching
- **ClickHouse** — Required for TRQL queries, dashboards, metrics and LLM cost data; needs ClickHouse 25.8 or newer (the bundled image is the official `clickhouse/clickhouse-server`, currently 26.2)
- **Electric** — Realtime sync service
- **s2** (plus a one-shot `s2-init`) — realtime streams v2, the default; set `REALTIME_STREAMS_DEFAULT_VERSION=v1` for the Redis-backed v1 streams
- **Container Registry** — Stores deployed task images
- **MinIO** — Object storage for task packets and artifacts

For production event storage set `EVENT_REPOSITORY_DEFAULT_STORE=clickhouse_v2` on the webapp (the default store is PostgreSQL; the setting affects new runs only).

### Worker Stack (Supervisor)
- **supervisor** — Manages task execution containers
- **Docker Socket Proxy** — Secure Docker access (replaces direct socket)

The v3 coordinator+provider are replaced by a single **supervisor** in v4. A Kubernetes Helm chart (`oci://ghcr.io/triggerdotdev/charts/trigger`) is also published; see https://trigger.dev/docs/self-hosting/kubernetes.

## Secrets (4.5.6+)

Since 4.5.6 self-hosted ships **no shared default credentials**. Generate them once:

```bash
cd trigger.dev/hosting/docker
cp .env.example .env
./generate-secrets.sh   # safe to re-run; never overwrites a value already set
```

`SESSION_SECRET`, `MAGIC_LINK_SECRET`, `ENCRYPTION_KEY`, `MANAGED_WORKER_SECRET` and the Postgres, ClickHouse, registry and MinIO passwords are required and empty in `.env.example`; the stack does not boot until they are set. `generate-secrets.sh` also writes `registry/auth.htpasswd` to match the registry password. Rotating the encryption key or session secret later invalidates existing sessions and encrypted data.

Upgrading an instance that still runs the old published defaults (a registry password, MinIO root credentials) requires a unique value first, or `ALLOW_INSECURE_DEFAULT_SECRETS=true` as a temporary bypass while you migrate.

## Worker Token

When running webapp and worker on separate machines:

1. First start of webapp prints the worker token in logs (shown once):
   ```
   TRIGGER_WORKER_TOKEN=tr_wgt_xxxxxxxxxxxxx
   ```
2. Set this in the worker's `.env` file
3. Set `MANAGED_WORKER_SECRET` on the worker to the **same** value as on the webapp, and set `TRIGGER_API_URL` to the public webapp URL. Do not run `generate-secrets.sh` on the worker host: it would create a mismatched secret and the worker could not authenticate
4. Restart the worker: `docker compose down && docker compose up -d`

## Docker Compose Quick Start

```bash
# Clone the repo
git clone --depth=1 https://github.com/triggerdotdev/trigger.dev
cd trigger.dev/hosting/docker

# Start webapp stack
cd webapp && docker compose up -d

# Start worker stack (same or separate machine)
cd ../worker && docker compose up -d
```

## Registry Configuration

Trigger.dev v4 uses a built-in container registry for task deployments. The registry user is `registry-user`; the password is whatever `generate-secrets.sh` wrote to `DOCKER_REGISTRY_PASSWORD` in `.env` (and, bcrypt-hashed, to `hosting/docker/registry/auth.htpasswd`):

```bash
docker login -u registry-user localhost:5000
# Password: the DOCKER_REGISTRY_PASSWORD value from the instance's .env
```

The compose file maps `DOCKER_REGISTRY_URL` to the webapp's `DEPLOY_REGISTRY_HOST` and `DOCKER_REGISTRY_NAMESPACE` to `DEPLOY_REGISTRY_NAMESPACE`; the supervisor reads `DOCKER_REGISTRY_*` to pull images. The CLI reads none of them, so `docker login` on every deploying machine is mandatory.

## MinIO Object Storage

MinIO provides S3-compatible storage for task packets:
- UI available at port 9001
- Ensure the `packets` bucket exists
- Root credentials come from `OBJECT_STORE_ACCESS_KEY_ID` / `OBJECT_STORE_SECRET_ACCESS_KEY` in the webapp `.env` (filled by `generate-secrets.sh`); for production use a separate non-root user scoped to the `packets` bucket

## Version Locking

Pin Docker image versions in your `.env`:

```bash
# A version you actually run; the default is `latest`
TRIGGER_IMAGE_TAG=v4.7.2
```

Lock the CLI and SDK to the same version. Patches are released only for the latest version line. 4.5.0 is the last server version that officially supports v3 tasks; 4.5.1 and later reject v3 triggers and deploys. If you pin or bring your own ClickHouse (`CLICKHOUSE_IMAGE_TAG`, `CLICKHOUSE_URL`), it must be 25.8 or newer.

## Telemetry Opt-Out

```yaml
services:
  webapp:
    environment:
      TRIGGER_TELEMETRY_DISABLED: 1
```

## Upgrading Self-Hosted

1. Pull new images: `docker compose pull`
2. Stop services: `docker compose down`
3. Start services: `docker compose up -d` (migrations run automatically)
4. Redeploy tasks: `npx trigger.dev@<server-version> deploy --env prod`

## SDK Configuration (programmatic)

```ts
import { configure } from "@trigger.dev/sdk";

configure({
  secretKey: process.env.TRIGGER_DEV_SECRET_KEY, // or TRIGGER_STAGE_SECRET_KEY / TRIGGER_PROD_SECRET_KEY
  baseURL: process.env.TRIGGER_API_URL,          // self-hosted instance URL
});
```
