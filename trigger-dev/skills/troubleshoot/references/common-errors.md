# Common Errors Catalog

## SDK Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find module '@trigger.dev/sdk'` | SDK not installed | `npm install @trigger.dev/sdk` |
| `defineJob is not a function` | Using v2 API | Use `task()` from `@trigger.dev/sdk` (v3 API) |
| `client.defineJob` | Deprecated v2 pattern | Migrate to `task()` / `schemaTask()` |
| `Property 'ok' does not exist` | Missing Result type check | Use `if (result.ok) { result.output }` |

## CLI Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find trigger.config.ts` | Wrong directory | Run from project root or pass `--config` |
| `Error: ENOENT: no such file` | Missing config file | Run `npx trigger.dev@latest init` |
| `Authentication failed` | Invalid credentials | Re-login: `npx trigger.dev@latest login` |
| `Could not find project` | Wrong project ref | Check `project` in trigger.config.ts |
| `Package version mismatch` | SDK/CLI version mismatch | `npx trigger.dev@<version> update` (on self-hosted use the server's version) |
| `The "maxDuration" trigger.config option is now required` | No `maxDuration` in `defineConfig` | Add `maxDuration: 300` (seconds, at least 5) |
| `Interactive prompts cannot be used in non-TTY environments` | `init` run without a TTY | Pass `--yes` with `--project-ref` (or `--project-name` and `--org-name`) |
| `unknown option` on a self-hosted flag (init, login, deploy) | The CLI has no self-hosted switch | Use `-a, --api-url <url>` or `TRIGGER_API_URL` |

## Runtime Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Task "xxx" not found` | Task not exported or not in dirs | Export task; check `dirs` in config |
| `Payload validation failed` | Schema mismatch | Match payload to task's schema definition |
| `AbortTaskRunError` | Task intentionally aborted | Check abort conditions in code |
| `Max duration exceeded` | Task took too long | Increase `maxDuration` (task or config) or optimize |
| `Out of memory` | Task exceeds machine RAM | Use larger machine preset |

## Deployment Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Build failed` | TypeScript/compile errors | Fix errors shown in build output |
| `Push failed: denied` | Registry authentication | `docker login -u <user> <registry-url>` |
| `Error: unauthorized` | Invalid access token | Set TRIGGER_ACCESS_TOKEN for CI/CD |
| `timeout during build` | Large project | Increase Docker resources or split project |
| `graphile_worker schema` | Migration issue | Check webapp logs for SSL/DB errors |

## Self-Hosted Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `connection refused :8030` | Webapp not running | `cd webapp && docker compose up -d` |
| `502 Bad Gateway` | Webapp crashed | `docker compose restart webapp` |
| `Worker not connected` | Missing worker token | Check webapp logs for TRIGGER_WORKER_TOKEN |
| `No containers starting` | Supervisor OOM | Increase Docker memory limits |
| `Registry push: connection refused` | Registry not running | Check registry container status |
| `MinIO: bucket not found` | Missing packets bucket | Create via MinIO UI at :9001 |
| `ClickHouse schema error` | Migration tracker out of sync | Check webapp migration logs; the goose tracker may need `goose reset && goose up` (destructive, non-production only) |
| Webapp refuses to start after upgrade | Old default credentials in `.env` (4.5.6+) | Generate unique secrets, or temporarily `ALLOW_INSECURE_DEFAULT_SECRETS=true` |

## MCP Errors

| Error | Cause | Fix |
|-------|-------|-----|
| MCP tools not found | Server not configured | Run `npx trigger.dev@latest mcp` |
| MCP returns empty | Wrong project/environment | Pass correct projectRef and environment |
| MCP timeout | Instance unreachable | Check network to self-hosted URL |
| MCP accesses prod | No dev-only restriction | Add `--dev-only` to the MCP server args |
| MCP can deploy or trigger | No read-only restriction | Add `--readonly` to the `mcp` server args (not to `install-mcp`) |
| `submit_feedback` missing | Read-only mode, or telemetry disabled | Expected: the tool is hidden in both cases |

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (invalid payload) |
| 401 | Invalid or missing secret key |
| 404 | Resource not found |
| 409 | Conflict (idempotencyKey already used) |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Server error |
