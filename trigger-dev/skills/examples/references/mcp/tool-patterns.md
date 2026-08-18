# MCP Tool Call Patterns

## Check Available Tasks

```
Tool: get_current_worker
Input: { "environment": "dev" }
→ Returns worker version, task list with IDs, payload schemas, machine presets
```

## Trigger a Task

```
Tool: trigger_task
Input: {
  "taskId": "process-order",
  "payload": { "orderId": "ORD-123", "items": ["item-1"] },
  "environment": "dev"
}
→ { id: "run_abc123", status: "QUEUED" }
```

## Trigger with Full Options

```
Tool: trigger_task
Input: {
  "taskId": "process-order",
  "payload": { "orderId": "ORD-123" },
  "environment": "prod",
  "options": {
    "tags": ["priority", "vip"],
    "idempotencyKey": "order-ORD-123",
    "machine": "medium-1x",
    "maxAttempts": 5,
    "delay": "5m"
  }
}
```

## Wait for Completion

```
Tool: wait_for_run_to_complete
Input: { "runId": "run_abc123", "timeoutInSeconds": 120 }
→ { status: "COMPLETED", output: { processed: true } }
```

## List Failed Runs

```
Tool: list_runs
Input: {
  "environment": "prod",
  "status": "FAILED",
  "period": "7d",
  "limit": 20
}
```

## Get Run Details with Trace

```
Tool: get_run_details
Input: { "runId": "run_abc123", "environment": "prod", "maxTraceLines": 500 }
→ { status, error, trace: [...], output: {...} }
```

## Deploy to Staging

```
Tool: deploy
Input: { "environment": "staging" }
→ { status: "DEPLOYED", version: "20250225.2" }
```

## Search Documentation

```
Tool: search_docs
Input: { "query": "wait for token human in the loop" }
```

## Full Workflow: Trigger → Wait → Report

```
1. get_current_worker(environment="dev")
   → Find task ID and verify payload schema

2. trigger_task(taskId="hello-world", payload={"name": "Claude"})
   → Get run_xxx ID

3. wait_for_run_to_complete(runId="run_xxx", timeoutInSeconds=60)
   → Get final status and output
```

## Full Workflow: Debug Failed Run

```
1. list_runs(status="FAILED", period="1d", limit=5)
   → Get list of failed run IDs

2. get_run_details(runId="run_xxx", maxTraceLines=500)
   → Read error message and stack trace, grab spanId of the failing span

3. get_span_details(runId="run_xxx", spanId="span_xxx")
   → AI enrichment (llm model/tokens/cost) + child runs

4. search_docs(query="<error message keywords>")
   → Find relevant documentation
```

## Profile Switch

```
Tool: whoami
→ { profile: "default", user: {...}, apiUrl: "https://api.trigger.dev" }

Tool: list_profiles
→ { active: "default", profiles: [{ name, apiUrl }, ...] }

Tool: switch_profile
Input: { "profile": "self-hosted-prod" }
→ { active: "self-hosted-prod", apiUrl: "https://trigger.example.com" }
```

## Get Task Schema

```
Tool: get_task_schema
Input: { "taskIdentifier": "process-order", "environment": "dev" }
→ { payloadSchema: { type: "object", properties: {...}, required: [...] } }
```

Note: v4.4.4 removed inlined payload schemas from `get_current_worker` — always call this before `trigger_task`.

## Run TRQL Query

```
Tool: get_query_schema
Input: { "table": "runs" }
→ { table: "runs", columns: [...] }

Tool: query
Input: {
  "query": "SELECT status, count() AS n FROM runs GROUP BY status",
  "period": "7d",
  "scope": "environment"
}
→ (text table)
```

## Run a Dashboard Widget

```
Tool: list_dashboards
→ [{ dashboardId: "overview", widgets: [{ widgetId: "failure-rate", title: "Failure rate" }] }]

Tool: run_dashboard_query
Input: { "dashboardId": "overview", "widgetId": "failure-rate", "period": "30d" }
→ (text table)
```

## Dev Server Lifecycle

```
Tool: start_dev_server
Input: { "configPath": "./packages/jobs/trigger.config.ts" }
→ { status: "ready", pid: 12345 }

Tool: dev_server_status
Input: { "lines": 50 }
→ { status: "ready", recentLogs: [...] }

Tool: stop_dev_server
→ { status: "stopped" }
```

## Managed Prompts — Hotfix Workflow

```
Tool: list_prompts
Input: { "environment": "prod" }
→ [{ slug: "customer-reply", currentVersion: 4, overrideActive: false, versionCount: 7 }]

Tool: get_prompt_versions
Input: { "slug": "customer-reply", "environment": "prod" }
→ [{ version: 4, labels: ["current", "latest"], source: "code", ... }]

Tool: create_prompt_override
Input: {
  "slug": "customer-reply",
  "textContent": "You are a support agent. Be concise…",
  "commitMessage": "Hotfix tone OPS-1234",
  "environment": "prod"
}
→ { slug: "customer-reply", overrideVersion: 8, source: "dashboard" }

Tool: remove_prompt_override
Input: { "slug": "customer-reply", "environment": "prod" }
→ { slug: "customer-reply", overrideActive: false }
```
