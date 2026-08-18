# CI/CD Patterns

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
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - name: Deploy to production
        run: npx trigger.dev@latest deploy --env production
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
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci

      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to production
        run: npx trigger.dev@latest deploy --env production
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
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci

      # Self-hosted registry login (skip if deploying to cloud)
      - name: Login to Trigger.dev container registry
        run: echo "${{ secrets.DOCKER_REGISTRY_PASSWORD }}" | docker login "${{ secrets.DOCKER_REGISTRY_URL }}" -u "${{ secrets.DOCKER_REGISTRY_USERNAME }}" --password-stdin

      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: npx trigger.dev@latest deploy --env staging
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: npx trigger.dev@latest deploy --env production
        env:
          TRIGGER_ACCESS_TOKEN: ${{ secrets.TRIGGER_ACCESS_TOKEN }}
          TRIGGER_API_URL: ${{ secrets.TRIGGER_API_URL }}
```

## GitLab CI

```yaml
deploy-trigger:
  stage: deploy
  image: node:20
  script:
    - npm ci
    - npx trigger.dev@latest deploy --env production
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
| `TRIGGER_ACCESS_TOKEN` | Yes | Personal access token (tr_pat_xxx) or fall back to `TRIGGER_SECRET_KEY` |
| `TRIGGER_API_URL` | Self-hosted only | Your instance URL |
| `DOCKER_REGISTRY_URL` | Self-hosted only | Registry hostname (e.g. `registry.your-domain.com`) |
| `DOCKER_REGISTRY_USERNAME` | Self-hosted only | Registry basic-auth username |
| `DOCKER_REGISTRY_PASSWORD` | Self-hosted only | Registry basic-auth password |

For self-hosted, add a docker login step before deploy:

```bash
# Self-hosted only — authenticate to the built-in registry
echo "$DOCKER_REGISTRY_PASSWORD" | docker login "$DOCKER_REGISTRY_URL" -u "$DOCKER_REGISTRY_USERNAME" --password-stdin

# Deploy
npx trigger.dev@latest deploy --env production
```

For cloud, just run:

```bash
npx trigger.dev@latest deploy --env production
```
