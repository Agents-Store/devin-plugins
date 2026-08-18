---
name: troubleshoot
description: Diagnose and fix Trigger.dev errors, failed runs, deployment issues, and self-hosted problems. Use when the user encounters "trigger.dev not working", "task keeps failing", "deploy failed", "runs stuck", "self-hosted issues", "trigger.dev connection error", or needs to debug Trigger.dev v4.
---

# Troubleshooting

Diagnostic steps and fixes for common Trigger.dev v4 problems.

## Quick Diagnostics

Run these checks first:

1. **CLI auth**: `npx trigger.dev@latest whoami`
2. **Dev server**: `npx trigger.dev@latest dev` — starts without errors?
3. **If MCP**: `list_orgs()` — returns organizations?
4. **Recent failures**: `list_runs(status="FAILED", period="1d")`

## Task Errors

| Status | Cause | Fix |
|--------|-------|-----|
| FAILED | Task threw an error | Check run details → read error trace |
| CRASHED | OOM or unexpected crash | Increase machine preset or fix memory leak |
| SYSTEM_FAILURE | Infrastructure issue | Check supervisor container health |
| TIMED_OUT | Exceeded maxDuration | Increase `maxDuration` or optimize task |
| EXPIRED | TTL expired before execution | Raise `ttl` on the trigger / task / global default, or drain the queue. See **config-and-build** and **task-development** for TTL precedence. |
| PENDING_VERSION | No matching worker deployed | Deploy to the correct environment |

## Connection Errors

| Error | Cause | Fix |
|-------|-------|-----|
| ECONNREFUSED | Instance not running | Start: `docker compose up -d` |
| ETIMEDOUT | Network/firewall | Check DNS, firewall, proxy config |
| ENOTFOUND | Wrong URL | Verify TRIGGER_API_URL |
| SSL_ERROR | Invalid certificate | Check reverse proxy SSL config |
| Redirected to cloud | Missing API URL | Use `login -a <url>` or set TRIGGER_API_URL |

## Authentication Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid secret key | Check format: tr_dev_xxx (dev), tr_prod_xxx (prod) |
| 403 Forbidden | Wrong environment key | Use dev key for dev, prod key for prod |
| Token expired | Key rotated | Generate new key in dashboard |
| CI auth fails | Missing access token | Set TRIGGER_ACCESS_TOKEN (tr_pat_xxx) |

## Deployment Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Build failed | TypeScript errors | Fix compile errors in your task code |
| `denied: requested access to the resource is denied` | Not logged into self-hosted registry | `docker login -u $DOCKER_REGISTRY_USERNAME $DOCKER_REGISTRY_URL` (see Registry Push Failures below) |
| `unauthorized: authentication required` | Registry credentials wrong or expired | `docker logout $URL` + fresh login with current password |
| `no basic auth credentials` | Docker credentials store empty for this host | Run `docker login` on the machine; in CI, add login step before deploy |
| Push to `localhost:5000` fails on CI | `DEPLOY_REGISTRY_HOST` on server still set to default | Set public hostname in webapp `.env` + restart webapp |
| "No tasks found" | Wrong `dirs` config | Check `dirs` in trigger.config.ts |
| Version mismatch | SDK/CLI out of sync | `npm install @trigger.dev/sdk@latest` |

### Registry Push Failures (Self-Hosted)

When `trigger.dev deploy` fails at the push step, the developer/CI machine can't authenticate with the instance's built-in registry:

```bash
# Interactive (dev laptop)
docker login -u registry-user registry.your-domain.com

# Non-interactive (CI)
echo "$DOCKER_REGISTRY_PASSWORD" | docker login \
  "$DOCKER_REGISTRY_URL" \
  -u "$DOCKER_REGISTRY_USERNAME" \
  --password-stdin

# Verify creds are valid
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -u "$DOCKER_REGISTRY_USERNAME:$DOCKER_REGISTRY_PASSWORD" \
  "https://$DOCKER_REGISTRY_URL/v2/"
# → HTTP 200 means login will succeed
# → HTTP 401 means wrong username/password
```

Common root causes:
- **CI runner has no persisted Docker credentials** → add `docker login` step before deploy
- **Registry password rotated on server** but local docker keychain still has old password → `docker logout` + re-login
- **Using `localhost:5000` publicly** → change `DEPLOY_REGISTRY_HOST` to public hostname in webapp `.env`, restart webapp, re-login clients

## Dev Server Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Cannot find trigger.config.ts | Wrong directory | Run from project root or pass `--config` |
| Tasks not registering | File not in `dirs` | Check trigger.config.ts `dirs` |
| Hot reload not working | File watcher issue | Restart dev server |

## Self-Hosted v4 Diagnostics

### Check Instance Health

```bash
# Webapp
cd trigger.dev/hosting/docker/webapp
docker compose ps
docker compose logs -f webapp

# Supervisor
cd trigger.dev/hosting/docker/worker
docker compose ps
docker compose logs -f supervisor
```

### Common Self-Hosted Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| All runs CRASHED | Supervisor OOM | Increase Docker memory limits |
| Runs stuck QUEUED | Supervisor disconnected | Check worker token; restart supervisor |
| Dashboard 502 | Webapp crashed | `docker compose restart webapp` |
| Worker token missing | Separate machines | Check webapp logs for token on first start |
| Registry auth fails | Wrong credentials or stale docker keychain | See "Registry Push Failures" above — verify via `curl -u user:pass https://$URL/v2/` returns 200 |
| Object storage error | MinIO bucket missing | Create `packets` bucket via MinIO UI (:9001) |
| Disk full | Old runs not cleaned | Configure retention, clean old data |

### Log Analysis

```bash
# Find errors in webapp
docker compose logs webapp 2>&1 | grep -i error | tail -20

# Check for OOM kills
docker compose logs supervisor 2>&1 | grep -i "oom\|killed" | tail -10

# Check registry
curl -s http://localhost:5000/v2/

# Check MinIO
curl -s http://localhost:9000/minio/health/live
```

## Query & Dashboards (TRQL)

| Symptom | Cause | Fix |
|---------|-------|-----|
| "AST too complex" | Query too large / nested joins | Split the query, simplify aggregates |
| "Row limit exceeded" | > 10 000 rows | Add `LIMIT` + a time filter via `period` |
| "Concurrent queries exceeded" | Dashboard or batch query spam | Reduce widget refresh rate; stagger batch queries |
| `get_query_schema` error "table required" | v4.4.4 now requires a table arg | Pass `table: "runs"`, `"metrics"`, or `"llm_metrics"` |
| Column `value` not found on `metrics` | v4.4.4 renamed/clarified column | Use `metric_value` |

See the **observability** skill for the full TRQL syntax reference.

## MCP Tool Annotations (v4.4.4+)

Every MCP tool now carries `readOnlyHint` / `destructiveHint` annotations. If your MCP client respects them, agents can be prevented from calling write tools without explicit approval. For a hard-enforced read-only deployment, install with `npx trigger.dev@latest install-mcp --readonly` — `deploy`, `trigger_task`, and `cancel_run` are hidden server-side.

## Deeper Reference

- @references/common-errors.md — extended error catalog
