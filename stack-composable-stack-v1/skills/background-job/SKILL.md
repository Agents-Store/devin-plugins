---
name: background-job
description: This skill should be used when the user wants to "create a background job", "run async task", "process data in background", "schedule recurring task", "set up a queue", "choose between n8n and Trigger.dev", or needs to decide how background processing is split between Trigger.dev and n8n in the Composable Stack.
---

# Background Job Patterns

How background processing is divided between Trigger.dev (durable tasks) and n8n (workflow automation) in the Composable Stack, and how a job reports its state. The code and node-level detail live in the technology plugins; this skill is the decision and the contract between them.

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

## Where the Patterns Live

- Trigger.dev tasks — basic task, queues with `queue()`, cron schedules, fan-out with `batchTriggerAndWait`, record-driven tasks: see `trigger-dev:task-development` (and its `references/record-driven-tasks.md`)
- Start and watch a task from the agent (`trigger_task`, `get_run_details`, `list_runs`): see `trigger-dev:mcp-patterns`; in this stack the tools are named `mcp__plugin_stack-composable-stack-v1_trigger-dev__<tool>`, and `trigger_task` runs in `dev` unless you pass `environment`
- n8n workflow shapes — scheduled sync, webhook-triggered processing, error recovery: see `n8n-dev:examples` (`references/background-processing-patterns.md`)
- Run a workflow from the agent: the n8n native MCP (`mcp__plugin_stack-composable-stack-v1_n8n-native-mcp__execute_workflow`, which needs `executionMode`) or the workflow's webhook — see `n8n-dev:n8n-native-mcp`
- Which service starts which: `nocodb-to-n8n`, `nocodb-to-trigger`, `nocobase-to-n8n` in this plugin

## Error Handling Strategy

1. **Task-level retries** — Trigger.dev `retry.maxAttempts` for transient failures, `onFailure` to record the final failure
2. **Workflow-level error trigger** — n8n Error Trigger node for workflow failures
3. **Dead letter queue** — store failed jobs in a NocoDB `failed_jobs` table
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
