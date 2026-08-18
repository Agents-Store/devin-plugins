---
name: nocodb-to-trigger
description: This skill should be used when the user wants to "trigger background task from NocoDB", "connect NocoDB to Trigger.dev", "process NocoDB data with Trigger.dev", "run background job on NocoDB change", or needs to integrate NocoDB data events with Trigger.dev background tasks.
---

# NocoDB to Trigger.dev Integration

Patterns for triggering Trigger.dev background tasks from NocoDB data events. Use for long-running operations, AI processing, and durable execution that would timeout in n8n.

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
[NocoDB Webhook] → [n8n: Parse + Validate] → [n8n: Trigger Task via API] → [Trigger.dev: Process]
```

**n8n Code node to trigger a task:**

```javascript
const taskId = 'your-task-id';
const payload = $json.body.data.rows[0];

const response = await fetch(`${process.env.TRIGGER_API_URL}/api/v1/tasks/${taskId}/trigger`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.TRIGGER_SECRET_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ payload })
});

return { json: await response.json() };
```

### Pattern 2: Direct Trigger via MCP

Trigger a task directly using the Trigger.dev MCP tools.

```
Tool: mcp__trigger-dev__trigger_task
Input: {
  "taskId": "process-nocodb-record",
  "payload": {
    "recordId": 123,
    "tableId": "tbl_xxx",
    "action": "process"
  }
}
```

### Pattern 3: Batch Processing

Process multiple NocoDB records as background tasks.

**Trigger.dev task structure:**

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const processRecords = task({
  id: "process-nocodb-records",
  retry: { maxAttempts: 3 },
  run: async (payload: { tableId: string; filter: string }) => {
    // 1. Query records from NocoDB
    // 2. Process each record
    // 3. Update status back in NocoDB
    // 4. Return summary
  },
});
```

### Pattern 4: AI Processing Pipeline

Use Trigger.dev for AI-powered processing of NocoDB data.

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const aiProcessRecord = task({
  id: "ai-process-record",
  machine: { preset: "medium-1x" },
  retry: { maxAttempts: 2 },
  run: async (payload: { recordId: number; tableId: string }) => {
    // 1. Fetch record from NocoDB
    // 2. Send to LLM for processing
    // 3. Store result back in NocoDB
    // 4. Update record status
  },
});
```

## Monitoring Task Runs

Check task status via MCP:

```
Tool: mcp__trigger-dev__get_run_details
Input: { "runId": "run_xxx" }
```

List recent runs:

```
Tool: mcp__trigger-dev__list_runs
Input: { "limit": 10 }
```

## Error Handling

1. **Trigger.dev retries** — configure `retry.maxAttempts` on the task
2. **Status tracking** — update a `processing_status` field in NocoDB (`pending` → `processing` → `completed` / `failed`)
3. **Error logging** — write errors to a NocoDB `task_errors` table with run ID, error message, and timestamp
4. **Alerting** — chain a notification task on failure (Slack, email via n8n)

## Best Practices

- Use descriptive task IDs: `process-order-payment`, `generate-ai-summary`
- Include the NocoDB record ID and table ID in every task payload
- Update NocoDB record status before and after processing
- Use Trigger.dev queues for rate-limited operations
- Set appropriate machine presets for CPU/memory-intensive tasks
- Use `idempotencyKey` based on record ID to prevent duplicate processing
