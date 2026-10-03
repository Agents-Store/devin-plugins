# MCP Tool Call Patterns

All tools return text, not JSON; the `→` lines summarise what the text contains. Names are shown bare; in a Claude Code session they carry the `mcp__<server>__` prefix of the user's MCP server.

## Check Available Tasks

```
Tool: get_current_worker
Input: { "environment": "dev" }
→ Worker version, SDK version, task slugs (agents marked [agent]) with file paths. No payload schemas: use get_task_schema
```

## Trigger a Task

```
Tool: trigger_task
Input: {
  "taskId": "process-order",
  "payload": { "orderId": "ORD-123", "items": ["item-1"] },
  "environment": "dev"
}
→ "Task process-order triggered and run with ID created: run_abc123" + dashboard URL
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
    "delay": "5m",
    "region": "us-east-1"
  }
}
```

## Wait for Completion

```
Tool: wait_for_run_to_complete
Input: { "runId": "run_abc123", "timeoutInSeconds": 120 }
→ Final run state and output (or the current state after the timeout)
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
→ Run details, then "Run Trace (lines 1-500 of N)"; when more exists, call again with the `cursor` the text gives
```

## Deploy to Staging

```
Tool: deploy
Input: { "environment": "staging" }
→ The CLI deploy log (build, push, "Version 20250225.2 deployed with N detected tasks")
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
→ Active profile, user, email and API URL

Tool: list_profiles
→ Every profile with its API URL; the active one is marked

Tool: switch_profile
Input: { "profile": "self-hosted-prod" }
→ Confirms the new active profile; later calls use its account and API URL
```

## Get Task Schema

```
Tool: get_task_schema
Input: { "taskSlug": "process-order", "environment": "dev" }
→ The payload schema (JSON Schema) of that task
```

Note: `get_current_worker` returns task slugs only, never payload schemas — call this before `trigger_task`.

## Run TRQL Query

```
Tool: get_query_schema
Input: { "table": "runs" }
→ Columns, types, descriptions and allowed values of the runs table

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
→ Per dashboard: title and key (`overview` = run metrics, `llm` = AI metrics), then a table of widget IDs, titles and types

Tool: run_dashboard_query
Input: { "dashboardKey": "llm", "widgetId": "llm-cost", "period": "30d" }
→ (text table)
```

## Dev Server Lifecycle

```
Tool: start_dev_server
Input: { "configPath": "./packages/jobs/trigger.config.ts" }
→ "Dev server is ready." plus recent log lines (or the build errors / a still-starting note)

Tool: dev_server_status
Input: { "lines": 50 }
→ "Dev Server Status: ready", the directory, and the last 50 log lines

Tool: stop_dev_server
→ "Dev server stopped."
```

## Managed Prompts — Hotfix Workflow

```
Tool: list_prompts
Input: { "environment": "prod" }
→ Per prompt: slug, current version, override status, version count

Tool: get_prompt_versions
Input: { "slug": "customer-reply", "environment": "prod" }
→ Per version: number, labels (current / override / latest), source (code / dashboard), model, content

Tool: create_prompt_override
Input: {
  "slug": "customer-reply",
  "textContent": "You are a support agent. Be concise…",
  "commitMessage": "Hotfix tone OPS-1234",
  "environment": "prod"
}
→ Confirms the new dashboard-sourced override version

Tool: remove_prompt_override
Input: { "slug": "customer-reply", "environment": "prod" }
→ Confirms the override is gone; the current code version applies again
```

## Health Report

```
Tool: get_report
Input: { "key": "health", "environment": "prod", "period": "24h" }
→ Verdict (flow / execution / liveness), sparklines and a suggested next action. Show it to the user as-is.
```

## Chat With a chat.agent (server ≥ 4.5.0)

```
Tool: list_agents
Input: { "environment": "dev" }
→ Agent slugs with file paths

Tool: start_agent_chat
Input: { "agentId": "support-chat", "chatId": "conversation-123", "clientData": { "userId": "user_123" } }
→ Chat ID, session ID, agent, run ID

Tool: send_agent_message
Input: { "chatId": "conversation-123", "message": "Where is my order?" }
→ The agent's full response text, then "Run: run_xxx"

Tool: close_agent_chat
Input: { "chatId": "conversation-123" }
→ "Chat conversation-123 closed."
```

## Session Side Channel (server ≥ 4.5.0)

```
Tool: read_session_channel
Input: { "sessionId": "session_xxx", "channel": "control", "io": "in", "maxRecords": 50 }
→ Records after the cursor, plus a nextCursor to pass as afterEventId

Tool: write_session_channel
Input: { "sessionId": "session_xxx", "channel": "control", "value": { "paused": true } }
→ "Wrote 1 record to session session_xxx channel "control" .in. This does not wake or trigger a run."
```

## Read-Only and Dev-Only Servers

These are server flags, set in the MCP config `args`, not tool inputs:

```json
{ "command": "npx", "args": ["trigger.dev@latest", "mcp", "--readonly", "--dev-only", "--project-ref", "proj_abc123"] }
```

With `--readonly` the 15 write tools (deploy, trigger_task, cancel_run, prompt writers, agent chat, write_session_channel, ...) do not exist for the model.
