---
name: deployment
description: Deploy Trigger.dev tasks to staging, production, or preview environments. Use when the user asks to "deploy trigger.dev tasks", "set up CI/CD for trigger.dev", "deploy to production", "deploy self-hosted trigger", "manage environments", or needs deployment workflows and self-hosted infrastructure guidance.
---

# Deployment

Deploy Trigger.dev tasks to staging, production, or preview environments.

## Deploy Cycle

1. Develop locally with `npx trigger.dev@latest dev`
2. Deploy to staging: `npx trigger.dev@latest deploy --env staging`
3. Test in staging
4. Deploy to production: `npx trigger.dev@latest deploy --env production`
5. Verify: check dashboard or `list_deploys` MCP tool

## CLI Deploy

```bash
# Deploy to production (default)
npx trigger.dev@latest deploy

# Deploy to staging
npx trigger.dev@latest deploy --env staging

# Deploy to preview branch
npx trigger.dev@latest deploy --env preview --branch feature/new-task

# Deploy without promoting (canary)
npx trigger.dev@latest deploy --skip-promotion
```

## Deploy Flags

| Flag | Description |
|------|-------------|
| `--env <environment>` | Target: staging, prod, preview |
| `--api-url <url>` | Self-hosted server URL (default: `https://api.trigger.dev`) |
| `--env-file <path>` | Load .env file into CLI process (default: `.env`) |
| `--branch <name>` | Branch name (required for preview) |
| `--skip-promotion` | Deploy without making it active |
| `--skip-update-check` | Skip package version check |
| `--skip-sync-env-vars` | Skip syncEnvVars extension |
| `--config <path>` | Custom trigger.config.ts path |
| `--project-ref <ref>` | Override project ref |
| `--dry-run` | Show what would be deployed without deploying |
| `--local-build` | Build Docker image locally |

## Self-Hosted Deploy

For self-hosted instances, pass `--api-url` pointing to your Trigger.dev server and authenticate with `TRIGGER_ACCESS_TOKEN`:

```bash
# Option A: Use a Personal Access Token (from `trigger.dev login`)
TRIGGER_ACCESS_TOKEN=tr_pat_xxx \
npx trigger.dev@latest deploy \
  --env prod \
  --api-url https://your-trigger-instance.example.com \
  --env-file .env

# Option B: Use the project secret key as access token
# This works when the CLI profile token doesn't have access to the project
TRIGGER_ACCESS_TOKEN=$TRIGGER_SECRET_KEY \
npx trigger.dev@latest deploy \
  --env prod \
  --api-url https://your-trigger-instance.example.com \
  --project-ref proj_xxx \
  --env-file .env
```

If the CLI says "Project not found" even though the project exists, the CLI profile token likely lacks access to the project's organization. Use Option B (`TRIGGER_SECRET_KEY` as `TRIGGER_ACCESS_TOKEN`) to authenticate with the project-scoped key instead.

There is no `--self-hosted` flag — self-hosted and cloud deploys use the same CLI command, only `--api-url` differs (cloud default: `https://api.trigger.dev`).

The CLI automatically discovers the container registry from the server and handles Docker build + push internally.

## Container Registry Login (Self-Hosted Only)

When deploying to a self-hosted instance, the CLI builds the task image **locally** and pushes it to the instance's built-in container registry (served at `registry.<your-domain>` or `localhost:5000` in the default setup). The CLI does **not** prompt for registry credentials — it uses whatever Docker has in its credentials keychain from a prior `docker login`.

If `docker login` was never run on the machine (fresh laptop, fresh CI runner), deploy fails at the push step with:
```
denied: requested access to the resource is denied
# or
unauthorized: authentication required
# or
no basic auth credentials
```

### Two separate sets of registry env vars

| Scope | Var prefix | Who reads them | Purpose |
|-------|-----------|----------------|---------|
| **Server** (webapp docker-compose) | `DEPLOY_REGISTRY_*` | Trigger.dev webapp | Tells the server which registry to instruct CLIs to push to |
| **Client** (dev machine / CI) | `DOCKER_REGISTRY_*` *(convention)* | `docker login` via a shell wrapper | Stores registry creds in `.env` / secrets manager for non-interactive login |

The `DOCKER_REGISTRY_*` prefix is **not read by the Trigger.dev CLI** — it's a project convention for feeding `docker login` in a reproducible way (so secrets live in Infisical / .env alongside other service creds, not only in Docker's OS keychain).

**Server-side variables** (official, set in webapp's `.env` on the host):

| Var | Required | Default | Purpose |
|-----|----------|---------|---------|
| `DEPLOY_REGISTRY_HOST` | Yes | `localhost:5000` | Hostname CLIs will push to |
| `DEPLOY_REGISTRY_USERNAME` | Optional | `registry-user` | Basic-auth username |
| `DEPLOY_REGISTRY_PASSWORD` | Optional | `very-secure-indeed` | Basic-auth password (⚠️ CHANGE for prod — update `hosting/docker/registry/auth.htpasswd`) |
| `DEPLOY_REGISTRY_NAMESPACE` | Optional | `trigger` | Image namespace; final image path: `{host}/{namespace}/{project-ref}` |

**Client-side convention** (stored in project `.env` / Infisical alongside other creds):

```bash
DOCKER_REGISTRY_URL=registry.your-trigger-domain.com
DOCKER_REGISTRY_USERNAME=registry-user
DOCKER_REGISTRY_PASSWORD=<strong-password>
DOCKER_REGISTRY_NAMESPACE=trigger
```

### Login — interactive (dev laptop, one-time)

```bash
docker login -u registry-user registry.your-trigger-domain.com
# enter password at prompt
# → Login Succeeded (credentials saved to ~/.docker/config.json or OS keychain)
```

Once done, `npm run deploy:staging` / `deploy:production` works for all future deploys on this machine until credentials change.

### Login — non-interactive (CI, reproducible)

Use `--password-stdin` so the password never appears in process lists or shell history:

```bash
echo "$DOCKER_REGISTRY_PASSWORD" | docker login \
  "$DOCKER_REGISTRY_URL" \
  -u "$DOCKER_REGISTRY_USERNAME" \
  --password-stdin
```

Add this as a step **before** `trigger.dev deploy` in any CI pipeline.

### Verify registry connectivity

```bash
# Should return HTTP 200 and {} when auth is correct
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/"

# List repositories (expect: {"repositories":["trigger/proj_xxx", ...]})
curl -s -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/_catalog"

# List tags for a specific project
curl -s -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/$DOCKER_REGISTRY_NAMESPACE/$TRIGGER_PROJECT_REF/tags/list"
```

If `/v2/` returns `401`, the credentials are wrong. If it returns `404`, `DOCKER_REGISTRY_URL` is wrong or the host is not a Docker registry.

### When to re-login

- Password rotated in `auth.htpasswd` on the server → `docker logout $URL` + fresh login with new password
- New CI runner / fresh laptop → login step required
- "credentials store" changed on the machine → re-login to populate it

## Self-Hosted Runtime Environment Variables

Deployed tasks run in isolated Docker containers that do **not** have access to your local `.env` file. The `--env-file` flag only loads env vars into the CLI process during build — they are NOT available at runtime.

The `deploy.env` option in `trigger.config.ts` may not propagate env vars to self-hosted runtime containers. To reliably set runtime env vars, use one of these methods:

### Method 1: REST API (recommended for automation)

```bash
# Set a single env var for the prod environment
curl -X POST "$TRIGGER_API_URL/api/v1/projects/$TRIGGER_PROJECT_REF/envvars/prod" \
  -H "Authorization: Bearer $TRIGGER_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "MY_API_KEY", "value": "sk-xxx"}'

# Script to sync all required vars from .env.local
for var_name in DIRECTUS_URL API_KEY OTHER_VAR; do
  eval var_value=\$$var_name
  curl -s -X POST "$TRIGGER_API_URL/api/v1/projects/$TRIGGER_PROJECT_REF/envvars/prod" \
    -H "Authorization: Bearer $TRIGGER_SECRET_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$var_name\", \"value\": \"$var_value\"}"
done
```

### Method 2: Dashboard UI

Navigate to `$TRIGGER_API_URL/projects/v3/$PROJECT_REF/environment-variables` and add vars manually.

### Common symptom

If a deployed task fails with `TypeError: Failed to parse URL from undefined/...`, the env var providing the base URL is missing from the runtime environment. Set it via the API or dashboard.

## Environments

| Environment | Key Format | Convention Var | Purpose |
|-------------|-----------|----------------|---------|
| dev | `tr_dev_xxx` | `TRIGGER_DEV_SECRET_KEY` | Local development |
| staging | `tr_dev_xxx` (different key) | `TRIGGER_STAGE_SECRET_KEY` | Testing before prod |
| production | `tr_prod_xxx` | `TRIGGER_PROD_SECRET_KEY` | Live traffic |
| preview | `tr_dev_xxx` | — | Feature branch testing |

Each environment has its own unique secret key. Staging uses the `tr_dev_` prefix but it is NOT the same key as development. Pass the appropriate per-env key to the SDK via `configure()`.

## CI/CD (GitHub Actions)

For **self-hosted**, add a `docker login` step before `deploy` — the runner has no Docker credentials by default and the push will fail with "unauthorized". For **cloud** (api.trigger.dev), skip the docker login step.

```yaml
name: Deploy Trigger.dev
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci

      # Required for self-hosted only — push target is the instance's built-in registry
      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to production
        run: npx trigger.dev@latest deploy --env production
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          # For self-hosted:
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

Required GitHub Actions secrets for self-hosted: `TRIGGER_ACCESS_TOKEN`, `TRIGGER_API_URL`, `DOCKER_REGISTRY_URL`, `DOCKER_REGISTRY_USERNAME`, `DOCKER_REGISTRY_PASSWORD`.

## Deployment Status Values

| Status | Description |
|--------|-------------|
| PENDING | Queued |
| BUILDING | Building project |
| DEPLOYING | Pushing to environment |
| DEPLOYED | Successfully deployed |
| FAILED | Build or deploy failed |
| CANCELED | Deployment cancelled |
| TIMED_OUT | Build/deploy timed out |

## Package.json Scripts

```json
{
  "scripts": {
    "trigger:dev": "trigger.dev dev",
    "trigger:deploy:staging": "trigger.dev deploy --env staging",
    "trigger:deploy:prod": "trigger.dev deploy --env production"
  }
}
```

## Post-Deploy Verification

After every deploy, verify tasks actually work — a successful deploy does NOT mean tasks run correctly. Environment variables, API endpoints, and data dependencies can all fail silently at runtime.

1. **Check recent runs** — use `list_runs` MCP tool (or dashboard) to see if tasks are failing
2. **Trigger each task** — use `trigger_task` MCP tool with test payloads to exercise all deployed tasks
3. **Wait and inspect** — use `wait_for_run_to_complete` and `get_run_details` to check for errors
4. **Common post-deploy failures:**
   - `undefined` in URLs → missing env vars (need `syncEnvVars` extension)
   - `401 Unauthorized` → expired or wrong API tokens in env vars
   - `Cannot read properties of null` → task code expects data that doesn't exist yet

Never declare a deploy done without triggering at least one test run per task.

## Deeper Reference

- @references/deploy-reference.md — preview branches, monorepo deploy
- @references/ci-cd-patterns.md — GitHub Actions, GitLab CI patterns
- @references/self-hosted-infrastructure.md — Docker Compose, supervisor, registry
