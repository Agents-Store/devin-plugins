---
name: deployment
description: Deploy Trigger.dev tasks to staging, production, or preview environments. Use when the user asks to "deploy trigger.dev tasks", "set up CI/CD for trigger.dev", "deploy to production", "deploy self-hosted trigger", "manage environments", or needs deployment workflows and self-hosted infrastructure guidance.
---

# Deployment

Deploy Trigger.dev tasks to staging, production, or preview environments.

## Deploy Cycle

1. Develop locally with `npx trigger.dev@latest dev`
2. Deploy to staging: `npx trigger.dev@<version> deploy --env staging`
3. Test in staging
4. Deploy to production: `npx trigger.dev@<version> deploy --env prod`
5. Verify: check dashboard or `list_deploys` MCP tool

`<version>` is the version of `@trigger.dev/sdk` your project uses; on self-hosted it must also be the version of the server. A CLI that differs from the installed `@trigger.dev/*` packages makes `deploy` fail in CI and behave unpredictably elsewhere, so keep the `trigger.dev` package in `devDependencies` and run it through `npm run` / `npx trigger.dev` instead of `@latest` (see CI/CD below).

## CLI Deploy

```bash
# Deploy to production (default env is prod)
npx trigger.dev@<version> deploy

# Deploy to staging
npx trigger.dev@<version> deploy --env staging

# Deploy to preview branch
npx trigger.dev@<version> deploy --env preview --branch feature/new-task

# Deploy without promoting (canary), promote later
npx trigger.dev@<version> deploy --skip-promotion
npx trigger.dev@<version> promote <deployed-version>
```

## Deploy Flags

| Flag | Description |
|------|-------------|
| `-e, --env <environment>` | Target: `prod` (default), `staging`, `preview`. `production` is coerced to `prod`, but write `prod` |
| `-a, --api-url <url>` | Self-hosted server URL (default: cloud) |
| `--profile <name>` | CLI login profile |
| `--env-file <path>` | Load .env file into CLI process (default: `.env`) |
| `-b, --branch <name>` | Preview branch (detected from git when omitted, with `--env preview`) |
| `--skip-promotion` | Deploy without making it active |
| `--skip-update-check` | Skip package version check |
| `--skip-sync-env-vars` | Skip syncEnvVars extension |
| `-c, --config <path>` | Custom trigger.config.ts path |
| `-p, --project-ref <ref>` | Override project ref |
| `--dry-run` | Show what would be deployed without deploying |
| `--external-id <id>` | Your own id for the deploy (commit SHA, CI run id, release tag; max 128 characters). Deploying an id that is already live reports the existing version instead of building again. Basis of version skew protection (below). Requires server ≥ 4.5.12 (CLI/SDK must match); an older CLI rejects the flag |
| `--force` | Rebuild even if the `--external-id` is already deployed; needs `--external-id` (same version requirement) |
| `--local-build` | Build the Docker image locally |
| `--native-build` | Build on the native build server (cloud build options) |
| `--depot-build` | Build with Depot (cloud build options) |
| `--local-bundle` | Experimental: bundle locally, upload only the output; requires `--native-build` |
| `--detach` | Return as soon as the deploy is queued; requires `--native-build` |
| `--build-logs <mode>` | `compact` (one updating line, default) or `full`; CI and piped output always use `full` |

On self-hosted, builds run locally on the machine that runs `deploy`, so the native and Depot build options do not apply there.

## Version Skew Protection (requires server ≥ 4.5.12; CLI/SDK must match)

Automatic atomic deployments are deprecated in favour of version skew protection. Give each deploy an id, give your running app the same id, and Trigger.dev pins every triggered run to the deployment built for that release:

```bash
npx trigger.dev@<version> deploy --env prod --external-id "$GITHUB_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
# and in the application's runtime environment, the same value:
# TRIGGER_EXTERNAL_DEPLOYMENT_ID=<same commit sha>
```

Make sure the id cannot expand to an empty string (an unset variable silently deploys with no id), and do not add a `paths:` filter to the workflow when the id is a commit SHA: commits that do not touch tasks never produce a deployment with that SHA, so their runs expire after an hour. Without a matching id nothing changes: runs execute on the current version.

## Self-Hosted Deploy

For self-hosted instances, pass `--api-url` (or set `TRIGGER_API_URL`) pointing to your Trigger.dev server and authenticate with `TRIGGER_ACCESS_TOKEN`. There is no self-hosted-specific deploy flag: cloud and self-hosted use the same command, only the URL differs.

```bash
# Option A — local machine: personal access token from `trigger.dev login`
TRIGGER_ACCESS_TOKEN=tr_pat_xxx \
npx trigger.dev@<server-version> deploy \
  --env prod \
  --api-url https://your-trigger-instance.example.com \
  --env-file .env

# Option B — CI: an environment API key with "Deploy only" access, one per environment
# (Dashboard -> project -> environment -> API keys -> New API key). It is passed as
# TRIGGER_ACCESS_TOKEN and is not tied to one person's account.
TRIGGER_ACCESS_TOKEN=<deploy-only-key-for-prod> \
TRIGGER_API_URL=https://your-trigger-instance.example.com \
npx trigger.dev@<server-version> deploy --env prod --external-id "$GITHUB_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
```

Deploy-only keys are documented for Trigger.dev Cloud; confirm they exist on your server version before relying on them. A personal access token is the documented fallback, but it is tied to a person and not recommended for CI.

```bash
# Option C — workaround seen on some self-hosted instances (not documented upstream):
# the project's secret key as the access token, when the profile token is rejected
TRIGGER_ACCESS_TOKEN=$TRIGGER_SECRET_KEY \
npx trigger.dev@<server-version> deploy \
  --env prod \
  --api-url https://your-trigger-instance.example.com \
  --project-ref proj_xxx \
  --env-file .env
```

If the CLI says "Project not found" even though the project exists, the CLI profile token likely lacks access to the project's organization. Use Option B or C to authenticate with an environment-scoped key instead.

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

### Registry env vars: who reads what

| Scope | Var prefix | Who reads them | Purpose |
|-------|-----------|----------------|---------|
| **Server** (webapp docker-compose) | `DEPLOY_REGISTRY_*` | Trigger.dev webapp | Tells the server which registry to instruct CLIs to push to |
| **Instance `.env`** | `DOCKER_REGISTRY_*` | docker compose (webapp and supervisor) | Registry URL, user, password, namespace of the instance |
| **Client** (dev machine / CI) | `DOCKER_REGISTRY_*` *(same names, by convention)* | `docker login` via a shell wrapper | Stores registry creds in `.env` / secrets manager for non-interactive login |

The Trigger.dev **CLI does not read** `DOCKER_REGISTRY_*`, so `docker login` is always needed. The names are not arbitrary though: the instance's `.env.example` and compose files use `DOCKER_REGISTRY_URL`, `DOCKER_REGISTRY_USERNAME`, `DOCKER_REGISTRY_PASSWORD` and `DOCKER_REGISTRY_NAMESPACE`. The webapp compose maps `DOCKER_REGISTRY_URL` to `DEPLOY_REGISTRY_HOST` and `DOCKER_REGISTRY_NAMESPACE` to `DEPLOY_REGISTRY_NAMESPACE`, and the supervisor reads `DOCKER_REGISTRY_*` to pull images. Reuse the same names on deploying machines and CI so secrets live in one place (Infisical / .env) and feed `docker login` reproducibly.

**Instance-side variables** (the compose `.env` on the host; since 4.5.6 there are no shared default credentials):

| Var | Required | Default | Purpose |
|-----|----------|---------|---------|
| `DOCKER_REGISTRY_URL` | Yes | `localhost:5000` | Registry hostname CLIs push to (becomes `DEPLOY_REGISTRY_HOST` in the webapp) |
| `DOCKER_REGISTRY_USERNAME` | Yes | `registry-user` | Basic-auth username |
| `DOCKER_REGISTRY_PASSWORD` | Yes | none, empty in `.env.example` | Basic-auth password. `./generate-secrets.sh` fills it and writes the matching bcrypt entry to `registry/auth.htpasswd` |
| `DOCKER_REGISTRY_NAMESPACE` | Optional | `trigger` | Image namespace; final image path: `{host}/{namespace}/{project-ref}` |

Instances installed before 4.5.6 may still run the old published default password. Replace it, or the upgrade refuses to boot unless `ALLOW_INSECURE_DEFAULT_SECRETS=true` is set as a temporary bypass.

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

Once done, deploys work on this machine until the credentials change.

### Login — non-interactive (CI, reproducible)

Use `--password-stdin` so the password never appears in process lists or shell history:

```bash
echo "$DOCKER_REGISTRY_PASSWORD" | docker login \
  "$DOCKER_REGISTRY_URL" \
  -u "$DOCKER_REGISTRY_USERNAME" \
  --password-stdin
```

Add this as a step **before** `trigger.dev deploy` in any CI pipeline, together with Docker Buildx (`docker/setup-buildx-action`), since self-hosted images are built on the CI runner.

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

### Method 1: CLI (CLI 4.6.1+)

```bash
npx trigger.dev@<version> env set MY_API_KEY "<value>" --env prod
npx trigger.dev@<version> env set MY_SECRET "<value>" --env prod --secret   # cannot be read back
npx trigger.dev@<version> env list --env prod
npx trigger.dev@<version> env pull --env prod                              # to a local file
```

### Method 2: SDK or REST API (recommended for automation)

```ts
import { envvars } from "@trigger.dev/sdk";

await envvars.upload("proj_xxx", "prod", {
  variables: { MY_API_KEY: "<value>", MY_SECRET: "<value>" },
  override: true,
  isSecret: true, // store as redacted secrets
});
```

```bash
# Set a single env var for the prod environment ({env} is dev, staging or prod)
curl -X POST "$TRIGGER_API_URL/api/v1/projects/$TRIGGER_PROJECT_REF/envvars/prod" \
  -H "Authorization: Bearer $TRIGGER_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "MY_API_KEY", "value": "<value>", "isSecret": true}'

# Script to sync all required vars from the current shell environment
for var_name in DIRECTUS_URL API_KEY OTHER_VAR; do
  eval var_value=\$$var_name
  curl -s -X POST "$TRIGGER_API_URL/api/v1/projects/$TRIGGER_PROJECT_REF/envvars/prod" \
    -H "Authorization: Bearer $TRIGGER_SECRET_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$var_name\", \"value\": \"$var_value\"}"
done
```

### Method 3: Dashboard UI

Open the project's **Environment variables** page in the dashboard of your instance and add vars manually.

### Common symptom

If a deployed task fails with `TypeError: Failed to parse URL from undefined/...`, the env var providing the base URL is missing from the runtime environment. Set it with one of the methods above (or sync it at deploy time with the `syncEnvVars` extension).

## Environments

| Environment | Key Format | Convention Var | Purpose |
|-------------|-----------|----------------|---------|
| dev | `tr_dev_xxx` | `TRIGGER_DEV_SECRET_KEY` | Local development |
| staging | `tr_dev_xxx` (different key) | `TRIGGER_STAGE_SECRET_KEY` | Testing before prod |
| production | `tr_prod_xxx` | `TRIGGER_PROD_SECRET_KEY` | Live traffic |
| preview | `tr_dev_xxx` | — | Feature branch testing |

Each environment has its own unique secret key. Staging uses the `tr_dev_` prefix but it is NOT the same key as development. Pass the appropriate per-env key to the SDK via `configure()`.

## CI/CD (GitHub Actions)

For **self-hosted**, add a `docker login` step (and Docker Buildx) before `deploy` — the runner has no Docker credentials by default and the push will fail with "unauthorized". For **cloud** (api.trigger.dev), skip the docker login step.

Pin the CLI: put `trigger.dev` in `devDependencies` at the version of the SDK (on self-hosted, the version of the server) and call it through a script. `deploy` aborts in CI when the CLI and the `@trigger.dev/*` packages differ.

```json
{
  "scripts": {
    "deploy:trigger": "trigger deploy --env prod"
  },
  "devDependencies": {
    "trigger.dev": "<sdk-version>"
  }
}
```

```yaml
name: Deploy Trigger.dev
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: "22"
      - run: npm ci

      # Required for self-hosted only — images are built here and pushed to the instance's built-in registry
      - uses: docker/setup-buildx-action@v3
      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to production
        run: npm run deploy:trigger -- --external-id ${{ github.sha }}  # requires CLI/SDK and server >= 4.5.12; drop it on older
        env:
          # A "Deploy only" environment API key, one per environment (a personal access token also works)
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          # For self-hosted:
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

Without a `package.json` script you can pin on the command line instead: `npx trigger.dev@<version> deploy --env prod`.

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
    "trigger:deploy:prod": "trigger.dev deploy --env prod"
  }
}
```

Keep `trigger.dev` in `devDependencies` at the SDK (server) version so these scripts run the matching CLI.

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
