# Deploy Reference

## Preview Branches

### Deploy to Preview

```bash
npx trigger.dev@latest deploy --env preview --branch feature/new-task
```

### Test Preview

```
1. deploy(environment="preview", branch="feature/new-task")
2. trigger_task(taskId="my-task", payload={...}, environment="preview", branch="feature/new-task")
3. list_runs(environment="preview", branch="feature/new-task")
```

### List Preview Branches

```bash
# Via MCP
list_preview_branches()

# Preview branches are created automatically on first deploy
```

## Monorepo Deploy

Always pass `configPath` for monorepo setups:

```bash
npx trigger.dev@latest deploy --config ./packages/jobs/trigger.config.ts
```

## Deploy without Promoting

Canary/blue-green deployment pattern:

```bash
npx trigger.dev@latest deploy --skip-promotion
```

The new version is deployed but does NOT become the active version. Use this to test before promoting.

## Deploy Filters (MCP)

```
list_deploys(
  environment="prod",
  status="DEPLOYED",
  period="7d",
  limit=10
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `environment` | enum | staging, prod, preview |
| `status` | enum | PENDING, BUILDING, DEPLOYED, FAILED, etc. |
| `period` | string | "1d", "7d", "30d" |
| `limit` | number | Max 100 |

## Standard Deploy Workflow

```
1. npm test                              → local tests
2. deploy --env staging                  → staging deploy
3. trigger_task(env="staging", ...)      → smoke test
4. list_runs(env="staging", period="1h") → verify
5. deploy --env production               → ship it
6. list_deploys(env="prod", limit=1)     → confirm
```
