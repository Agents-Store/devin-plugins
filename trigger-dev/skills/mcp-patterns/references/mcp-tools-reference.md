# MCP Tools Reference

Complete parameter documentation for all 41 Trigger.dev MCP tools (CLI 4.7.2; checked against the live server and the `trigger.dev` package).

Sections: Documentation & Search, Feedback, Project & Organization, Task Management, Run Monitoring, Deployment, Profile, Query & Analytics, Reports, Dev Server, Managed Prompts, Agent Chat, Session Channels (13 categories). The tools were added over time: 14 original tools, 11 in v4.4.4 (profile, query/dashboards, dev server, span details, task schema), 7 prompt tools, then agent chat, session channels, reports and feedback in 4.5-4.7. The tool list is whatever the **CLI version running the MCP server** exposes, not what the Trigger.dev server supports.

All tools return **text** (markdown-ish), not JSON objects. The `Output:` notes below describe what the text contains.

## Shared Parameters

Every tool that works on a project environment accepts these optional parameters. They are not repeated below.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `projectRef` | string | auto | `proj_xxx`. Detected from `trigger.config.ts` in the working directory or from the server's `--project-ref` flag |
| `configPath` | string | auto | Path to `trigger.config.ts` (monorepos) |
| `environment` | `dev` / `staging` / `prod` / `preview` | `dev` | `deploy` and `list_deploys` default to `prod` and do not accept `dev` |
| `branch` | string | — | Preview branch (or branchable dev environment) |

Tools without these parameters: `search_docs`, `submit_feedback`, `list_orgs`, `list_projects`, `create_project_in_org`, `initialize_project`, `list_profiles`, `switch_profile`, `whoami`, `start_dev_server` (takes only `configPath`), `stop_dev_server`, `dev_server_status`, `send_agent_message`, `close_agent_chat`, `list_preview_branches` (takes only `projectRef` and `configPath`).

**`--readonly`** (a flag of `trigger.dev mcp`, not of `install-mcp`) removes 15 tools: `deploy`, `trigger_task`, `cancel_run`, `create_project_in_org`, `initialize_project`, `promote_prompt_version`, `create_prompt_override`, `update_prompt_override`, `remove_prompt_override`, `reactivate_prompt_override`, `start_agent_chat`, `send_agent_message`, `close_agent_chat`, `write_session_channel`, `submit_feedback`. **`--dev-only`** keeps all tools but rejects any non-dev `environment`, plus `deploy`, `list_deploys` and `list_preview_branches`.

---

## Documentation & Search

### search_docs

Search the Trigger.dev documentation.

```
Input: { "query": "wait for token human in the loop" }
Output: matching documentation pages with titles, excerpts and links
```

---

## Feedback

### submit_feedback

Report a problem with the MCP server, SDK or docs to the Trigger.dev team. Use it when a tool returned a confusing error, the docs disagreed with the behavior, a needed capability was missing, or a workaround was required. **Write tool**: hidden by `--readonly`, and also hidden when telemetry is off (`--skip-telemetry` or the `TRIGGER_TELEMETRY_DISABLED` environment variable), because the report leaves the machine.

```
Input: {
  "message": "What I tried, what happened, what I expected (1-4000 chars)",
  "toolName": "get_run_details",
  "projectRef": "proj_xxx"
}
```

Never put secrets, credentials, environment variables or the user's own data in `message`; summarise and redact. Tell the user what was reported, and do not send the same report twice.

---

## Project & Organization

### list_orgs

```
Input: {}
Output: the user's organizations (slug and id)
```

### list_projects

```
Input: {}
Output: projects grouped by organization: name, projectRef (proj_xxx), slug, createdAt
```

### create_project_in_org

**Write tool.** Only for adding Trigger.dev to a codebase that has no `trigger.config.ts` yet.

```
Input: { "orgParam": "my-org-slug", "name": "My Background Jobs" }
```

### initialize_project

**Write tool.** Creates a project in the organization (unless `projectRef` is passed or `trigger.config.ts` already exists in `cwd`, in which case it skips with a message), then returns the manual-setup guide with `TRIGGER_PROJECT_REF`, `TRIGGER_SECRET_KEY` (the project's dev key) and `TRIGGER_API_URL` filled in. It **does not write files or install packages**: the agent follows the returned guide. Treat the output as secret, it contains a dev key.

```
Input: { "orgParam": "my-org", "projectName": "email-jobs", "cwd": "/path/to/project", "projectRef": "proj_xxx" }
```

`projectRef` is optional.

---

## Task Management

### get_current_worker

The current worker of an environment: worker version, SDK version, and the registered task slugs. Output is text: a header line (`Current worker for dev is <version> using <sdk> of the SDK`), one line per task (`- <slug> [agent] in <file path>`; `[agent]` marks `chat.agent` tasks), the runs URL, and a warning when the SDK version differs from the CLI version. It does **not** include payload schemas, machine presets or queue settings; use `get_task_schema` for the payload.

```
Input: { "environment": "dev" }
```

### get_task_schema

Payload schema of one registered task.

```
Input: { "taskSlug": "hello-world", "environment": "dev" }
```

The parameter is `taskSlug` (not `taskIdentifier`). Call it before `trigger_task` to build a valid payload.

### trigger_task

**Write tool.**

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
    "queue": { "name": "high-priority" },
    "region": "us-east-1"
  }
}
Output: "Task process-order triggered and run with ID created: run_xxx", the dashboard URL, and a note when the dev CLI is not connected
```

`payload` is the payload object itself, not a JSON string (a JSON string is parsed as a convenience). The tool description mentions `get_tasks`; that tool does not exist, use `get_current_worker`.

#### Trigger Options

| Option | Type | Description |
|--------|------|-------------|
| `delay` | string / ISO datetime | `"5m"`, `"2h"`, or an ISO 8601 datetime (UTC, `Z`) |
| `tags` | string[] | Up to 5, each < 128 chars |
| `machine` | enum | `micro`, `small-1x`, `small-2x`, `medium-1x`, `medium-2x`, `large-1x`, `large-2x` |
| `maxAttempts` | integer | Max retry attempts |
| `maxDuration` | number | Max seconds |
| `ttl` | string / integer | Time-to-live; default `"10m"`; overrides task-level and global defaults |
| `idempotencyKey` | string | Prevent duplicates |
| `queue` | `{ name }` | Override queue name |
| `region` | string | Region to run in, overriding the project default. Regions are listed on the dashboard Regions page. No effect in `dev` |

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
| `status` | enum | `PENDING_VERSION`, `QUEUED`, `DEQUEUED`, `EXECUTING`, `WAITING`, `COMPLETED`, `CANCELED`, `FAILED`, `CRASHED`, `SYSTEM_FAILURE`, `DELAYED`, `EXPIRED`, `TIMED_OUT` |
| `taskIdentifier` | string | Filter by task ID |
| `tag` | string | Filter by tag |
| `version` | string | Worker version, for example `20250808.3` |
| `machine` | enum | Machine preset |
| `region` | string | Region (worker instance group) the run executed in, for example `us-east-1` or `main` |
| `period` | string | `"1d"`, `"7d"`, `"30d"`, `"365d"` |
| `from` / `to` | ISO 8601 | Created after / before |
| `limit` | integer | Page size, max 100 |
| `cursor` | string | Pagination cursor, starts with `run_` |

### get_run_details

Run details plus the trace, paginated. The first call returns the run and the first page of trace lines (`maxTraceLines`, default 200); when more exist the text ends with an instruction to call again with a `cursor`. Span IDs appear as `[spanId]` before each span message. Completed runs are cached for ten minutes, so paging does not re-fetch the trace.

```
Input: { "runId": "run_abc123", "environment": "prod", "maxTraceLines": 500 }
Next page: { "runId": "run_abc123", "environment": "prod", "cursor": "<cursor from the previous response>" }
```

The parameter is `cursor`; treat the value as opaque and pass it back exactly as the response gives it.

### get_span_details

One span: timing, attributes, error info, and for AI spans model, tokens, cost and response data. Get span IDs from `get_run_details`.

```
Input: { "runId": "run_abc123", "spanId": "<span id>", "environment": "prod" }
```

### wait_for_run_to_complete

```
Input: { "runId": "run_abc123", "timeoutInSeconds": 120 }
Output: the run's final state, or its current state when the timeout (default 60 s) expires first
```

### cancel_run

**Write tool.**

```
Input: { "runId": "run_abc123", "environment": "prod" }
```

---

## Deployment

### deploy

**Write tool.** Runs the CLI `deploy` in the working project. The CLI version it uses is the project's installed `trigger.dev`, else `trigger.dev@<installed SDK version>`, else the version of the MCP server itself, so keep the SDK pinned to the server version. Rejected by `--dev-only`.

```
Input: {
  "environment": "prod",
  "skipPromotion": false,
  "skipSyncEnvVars": false,
  "skipUpdateCheck": false
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `environment` | `staging` / `prod` / `preview` | Default `prod` |
| `skipPromotion` | boolean | Deploy without making it current |
| `skipSyncEnvVars` | boolean | Skip the `syncEnvVars` extension |
| `skipUpdateCheck` | boolean | Skip the `@trigger.dev/*` package update check |
| `branch` | string | Preview branch |

Output: the CLI's deploy log (ANSI stripped). On failure the log is returned as the error.

### list_deploys

Text list: `- <shortCode> | v<version> | <status> | <deployedAt> | <commit message>`, plus `Next page available`. Rejected by `--dev-only`.

```
Input: { "environment": "prod", "status": "DEPLOYED", "limit": 5 }
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `environment` | `staging` / `prod` / `preview` | Default `prod` |
| `status` | enum | `PENDING`, `BUILDING`, `DEPLOYING`, `DEPLOYED`, `FAILED`, `CANCELED`, `TIMED_OUT` |
| `limit` | number | 1-100, default 20 |
| `period` | string | For example `1d`, `7d`, `3h` |
| `from` / `to` | ISO 8601 | Date range |
| `cursor` | string | Deployment ID to continue from |

### list_preview_branches

Not available in `--dev-only` mode.

```
Input: {}
Output: preview branch names, with a paused marker
```

---

## Profile

### whoami

```
Input: {}
Output: active profile, user, email and API URL
```

### list_profiles

```
Input: {}
Output: every CLI profile with its API URL; the active one is marked
```

### switch_profile

Changes the active profile for the rest of the MCP session. All subsequent tool calls use the new account and API URL. If authentication with the new profile fails the previous profile is restored.

```
Input: { "profile": "self-hosted" }
```

---

## Query & Analytics

TRQL = SQL-style over ClickHouse. See the **observability** skill for the full language reference. Three tables: `runs`, `metrics`, `llm_metrics`.

### get_query_schema

Columns, types, descriptions and allowed values of **one** table.

```
Input: { "table": "metrics" }
```

### query

Execute a TRQL query. Results come back as a text table.

```
Input: {
  "query": "SELECT status, count() AS n FROM runs GROUP BY status ORDER BY n DESC LIMIT 10",
  "scope": "environment",
  "period": "7d"
}
```

| Parameter | Type | Default |
|-----------|------|---------|
| `query` | string (TRQL) | required |
| `scope` | `environment` / `project` / `organization` | `environment` |
| `period` | shorthand (`1h`, `7d`, `30d`) | — (mutually exclusive with `from`/`to`) |
| `from`, `to` | ISO 8601 only, given as a pair | — |

The MCP tool has no `format` parameter; `format` (`json` / `csv`) belongs to the SDK and REST API. Limits: 10 000 rows per query; per-org concurrency cap; AST complexity and memory limits.

### list_dashboards

```
Input: {}
Output: per dashboard: title and key (`overview` = run metrics, `llm` = AI metrics) with a table of widgets (Widget ID, Title, Type); widget IDs are either opaque ids or slugs such as `llm-cost`
```

### run_dashboard_query

Execute a single widget of a built-in dashboard.

```
Input: { "dashboardKey": "llm", "widgetId": "llm-cost", "period": "30d" }
Output: the widget's data as a text table
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dashboardKey` | string | Dashboard key from `list_dashboards` (not an ID) |
| `widgetId` | string | Widget ID from `list_dashboards` |
| `period` | string | Default `1d` |
| `from`, `to` | ISO 8601 | Pair; alternative to `period` |
| `scope` | `environment` / `project` / `organization` | Default `environment` |

---

## Reports

### get_report

An interpreted report rendered as text with sparklines; the server computes the verdict. Currently one report: `health` — is work flowing, are the runs that start healthy, is the telemetry fresh, with a headline verdict and a suggested next action. The CLI equivalent is `trigger report health`. Hosts that render MCP prompts also get a `report` prompt (in Claude Code it appears as a slash command named after the server).

```
Input: { "key": "health", "environment": "prod", "period": "24h" }
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `health` | Required |
| `period` | string | `1h` (default), `24h`, `7d`; minutes to weeks (`m`, `h`, `d`, `w`), at most 90d; no seconds |
| `color` | boolean | ANSI-coloured output instead of markdown |

Show the returned report to the user as-is (it is monospace-aligned), then add at most a sentence of your own.

---

## Dev Server

### start_dev_server

Starts `trigger dev` in the background and waits up to 30 s for the worker to be ready.

```
Input: { "configPath": "./packages/jobs/trigger.config.ts" }
Output: "Dev server is ready." with recent log lines; or a build-error / still-starting message with the log
```

`configPath` is the config file or the project directory. Not hidden by `--readonly`.

### stop_dev_server

```
Input: {}
Output: "Dev server stopped."
```

### dev_server_status

```
Input: { "lines": 50 }
Output: "Dev Server Status: <stopped | starting | ready | error>", the directory, and the last `lines` log lines
```

---

## Managed Prompts

All prompt tools take the shared parameters. See the **managed-prompts** skill for the full workflow. The five writers are hidden by `--readonly`.

### list_prompts

```
Input: { "environment": "prod" }
Output: slug, current version, override status, version count per prompt
```

### get_prompt_versions

```
Input: { "slug": "customer-reply", "environment": "prod" }
Output: per version: number, labels (current / override / latest), source (code / dashboard), model, content
```

### promote_prompt_version

Only code-sourced versions can be promoted.

```
Input: { "slug": "customer-reply", "version": 4, "environment": "prod" }
```

### create_prompt_override

Creates a dashboard-sourced override. The override takes precedence over the current code version.

```
Input: {
  "slug": "customer-reply",
  "textContent": "You are a support agent. Be concise...",
  "model": "<model id>",
  "commitMessage": "Hotfix tone for incident OPS-1234",
  "environment": "prod"
}
```

`model` and `commitMessage` are optional.

### update_prompt_override

Updates the currently active override. Fails if no override is active.

```
Input: {
  "slug": "customer-reply",
  "textContent": "Revised copy v2",
  "commitMessage": "Follow-up tweak"
}
```

### remove_prompt_override

Removes the active override and reverts to the current code version.

```
Input: { "slug": "customer-reply", "environment": "prod" }
```

### reactivate_prompt_override

Use `get_prompt_versions` to find a dashboard-sourced version to reactivate.

```
Input: { "slug": "customer-reply", "version": 5, "environment": "prod" }
```

---

## Agent Chat

Tools for talking to `chat.agent()` / `chat.customAgent()` tasks from an MCP client. **Requires server ≥ 4.5.0** (Sessions); the agents themselves are described in the **ai-chat-agents** skill. Chats started here live in the MCP server process: restarting the MCP server forgets them. `start_agent_chat`, `send_agent_message` and `close_agent_chat` act on real sessions and runs and are hidden by `--readonly`; `list_agents` is read-only.

### list_agents

```
Input: { "environment": "dev" }
Output: agent slugs with their file path
```

### start_agent_chat

**Write tool.** Creates a `chat.agent` session and its first run.

```
Input: {
  "agentId": "support-chat",
  "chatId": "conversation-123",
  "clientData": { "userId": "user_123" },
  "preload": true,
  "environment": "dev"
}
Output: chat ID, session ID, agent, run ID
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `agentId` | string | Agent task slug (see `list_agents`) |
| `chatId` | string | Unique conversation ID; reuse it to resume. Generated when omitted |
| `clientData` | object | Sent with every message (for example `userId`, `model`) |
| `preload` | boolean | Default `true`; a session always starts with a live run |

### send_agent_message

**Write tool.** Sends a message and returns the agent's full response text, followed by the run ID. The agent remembers earlier messages of the same chat.

```
Input: { "chatId": "conversation-123", "message": "Where is my order?" }
```

### close_agent_chat

**Write tool.** The agent exits its loop gracefully; without it the agent closes when its idle timeout expires.

```
Input: { "chatId": "conversation-123" }
```

---

## Session Channels

Low-level access to the realtime streams of a session. **Requires server ≥ 4.5.0.**

### read_session_channel

Read records from a named side channel, or from the reserved chat transcript pair when `channel` is omitted. By default it drains what exists after the cursor and returns; `timeoutInSeconds` makes it wait for the next record.

```
Input: { "sessionId": "session_xxx", "channel": "screencast", "io": "out", "maxRecords": 100 }
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `sessionId` | string | `session_*` friendly ID, or the externalId it was created with |
| `channel` | string | 1-128 chars from `[A-Za-z0-9._-]`; omit for the chat transcript |
| `io` | `out` / `in` | `out` = producer feed (default), `in` = what clients sent |
| `afterEventId` | string | Cursor: pass the `nextCursor` of the previous read |
| `maxRecords` | integer | Default 100, max 500 |
| `timeoutInSeconds` | integer | Wait up to this long (max 60) when nothing is available |

### write_session_channel

**Write tool.** Appends one record to a named channel's `in` stream, to send control input to a running agent (for example a pause or viewport command) without waking or triggering a run. `channel` is required; the transcript and the `out` side are not writable.

```
Input: { "sessionId": "session_xxx", "channel": "control", "value": { "paused": true } }
```

`value` is an object (structured record) or a string (raw record).

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

Authenticate with the secret key of the environment (`Authorization: Bearer ${TRIGGER_SECRET_KEY}`), or with a personal access token where the docs allow it.

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
  "${TRIGGER_API_URL}/api/v1/runs/run_abc123/spans/<span-id>"
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

Requires the `read:query` JWT scope (new in v4.4.4). `format` is `json` or `csv` here (REST and SDK only).

### List Runs

```bash
GET /api/v1/runs?status=FAILED&limit=10&period=24h
```

### Cancel Run

```bash
POST /api/v1/runs/{runId}/cancel
```

### Complete Wait Token

Create the token first (`wait.createToken()`); its `id` starts with `waitpoint_`.

```bash
POST /api/v1/waitpoints/tokens/{waitpointId}/complete

curl -X POST "${TRIGGER_API_URL}/api/v1/waitpoints/tokens/${WAITPOINT_ID}/complete" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"approved": true}}'
```

The endpoint also accepts the token's short-lived `publicAccessToken`, so a browser can call it directly.

### Set Environment Variables

`{env}` is `dev`, `staging` or `prod`.

```bash
# One variable
POST /api/v1/projects/{projectRef}/envvars/{env}

curl -X POST "${TRIGGER_API_URL}/api/v1/projects/proj_xxx/envvars/prod" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name": "DATABASE_URL", "value": "<value>", "isSecret": true}'

# Several at once: `variables` is a name -> value map; `override: true` replaces existing
# values, `isSecret: true` stores them redacted. (The published OpenAPI page shows an array;
# the SDK sends the map form.)
POST /api/v1/projects/{projectRef}/envvars/{env}/import

curl -X POST "${TRIGGER_API_URL}/api/v1/projects/proj_xxx/envvars/prod/import" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"variables": {"DATABASE_URL": "<value>", "API_KEY": "<value>"}, "override": true}'
```

The CLI equivalent is `npx trigger.dev env set NAME VALUE --env prod [--secret]` (CLI 4.6.1+).

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
POST /api/v1/deployments/{version}/promote?allowRollbacks=true
```

`{version}` is the deployment version string (for example `20260101.1`), not a deployment ID. `allowRollbacks=true` (new in v4.4.4) lets the promote endpoint downgrade to an older version. The CLI equivalent is `npx trigger.dev promote <version>`.

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
