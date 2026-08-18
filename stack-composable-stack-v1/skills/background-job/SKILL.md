---
name: background-job
description: This skill should be used when the user wants to "create a background job", "run async task", "process data in background", "schedule recurring task", "set up a queue", or needs patterns for background processing using Trigger.dev and n8n in the Composable Stack.
---

# Background Job Patterns

Patterns for background processing in the Composable Stack using Trigger.dev (durable tasks) and n8n (workflow automation).

## Choosing the Right Service

| Pattern | Service | When to Use |
|---------|---------|-------------|
| One-off background task | Trigger.dev | Long-running, needs retries, >30s |
| Scheduled recurring job | n8n or Trigger.dev | n8n for simple schedules, Trigger.dev for complex |
| Event-driven automation | n8n | Webhook triggers, multi-step visual workflows |
| AI/LLM pipeline | Trigger.dev | Token streaming, checkpointing, long waits |
| Data sync/ETL | n8n | Visual data transformation, multiple integrations |
| Queue-based processing | Trigger.dev | Rate limiting, ordered execution, concurrency control |
| Simple notification relay | n8n | Quick webhook → email/Slack |

## Trigger.dev Task Patterns

### Basic Background Task

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const processOrder = task({
  id: "process-order",
  retry: { maxAttempts: 3 },
  run: async (payload: { orderId: number }) => {
    // 1. Fetch order data from NocoDB
    // 2. Process payment
    // 3. Update order status
    // 4. Return result
    return { success: true, orderId: payload.orderId };
  },
});
```

### Queue-Based Processing

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const sendEmail = task({
  id: "send-email",
  queue: { name: "email-queue", concurrencyLimit: 5 },
  retry: { maxAttempts: 3 },
  run: async (payload: { to: string; subject: string; body: string }) => {
    // Send email with rate limiting via queue
  },
});
```

### Scheduled Task

```typescript
import { schedules } from "@trigger.dev/sdk/v3";

export const dailyReport = schedules.task({
  id: "daily-report",
  cron: "0 9 * * *", // 9 AM daily
  run: async () => {
    // 1. Query NocoDB for daily stats
    // 2. Generate report
    // 3. Send via n8n webhook or email
  },
});
```

### Orchestrator Pattern

```typescript
import { task } from "@trigger.dev/sdk/v3";

export const processNewUser = task({
  id: "process-new-user",
  run: async (payload: { userId: number }) => {
    // Run subtasks in parallel
    const [profile, welcome, sync] = await Promise.all([
      createUserProfile.triggerAndWait({ userId: payload.userId }),
      sendWelcomeEmail.triggerAndWait({ userId: payload.userId }),
      syncToCRM.triggerAndWait({ userId: payload.userId }),
    ]);

    return { profile, welcome, sync };
  },
});
```

## n8n Workflow Patterns

### Scheduled Data Sync

```
[Schedule Trigger] → [Query NocoDB] → [Transform Data] → [HTTP: External API] → [Update NocoDB Status]
```

### Webhook-Triggered Processing

```
[Webhook] → [Validate Payload] → [Switch: Event Type] →
  ├─ [Create Path] → [Process New Record] → [Respond 200]
  ├─ [Update Path] → [Sync Changes] → [Respond 200]
  └─ [Delete Path] → [Cleanup] → [Respond 200]
```

### Error Recovery Workflow

```
[Error Trigger] → [Log to NocoDB Error Table] → [Check Retry Count] →
  ├─ [< Max Retries] → [Wait 5min] → [Retry Original Workflow]
  └─ [>= Max Retries] → [Send Alert Notification]
```

## Triggering Tasks via MCP

### Start a Trigger.dev Task

```
Tool: mcp__trigger-dev__trigger_task
Input: {
  "taskId": "process-order",
  "payload": { "orderId": 123 }
}
```

### Monitor a Run

```
Tool: mcp__trigger-dev__get_run_details
Input: { "runId": "run_xxx" }
```

### Execute an n8n Workflow

Use the n8n native MCP or call a webhook directly.

## Error Handling Strategy

1. **Task-level retries** — Trigger.dev `retry.maxAttempts` for transient failures
2. **Workflow-level error trigger** — n8n Error Trigger node for workflow failures
3. **Dead letter queue** — store failed jobs in NocoDB `failed_jobs` table
4. **Status tracking** — update a `job_status` field: `queued` → `running` → `completed` / `failed`
5. **Alerting** — notify via n8n on critical failures (Slack, email)

## Best Practices

- Use Trigger.dev for anything that takes >30 seconds
- Use n8n for visual workflows with multiple integration points
- Always include a `job_status` field in NocoDB tables that trigger background jobs
- Use idempotency keys to prevent duplicate processing
- Log all background job results to a NocoDB table for auditability
- Set appropriate machine presets in Trigger.dev for resource-intensive tasks
- Use Trigger.dev queues with concurrency limits for rate-sensitive operations
