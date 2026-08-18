# Self-Hosted Infrastructure

## Architecture (v4)

Trigger.dev v4 self-hosted consists of two Docker Compose stacks:

### Webapp Stack (`hosting/docker/webapp/`)
- **webapp** — Dashboard UI, API server, background workers
- **PostgreSQL** — Primary database
- **Redis** — Queue and caching layer
- **Container Registry** — Built-in registry for deployed task images
- **MinIO** — S3-compatible object storage for task packets and artifacts

### Worker Stack (`hosting/docker/worker/`)
- **supervisor** — Manages task execution containers (replaces v3 coordinator+provider)
- **Docker Socket Proxy** — Secure Docker access (security improvement over direct socket)

## Quick Start

```bash
# Clone the repo
git clone --depth=1 https://github.com/triggerdotdev/trigger.dev
cd trigger.dev/hosting/docker

# Start webapp (includes all dependencies)
cd webapp && docker compose up -d

# Start worker (supervisor)
cd ../worker && docker compose up -d

# Combined (same machine)
docker compose -f webapp/docker-compose.yml -f worker/docker-compose.yml up -d
```

## Worker Token

When webapp and worker run on separate machines, a worker token is required:

1. First start of webapp prints the token in logs:
   ```
   TRIGGER_WORKER_TOKEN=tr_wgt_xxxxxxxxxxxxx
   ```
2. Set in worker's `.env`:
   ```
   TRIGGER_WORKER_TOKEN=tr_wgt_xxxxxxxxxxxxx
   ```
3. Restart worker: `docker compose down && docker compose up -d`

## Container Registry

Task deployments build Docker images locally (on the developer or CI machine) and push them to the instance's built-in registry. The Trigger.dev CLI discovers the registry URL from the server automatically but relies on **Docker's own credentials store** for auth — you must `docker login` once per machine (or provide non-interactive login in CI).

### Server-side env vars (webapp docker-compose `.env`)

These are read by the webapp container and determine what CLIs are told to push to:

| Var | Required | Default | Notes |
|-----|----------|---------|-------|
| `DEPLOY_REGISTRY_HOST` | Yes | `localhost:5000` | Public hostname — e.g. `registry.your-domain.com` |
| `DEPLOY_REGISTRY_USERNAME` | Optional | `registry-user` | Basic-auth user in `auth.htpasswd` |
| `DEPLOY_REGISTRY_PASSWORD` | Optional | `very-secure-indeed` | Must match htpasswd entry |
| `DEPLOY_REGISTRY_NAMESPACE` | Optional | `trigger` | Final image: `{host}/{namespace}/{project-ref}:{tag}` |

### Client-side convention (developer + CI `.env`)

The Trigger.dev CLI does **not** read `DOCKER_REGISTRY_*` vars — they are a project convention for storing registry creds alongside other service creds (Infisical, Vault, .env) and feeding `docker login` in a reproducible way:

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

### Default credentials — CHANGE IN PRODUCTION

The shipped defaults (`registry-user` / `very-secure-indeed` at `localhost:5000`) are for local testing only. To rotate:

```bash
# 1. Generate new htpasswd entry (bcrypt)
docker run --rm -it httpd:alpine htpasswd -nbB registry-user 'new-strong-password'
# → registry-user:$2y$05$...

# 2. Replace line in hosting/docker/registry/auth.htpasswd

# 3. Update DEPLOY_REGISTRY_PASSWORD in webapp .env to the plaintext password

# 4. Restart registry container
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
- Default credentials in webapp `.env`
- Used for task payloads, outputs, and artifacts

## Version Locking

Pin Docker image versions for stability:

```bash
# In .env
TRIGGER_IMAGE_TAG=v4.0.0
```

## Upgrading

```bash
# 1. Pull new images
docker compose pull

# 2. Restart services (migrations run automatically)
docker compose down && docker compose up -d

# 3. Redeploy tasks
npx trigger.dev@latest deploy --env production
```

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

The webapp machine hosts: webapp, PostgreSQL, Redis, registry, MinIO.
The worker machine hosts: supervisor and spawned task containers.
