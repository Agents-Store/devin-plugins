# Triggering Patterns

All methods for triggering tasks — single, batch, with wait, typed.

## From Backend Code

```ts
import { tasks } from "@trigger.dev/sdk";
import type { myTask } from "./trigger/tasks";

// Single trigger (fire and forget)
const handle = await tasks.trigger<typeof myTask>("my-task", payload);
console.log("Run ID:", handle.id);

// Batch trigger (up to 1,000 items, 3MB per payload)
const batchHandle = await tasks.batchTrigger<typeof myTask>("my-task", [
  { payload: { id: "1" } },
  { payload: { id: "2" } },
]);
```

## From Inside Tasks

### trigger() — fire and forget

```ts
const handle = await childTask.trigger({ data: "value" });
// Returns immediately with handle.id
```

### triggerAndWait() — wait for result

```ts
const result = await childTask.triggerAndWait({ data: "value" });
if (result.ok) {
  console.log(result.output);  // Typed output
} else {
  console.error(result.error);
}
```

### .unwrap() — shorthand

```ts
const output = await childTask.triggerAndWait({ data: "value" }).unwrap();
// Throws if the child task fails
```

### batchTriggerAndWait() — parallel batch

```ts
const results = await childTask.batchTriggerAndWait([
  { payload: { data: "item1" } },
  { payload: { data: "item2" } },
]);
```

## Typed Multi-Task Batch

Use `batch.triggerByTaskAndWait` to run different tasks in parallel:

```ts
import { batch } from "@trigger.dev/sdk";

const { runs: [sentimentResult, summaryResult, moderationResult] } =
  await batch.triggerByTaskAndWait([
    { task: analyzeSentiment, payload: { text } },
    { task: summarizeText, payload: { text } },
    { task: moderateContent, payload: { text } },
  ]);

if (sentimentResult.ok) {
  console.log(sentimentResult.output);  // Typed per task
}
```

## Trigger with Options

```ts
await myTask.trigger(payload, {
  delay: "5m",
  tags: ["priority", "vip"],
  machine: { preset: "medium-1x" },
  maxAttempts: 5,
  maxDuration: 300,
  ttl: "30m",
  idempotencyKey: "unique-key",
  queue: { name: "high-priority" },
});
```

## REST API Trigger

```bash
curl -X POST "${TRIGGER_API_URL}/api/v1/tasks/my-task/trigger" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"payload": {"name": "test"}, "options": {"tags": ["api"]}}'
```

## Run Status Values

| Status | Description |
|--------|-------------|
| QUEUED | In queue, waiting to execute |
| EXECUTING | Currently running |
| COMPLETED | Finished successfully |
| FAILED | Task threw an error |
| CRASHED | OOM or unexpected crash |
| CANCELED | Manually cancelled |
| DELAYED | Waiting for delay to expire |
| EXPIRED | TTL expired before execution |
| TIMED_OUT | Exceeded maxDuration |
| WAITING | Paused (wait.for, triggerAndWait) |
| PENDING_VERSION | Waiting for matching deployment |
| SYSTEM_FAILURE | Infrastructure issue |
