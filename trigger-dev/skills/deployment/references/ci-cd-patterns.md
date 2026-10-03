# CI/CD Patterns

**Pin the CLI.** `deploy` aborts in CI when the `trigger.dev` CLI and the `@trigger.dev/*` packages are on different versions. Do not use `@latest` in a workflow: add `trigger.dev` to `devDependencies` at the SDK version (on self-hosted, at the server version) and call it through a `package.json` script, or write `npx trigger.dev@<version>` explicitly. The examples below use the script form:

```json
{
  "scripts": {
    "deploy:trigger": "trigger deploy",
    "deploy:trigger:staging": "trigger deploy --env staging"
  },
  "devDependencies": { "trigger.dev": "<sdk-version>" }
}
```

**Authenticate with a Deploy-only API key.** Create one environment API key per environment you deploy to (Dashboard, API keys, "Deploy only" access) and pass it as `TRIGGER_ACCESS_TOKEN`; a personal access token also works but is tied to a person and not recommended for CI. Deploy-only keys are documented for Cloud; check them on your self-hosted version.

**Tag the deploy.** `--external-id ${{ github.sha }}` (max 128 characters) makes re-runs idempotent and enables version skew protection. **Requires server ≥ 4.5.12 (CLI/SDK must match)**: an older CLI rejects the flag, so drop it on a 4.4.4 server. Give the application the same value as `TRIGGER_EXTERNAL_DEPLOYMENT_ID`.

## GitHub Actions — Cloud

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
      - name: Deploy to production
        run: npm run deploy:trigger -- --external-id ${{ github.sha }}  # requires CLI/SDK and server >= 4.5.12; drop it on older
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
```

## GitHub Actions — Self-Hosted

Self-hosted deploys push built images to the instance's built-in container registry. The runner must `docker login` to the registry before `trigger.dev deploy` — otherwise the push fails with `unauthorized: authentication required`.

```yaml
name: Deploy Trigger.dev (Self-Hosted)
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

      # Self-hosted images are built on the runner
      - uses: docker/setup-buildx-action@v3

      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to production
        run: npm run deploy:trigger -- --external-id ${{ github.sha }}  # requires CLI/SDK and server >= 4.5.12; drop it on older
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

## GitHub Actions — Staging + Production

Both staging and production push to the same registry, so the docker login step runs once and benefits both deploy jobs below.

```yaml
name: Deploy Trigger.dev
on:
  push:
    branches:
      - main
      - develop

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: "22"
      - run: npm ci

      # Self-hosted only (skip if deploying to cloud): Buildx and registry login
      - uses: docker/setup-buildx-action@v3
      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: npm run deploy:trigger:staging -- --external-id ${{ github.sha }}  # requires CLI/SDK and server >= 4.5.12; drop it on older
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: npm run deploy:trigger -- --external-id ${{ github.sha }}  # requires CLI/SDK and server >= 4.5.12; drop it on older
        env:
          # A key for the production environment; staging uses its own secret
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

Use a separate secret per environment (for example `TRIGGER_STAGING_ACCESS_TOKEN` for the staging step), because a Deploy-only key belongs to one environment.

## GitLab CI

```yaml
deploy-trigger:
  stage: deploy
  image: node:22
  script:
    - npm ci
    - npm run deploy:trigger -- --external-id "$CI_COMMIT_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
  variables:
    TRIGGER_ACCESS_TOKEN: $TRIGGER_ACCESS_TOKEN
    TRIGGER_API_URL: $TRIGGER_API_URL
  only:
    - main
```

## Generic CI

For any CI system, set these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TRIGGER_ACCESS_TOKEN` | Yes | A "Deploy only" environment API key (one per environment). A personal access token (tr_pat_xxx) also works but is not recommended for CI; `TRIGGER_SECRET_KEY` as a fallback is an undocumented workaround |
| `TRIGGER_API_URL` | Self-hosted only | Your instance URL |
| `DOCKER_REGISTRY_URL` | Self-hosted only | Registry hostname (e.g. `registry.your-domain.com`) |
| `DOCKER_REGISTRY_USERNAME` | Self-hosted only | Registry basic-auth username |
| `DOCKER_REGISTRY_PASSWORD` | Self-hosted only | Registry basic-auth password |

For self-hosted, add a docker login step before deploy:

```bash
# Self-hosted only — authenticate to the built-in registry
echo "$DOCKER_REGISTRY_PASSWORD" | docker login "$DOCKER_REGISTRY_URL" -u "$DOCKER_REGISTRY_USERNAME" --password-stdin

# Deploy with the pinned CLI (npm script that runs `trigger deploy --env prod`)
npm run deploy:trigger -- --external-id "$CI_COMMIT_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
```

For cloud, just run the same script (no docker login):

```bash
npx trigger.dev@<sdk-version> deploy --env prod --external-id "$CI_COMMIT_SHA"  # requires CLI/SDK and server >= 4.5.12; drop it on older
```
