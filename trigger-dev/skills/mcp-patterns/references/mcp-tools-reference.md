# MCP Tools Reference

Complete parameter documentation for all 33 Trigger.dev MCP tools (v4.4.4).

Sections mirror the MCP tool taxonomy: Documentation, Project & Organization, Task Management, Run Monitoring, Deployment, Profile, Query & Analytics, Dev Server, Managed Prompts.

---

## Documentation & Search

### search_docs

Search the Trigger.dev documentation.

```
Input: { "query": "wait for token human in the loop" }
Output: Relevant documentation pages
```

---

## Project & Organization

### list_orgs

```
Input: {}
Output: [{ slug: "my-org", id: "org_xxx" }]
```

### list_projects

```
Input: {}
Output: [{ ref: "proj_xxx", name: "My Project" }]
```

### create_project_in_org

```
Input: { "orgParam": "my-org-slug", "name": "My Background Jobs" }
Output: { ref: "proj_xxx", name: "My Background Jobs" }
```

### initialize_project

```
Input: { "orgParam": "my-org", "projectName": "email-jobs", "cwd": "/path/to/project" }
Output: Creates trigger.config.ts, src/trigger/ directory, installs SDK
```

---

## Task Management

### get_current_worker

Get worker version, SDK version, registered tasks, and machine presets for an environment. **Since v4.4.4 this tool no longer inlines payload schemas** — use `get_task_schema` for the schema of a specific task.

```
Input: { "environment": "dev" }
Output: {
  version: "20260413.1",
  sdkVersion: "4.4.4",
  tasks: [{
    id: "hello-world",
    machine: "small-1x",
    queue: { name: "default", concurrencyLimit: 10 }
  }]
}
```

### get_task_schema

Fetch the payload schema (and any other declared schemas) for a specific registered task.

```
Input: { "taskIdentifier": "hello-world", "environment": "dev" }
Output: {
  payloadSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] }
}
```

Call this before `trigger_task` to validate payloads.

### trigger_task

```
Input: {
  "taskId": "process-order",
  "payload": { "orderId": "ORD-123" },
  "environment": "dev",
  "options": {
    "tags": ["priority"],
    "idempotencyKey": "order-ORD-123",
    "machine": "medium-1x",
    "maxAttempts": 5,
    "maxDuration": 300,
    "delay": "5m",
    "ttl": "30m",
    "queue": { "name": "high-priority" }
  }
}
Output: { id: "run_abc123", status: "QUEUED" }
```

#### Trigger Options

| Option | Type | Description |
|--------|------|-------------|
| delay | string/datetime | "5m", "2h", or ISO datetime |
| tags | string[] | Up to 5, each < 128 chars |
| machine | enum | micro to large-2x |
| maxAttempts | integer | Max retry attempts |
| maxDuration | number | Max seconds |
| ttl | string/integer | Time-to-live; overrides task-level and global defaults |
| idempotencyKey | string | Prevent duplicates |
| queue | object | Override queue name |

---

## Run Monitoring

### list_runs

```
Input: {
  "environment": "prod",
  "status": "FAILED",
  "taskIdentifier": "process-order",
  "tag": "vip-customer",
  "period": "7d",
  "limit": 20
}
```

#### Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| status | enum | QUEUED, EXECUTING, COMPLETED, FAILED, CRASHED, EXPIRED, SYSTEM_FAILURE, TIMED_OUT, PENDING_VERSION |
| taskIdentifier | string | Filter by task ID |
| tag | string | Filter by tag |
| version | string | Filter by worker version |
| machine | enum | Filter by machine preset |
| period | string | "1d", "7d", "30d" |
| from / to | ISO datetime | Custom time range |
| limit | integer | Max 100 |
| cursor | string | Pagination cursor |

### get_run_details

Run trace, logs, and output. Since v4.4.4 the **trace output is paginated** — pass `traceCursor` from a prior response to get the next page. Span IDs are surfaced so you can drill in with `get_span_details`.

```
Input: {
  "runId": "run_abc123",
  "environment": "prod",
  "maxTraceLines": 500,
  "traceCursor": "eyJvZmZzZXQiOjIwMH0="
}
Output: {
  status: "FAILED",
  error: { message: "...", stack: "..." },
  trace: [{ spanId: "span_xyz", name: "openai.chat", startedAt: "...", durationMs: 420 }],
  nextTraceCursor: "eyJvZmZzZXQiOjQwMH0=",
  output: {}
}
```

### get_span_details

Inspect a single span (including child runs and AI enrichment).

```
Input: { "runId": "run_abc123", "spanId": "span_xyz", "environment": "prod" }
Output: {
  attributes: {
    "llm.model": "gpt-4o-mini",
    "llm.usage.input_tokens": 812,
    "llm.usage.output_tokens": 140,
    "trigger.llm.cost_usd": 0.00036
  },
  events: [{ name: "retry", timestamp: "..." }],
  children: [{ runId: "run_child_123" }]
}
```

### wait_for_run_to_complete

```
Input: { "runId": "run_abc123", "timeoutInSeconds": 120 }
Output: { status: "COMPLETED", output: { processed: true } }
```

### cancel_run

Cancels a run. Output is now text-formatted.

```
Input: { "runId": "run_abc123", "environment": "prod" }
Output: "Run run_abc123 cancelled."
```

---

## Deployment

### deploy

```
Input: { "environment": "prod", "skipPromotion": false }
Output: { status: "DEPLOYED", version: "20260413.3" }
```

### list_deploys

Text-formatted. In v4.4.4 this tool stopped crashing on deploys with null `runtime` / `runtimeVersion`.

```
Input: { "environment": "prod", "status": "DEPLOYED", "limit": 5 }
```

### list_preview_branches

Not available in `--dev-only` mode.

```
Input: {}
Output: [{ branch: "feature/new-task", version: "20260413.1", ... }]
```

---

## Profile

### whoami

```
Input: {}
Output: {
  profile: "self-hosted",
  user: { email: "...", userId: "user_xxx" },
  apiUrl: "https://trigger.example.com"
}
```

### list_profiles

```
Input: {}
Output: {
  active: "self-hosted",
  profiles: [
    { name: "default",    apiUrl: "https://api.trigger.dev" },
    { name: "self-hosted", apiUrl: "https://trigger.example.com" }
  ]
}
```

### switch_profile

Changes the active profile for the rest of the MCP session. All subsequent tool calls use the new account and API URL.

```
Input: { "profile": "self-hosted" }
Output: { active: "self-hosted", apiUrl: "https://trigger.example.com" }
```

---

## Query & Analytics

TRQL = SQL-style over ClickHouse. See the **observability** skill for the full language reference. Three tables available: `runs`, `metrics`, `llm_metrics`.

### get_query_schema

Returns the schema for **one** table (the tool now requires a `table` parameter).

```
Input: { "table": "metrics" }
Output: {
  table: "metrics",
  columns: [
    { name: "metric_name",  type: "string",   description: "Metric identifier" },
    { name: "metric_value", type: "number",   description: "Observed value" },
    { name: "bucket_start", type: "datetime", description: "10-second aggregation bucket start time" },
    // ...
  ]
}
```

### query

Execute a TRQL query.

```
Input: {
  "query": "SELECT status, count() AS n FROM runs GROUP BY status ORDER BY n DESC LIMIT 10",
  "scope": "environment",
  "period": "7d",
  "format": "json"
}
Output: (text table by default — ~50% fewer tokens than JSON)
```

| Parameter | Type | Default |
|-----------|------|---------|
| query | string (TRQL) | required |
| scope | `environment` / `project` / `organization` | `environment` |
| period | shorthand (`1h`, `7d`, …) | — |
| from, to | ISO datetime or unix ms | — |
| format | `json` / `csv` | `json` (when called from SDK); MCP returns text tables |

Limits: 10 000 rows per query; per-org concurrency cap; AST complexity and memory limits.

### list_dashboards

```
Input: {}
Output: [{
  dashboardId: "overview",
  name: "Overview",
  widgets: [
    { widgetId: "total-runs",   title: "Total runs" },
    { widgetId: "failure-rate", title: "Failure rate" }
  ]
}]
```

### run_dashboard_query

```
Input: { "dashboardId": "overview", "widgetId": "failure-rate", "period": "30d" }
Output: text table for the widget
```

---

## Dev Server

### start_dev_server

Starts `trigger dev` in the background. Blocks up to 30 s waiting for the worker to come online.

```
Input: { "configPath": "./packages/jobs/trigger.config.ts" }
Output: { status: "ready" | "starting" | "error", pid: 12345 }
```

### stop_dev_server

```
Input: {}
Output: { status: "stopped" }
```

### dev_server_status

```
Input: { "lines": 50 }
Output: {
  status: "ready",
  pid: 12345,
  recentLogs: ["...last 50 log lines..."]
}
```

---

## Managed Prompts

All prompt tools take the shared parameters (`environment`, `projectRef`, `configPath`, `branch`). See the **managed-prompts** skill for the full workflow.

### list_prompts

```
Input: { "environment": "prod" }
Output: [{
  slug: "customer-reply",
  currentVersion: 4,
  overrideActive: false,
  versionCount: 7
}]
```

### get_prompt_versions

```
Input: { "slug": "customer-reply", "environment": "prod" }
Output: [{
  version: 4,
  labels: ["current", "latest"],
  source: "code",
  model: "gpt-4o-mini",
  content: "You are a support agent..."
}, {
  version: 5,
  labels: ["override"],
  source: "dashboard",
  model: "gpt-4o",
  content: "Updated prompt via dashboard..."
}]
```

### promote_prompt_version

Only code-sourced versions can be promoted.

```
Input: { "slug": "customer-reply", "version": 4, "environment": "prod" }
Output: { slug: "customer-reply", currentVersion: 4 }
```

### create_prompt_override

Creates a dashboard-sourced override. Override takes precedence over the current code version.

```
Input: {
  "slug": "customer-reply",
  "textContent": "You are a support agent. Be concise...",
  "model": "gpt-4o",
  "commitMessage": "Hotfix tone for incident 2026-04-24",
  "environment": "prod"
}
Output: { slug: "customer-reply", overrideVersion: 5, source: "dashboard" }
```

### update_prompt_override

Updates the currently active override. Fails if no override is active.

```
Input: {
  "slug": "customer-reply",
  "textContent": "Revised copy v2",
  "commitMessage": "Follow-up tweak"
}
Output: { slug: "customer-reply", overrideVersion: 6 }
```

### remove_prompt_override

Removes the active override — reverts to the current code version.

```
Input: { "slug": "customer-reply", "environment": "prod" }
Output: { slug: "customer-reply", overrideActive: false }
```

### reactivate_prompt_override

Use `get_prompt_versions` to find a dashboard-sourced version to reactivate.

```
Input: { "slug": "customer-reply", "version": 5, "environment": "prod" }
Output: { slug: "customer-reply", overrideVersion: 5 }
```

---

## TRQL at a Glance

(See the **observability** skill and `skills/observability/references/trql-reference.md` for depth.)

- **Tables**: `runs`, `metrics`, `llm_metrics`
- **Time bucket**: `SELECT timeBucket(), count() FROM runs GROUP BY timeBucket()` — auto-bucketed by the caller's time range
- **Scopes**: `environment` (default), `project`, `organization`
- **Period shorthand**: `1h`, `6h`, `12h`, `1d`, `7d`, `30d`, `90d`
- **Pretty formatters**: `prettyFormat(col, 'bytes' | 'percent' | 'duration' | 'durationSeconds' | 'quantity' | 'costInDollars')`
- Prefer the built-in time filter (dashboard / API / SDK) over embedding `triggered_at` in the TRQL itself.

---

## REST Management API

### Trigger a Task

```bash
POST /api/v1/tasks/{taskId}/trigger

curl -X POST "${TRIGGER_API_URL}/api/v1/tasks/process-order/trigger" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"orderId": "ORD-123"}, "options": {"tags": ["priority"]}}'
```

### Batch Trigger

```bash
POST /api/v1/tasks/{taskId}/batch
```

### Get Run Status

```bash
GET /api/v1/runs/{runId}
```

### Get Span Details (new in v4.4.4)

```bash
GET /api/v1/runs/{runId}/spans/{spanId}

curl -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  "${TRIGGER_API_URL}/api/v1/runs/run_abc123/spans/span_xyz"
```

### Execute a TRQL Query

```bash
POST /api/v1/query

curl -X POST "${TRIGGER_API_URL}/api/v1/query" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT run_id, status FROM runs LIMIT 10",
    "scope": "environment",
    "period": "7d",
    "format": "json"
  }'
```

Requires the `read:query` JWT scope (new in v4.4.4).

### List Runs

```bash
GET /api/v1/runs?status=FAILED&limit=10&period=24h
```

### Cancel Run

```bash
POST /api/v1/runs/{runId}/cancel
```

### Complete Wait Token

```bash
POST /api/v1/waitpoints/tokens/{tokenId}/complete

curl -X POST "${TRIGGER_API_URL}/api/v1/waitpoints/tokens/${TOKEN_ID}/complete" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"approved": true}}'
```

### Set Environment Variables

```bash
POST /api/v1/projects/{projectRef}/envvars/{environment}

curl -X POST "${TRIGGER_API_URL}/api/v1/projects/proj_xxx/envvars/production" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"DATABASE_URL": "postgres://...", "API_KEY": "sk-..."}}'
```

### Create Schedule

```bash
POST /api/v1/schedules

curl -X POST "${TRIGGER_API_URL}/api/v1/schedules" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"task": "daily-report", "cron": "0 9 * * *", "externalId": "report-daily"}'
```

### Promote Deployment (with allowRollbacks)

```bash
POST /api/v1/deployments/{deploymentId}/promote?allowRollbacks=true
```

`allowRollbacks=true` (new in v4.4.4) lets the promote endpoint downgrade to an older version.

### SDK Management API

```ts
import { configure, runs, query } from "@trigger.dev/sdk";

configure({ secretKey: process.env.TRIGGER_SECRET_KEY });

const result = await runs.list({ limit: 10, status: ["COMPLETED"] });
const run = await runs.retrieve(runId);
await runs.cancel(runId);

// TRQL from SDK
const failed = await query.execute(
  "SELECT count() AS n FROM runs WHERE status = 'Failed'",
  { period: "24h" }
);
```
