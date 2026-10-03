---
name: nocodb-to-trigger
description: This skill should be used when the user wants to "trigger background task from NocoDB", "connect NocoDB to Trigger.dev", "process NocoDB data with Trigger.dev", "run background job on NocoDB change", or needs to integrate NocoDB data events with Trigger.dev background tasks.
---

# NocoDB to Trigger.dev Integration

Patterns for triggering Trigger.dev background tasks from NocoDB data events. Use for long-running operations, AI processing, and durable execution that would time out in n8n. The task code is in `trigger-dev`; the NocoDB side is in `nocodb-ops`; this skill is the link between them.

## When to Use Trigger.dev vs n8n

| Use Case | Service | Reason |
|----------|---------|--------|
| Short workflow (<30s) | n8n | Visual workflow, quick execution |
| Long-running job (>30s) | Trigger.dev | Durable execution, retries |
| AI/LLM processing | Trigger.dev | Token streaming, long waits |
| Multi-step orchestration | Trigger.dev | Checkpointing, resumability |
| Simple webhook relay | n8n | Low overhead, visual |
| File processing | Trigger.dev | Large memory, long timeouts |

## Integration Patterns

### Pattern 1: NocoDB Webhook → n8n → Trigger.dev Task

Chain through n8n as a lightweight dispatcher.

```
[NocoDB Webhook] → [n8n: Webhook] → [Split Out: body.data.rows] → [n8n: HTTP Request → Trigger.dev API] → [Trigger.dev: Process]
```

NocoDB sends the changed records as an array (`body.data.rows`, see `nocodb-ops:webhooks`); split it so each record becomes one task run. Use an **HTTP Request** node for the call — not a Code node. In n8n 2.x Code nodes run in task runners and cannot read `process.env` or `$env` (blocked by default), and an `Authorization` header belongs in a credential anyway:

```
Method:         POST
URL:            <TRIGGER_API_URL>/api/v1/tasks/<taskId>/trigger      (fixed in the node)
Authentication: Generic Credential Type → Header Auth
                (Name: Authorization, Value: Bearer <TRIGGER_SECRET_KEY>)
Send Body:      JSON
Body:           {
                  "payload": { "recordId": {{ $json.Id }}, "tableId": "<tableId>" },
                  "options": { "idempotencyKey": "record-{{ $json.Id }}-{{ $json.UpdatedAt }}" }
                }
```

The idempotency key (record id plus its `UpdatedAt`) keeps a **repeated delivery of one event** from starting a second run. It does not stop a loop: `UpdatedAt` changes with every write. The trigger endpoint, its options and the secret-key rules: see `trigger-dev:mcp-patterns` (*REST Management API*).

**Guard against a self-trigger loop.** The task writes `processing_status` back to the row that fired the webhook, and on an *After Update* webhook that write is an update too — it fires the webhook again, `UpdatedAt` is new, and the key never dedupes. Break the loop at the source, with one of:

1. **A condition on the status transition** (all editions): *After Update* with the condition `processing_status` = `pending`. NocoDB fires a conditional webhook only when the record goes from "not met" to "met", and the task's own writes (`processing`, `completed`, `failed`) never meet it. Whoever wants a run (a user, a Button, an automation) sets the status to `pending`.
2. **Watch only the business fields** (paid plans): on *After Update* choose the fields to monitor and leave out the status and detail columns the task writes.
3. **Keep job state out of the triggering row**: write status to a separate `job_runs` table (or only into the Trigger.dev run metadata) so the task never updates the row it was started for.

Also make the task check first: read the record, and return without work unless `processing_status` is `pending`. Event details and conditions: `nocodb-ops:webhooks`.

### Pattern 2: Direct Trigger via MCP

Trigger a task directly from the agent with the Trigger.dev MCP tools. `trigger_task` runs in `dev` unless you pass `environment`.

```
Tool: mcp__plugin_stack-composable-stack-v1_trigger-dev__trigger_task
Input: {
  "taskId": "process-nocodb-record",
  "payload": {
    "recordId": 123,
    "tableId": "tbl_xxx",
    "action": "process"
  },
  "environment": "dev"
}
```

### Pattern 3: Batch Processing

Process many NocoDB records as background tasks: one parent task takes the table id and a list of record ids, fans out one child run per record (`batchTriggerAndWait` under a queue with a concurrency limit), and each child reads its record from NocoDB, processes it and writes its status back. Task code: see `trigger-dev:task-development` (`references/record-driven-tasks.md`, *Many records*).

### Pattern 4: AI Processing Pipeline

Use Trigger.dev for AI-powered processing of NocoDB data: the task reads the record, sends it to the model, stores the result back in NocoDB and updates the record status. It needs a larger machine preset, a `maxDuration` and few retries. Task code: see `trigger-dev:task-development` (`references/record-driven-tasks.md`, *AI processing of a record*).

## Monitoring Task Runs

Check task status via MCP:

```
Tool: mcp__plugin_stack-composable-stack-v1_trigger-dev__get_run_details
Input: { "runId": "run_xxx" }
```

List recent runs:

```
Tool: mcp__plugin_stack-composable-stack-v1_trigger-dev__list_runs
Input: { "limit": 10 }
```

## Error Handling

1. **Trigger.dev retries** — configure `retry.maxAttempts` on the task; `onFailure` runs when the retries are used up
2. **Status tracking** — update a `processing_status` field in NocoDB (`pending` → `processing` → `completed` / `failed`)
3. **Error logging** — write errors to a NocoDB `task_errors` table with run ID, error message, and timestamp
4. **Alerting** — chain a notification task on failure (Slack, email via n8n)

## Best Practices

- Never let a task's status write-back re-fire the webhook that started it (see the loop guard in Pattern 1)
- Use descriptive task IDs: `process-order-payment`, `generate-ai-summary`
- Include the NocoDB record ID and table ID in every task payload
- Update the NocoDB record status before and after processing
- Use Trigger.dev queues for rate-limited operations
- Set appropriate machine presets for CPU/memory-intensive tasks
- Use an `idempotencyKey` based on the record ID to prevent duplicate processing
