---
name: task-development
description: Write Trigger.dev tasks, configure retries, queues, concurrency, waits, metadata, tags, debouncing, idempotency, and use the @trigger.dev/sdk. Use when the user asks to "write a trigger.dev task", "create a background job", "add retries to task", "set up a task queue", "use triggerAndWait", "schedule a cron job", or needs SDK code patterns for Trigger.dev.
---

# Task Development

Build durable background tasks that run reliably with automatic retries, queuing, and observability.

## Critical Rules

1. **Always use `@trigger.dev/sdk`** — never use deprecated `client.defineJob` or `@trigger.dev/sdk/v3`
2. **Check `result.ok`** before accessing `result.output` from `triggerAndWait()`
3. **Never use `Promise.all`** with `triggerAndWait()` or `wait.*` calls — use `batchTriggerAndWait` instead
4. **Export every task** from files in your `trigger/` directory — unexported tasks are invisible
5. **Use `logger`** for structured logs — `import { logger } from "@trigger.dev/sdk"`, not just `console.log`
6. **Lazy-initialize external SDK clients** — never instantiate clients (e.g. `new OpenAI()`, `new S3Client()`) at the module top level because env vars like `OPENAI_API_KEY` are not available during the Docker build phase, causing the deploy to fail with "Missing credentials"

```ts
// BAD — fails during deploy build
import OpenAI from "openai";
const openai = new OpenAI(); // ← crashes: OPENAI_API_KEY undefined at build time

// GOOD — initialized on first use at runtime
import OpenAI from "openai";
let _openai: OpenAI | null = null;
function getClient(): OpenAI {
  if (!_openai) _openai = new OpenAI();
  return _openai;
}
```

## Basic Task

```ts
import { task } from "@trigger.dev/sdk";

export const processData = task({
  id: "process-data",
  retry: {
    maxAttempts: 10,
    factor: 1.8,
    minTimeoutInMs: 500,
    maxTimeoutInMs: 30_000,
  },
  run: async (payload: { userId: string; data: any[] }) => {
    console.log(`Processing ${payload.data.length} items`);
    return { processed: payload.data.length };
  },
});
```

## Schema Task (Validated Input)

```ts
import { schemaTask } from "@trigger.dev/sdk";
import { z } from "zod";

export const validatedTask = schemaTask({
  id: "validated-task",
  schema: z.object({
    name: z.string(),
    email: z.string().email(),
  }),
  run: async (payload) => {
    return { message: `Hello ${payload.name}` };
  },
});
```

## Triggering Tasks

### From Backend Code

```ts
import { tasks } from "@trigger.dev/sdk";
import type { processData } from "./trigger/tasks";

// Fire and forget
const handle = await tasks.trigger<typeof processData>("process-data", {
  userId: "123", data: [{ id: 1 }],
});

// Batch trigger (up to 1,000 items)
const batchHandle = await tasks.batchTrigger<typeof processData>("process-data", [
  { payload: { userId: "123", data: [] } },
  { payload: { userId: "456", data: [] } },
]);
```

### From Inside Tasks

```ts
export const parentTask = task({
  id: "parent-task",
  run: async (payload) => {
    // Fire and forget
    const handle = await childTask.trigger({ data: "value" });

    // Wait for result — returns Result object, NOT direct output
    const result = await childTask.triggerAndWait({ data: "value" });
    if (result.ok) {
      console.log("Output:", result.output);
    } else {
      console.error("Failed:", result.error);
    }

    // Quick unwrap (throws on error)
    const output = await childTask.triggerAndWait({ data: "value" }).unwrap();

    // Batch with wait
    const results = await childTask.batchTriggerAndWait([
      { payload: { data: "item1" } },
      { payload: { data: "item2" } },
    ]);
  },
});
```

## TTL

Tasks can be configured to expire if not dequeued in time — runs that expire get status `EXPIRED`.

```ts
export const hotfix = task({
  id: "hotfix",
  ttl: "30m",         // expire after 30 minutes in the queue
  run: async (payload) => { /* … */ },
});

// Per-trigger override
await hotfix.trigger(payload, { ttl: "5m" });

// Opt out of a global TTL default set in trigger.config.ts
export const longRunning = task({
  id: "long-running",
  ttl: 0,             // never expire due to queue wait
  run: async (payload) => { /* … */ },
});
```

Precedence: `options.ttl` at trigger time > task-level `ttl` > global `ttl` in `defineConfig(...)`. See the **config-and-build** skill for global defaults.

## Waits

```ts
import { task, wait } from "@trigger.dev/sdk";

export const taskWithWaits = task({
  id: "task-with-waits",
  run: async (payload) => {
    await wait.for({ seconds: 30 });
    await wait.for({ minutes: 5 });
    await wait.until({ date: new Date("2024-12-25") });

    // Wait for external approval (human-in-the-loop) — returns Result
    const result = await wait.forToken<{ approved: boolean }>("user-approval-token");
    if (result.ok) console.log("Approved:", result.output.approved);
  },
});
```

> Waits > 5 seconds are checkpointed and don't count toward compute.

## Concurrency & Queues

```ts
import { task, queue } from "@trigger.dev/sdk";

const emailQueue = queue({
  name: "email-processing",
  concurrencyLimit: 5,
});

export const sendEmail = task({
  id: "send-email",
  queue: emailQueue,
  run: async (payload) => {},
});

// Per-tenant concurrency at trigger time
await childTask.trigger(payload, {
  queue: { name: `user-${userId}`, concurrencyLimit: 2 },
});
```

## Error Handling & Retries

```ts
import { task, retry, AbortTaskRunError } from "@trigger.dev/sdk";

export const resilientTask = task({
  id: "resilient-task",
  retry: { maxAttempts: 10, factor: 1.8, minTimeoutInMs: 500, maxTimeoutInMs: 30_000 },
  catchError: async ({ error }) => {
    if (error.code === "FATAL_ERROR") throw new AbortTaskRunError("Cannot retry");
    return { retryAt: new Date(Date.now() + 60000) };
  },
  run: async (payload) => {
    const result = await retry.onThrow(
      async () => unstableApiCall(payload),
      { maxAttempts: 3 }
    );
  },
});
```

## Scheduled Tasks (Cron)

```ts
import { schedules } from "@trigger.dev/sdk";

export const dailyTask = schedules.task({
  id: "daily-cleanup",
  cron: "0 0 * * *",
  run: async (payload) => {
    // payload.timestamp, payload.timezone, payload.scheduleId
  },
});

// With timezone
export const tokyoTask = schedules.task({
  id: "tokyo-morning",
  cron: { pattern: "0 9 * * *", timezone: "Asia/Tokyo" },
  run: async () => {},
});
```

## Logging

Use the structured `logger` for searchable, filterable logs:

```ts
import { task, logger } from "@trigger.dev/sdk";

export const myTask = task({
  id: "my-task",
  run: async (payload) => {
    logger.info("Processing started", { itemCount: payload.items.length });
    logger.warn("Slow response detected", { latencyMs: 3200 });
    logger.error("Failed to process", { itemId: "123" });
  },
});
```

`console.log` also works but `logger` is recommended — structured logs are searchable in the dashboard.

## Metadata & Progress

Metadata is a standalone import. All update methods are synchronous and chainable:

```ts
import { task, metadata } from "@trigger.dev/sdk";

export const batchProcessor = task({
  id: "batch-processor",
  run: async (payload: { items: any[] }) => {
    metadata.set("progress", 0).set("total", payload.items.length);
    for (let i = 0; i < payload.items.length; i++) {
      await processItem(payload.items[i]);
      metadata.set("progress", ((i + 1) / payload.items.length) * 100);
    }
    metadata.flush(); // Force immediate persistence if needed
  },
});
```

Available methods: `set()`, `get()`, `del()`, `replace()`, `append()`, `remove()`, `increment()`, `decrement()`, `flush()`, `current()`. Max 256KB per run.
```

## Machine Presets

| Preset | vCPU | RAM | Disk |
|--------|------|-----|------|
| micro | 0.25 | 0.25 GB | 10 GB |
| small-1x | 0.5 | 0.5 GB (default) | 10 GB |
| small-2x | 1 | 1 GB | 10 GB |
| medium-1x | 1 | 2 GB | 10 GB |
| medium-2x | 2 | 4 GB | 10 GB |
| large-1x | 4 | 8 GB | 10 GB |
| large-2x | 8 | 16 GB | 10 GB |

```ts
export const heavyTask = task({
  id: "heavy-computation",
  machine: { preset: "large-2x" },
  maxDuration: 1800,
  run: async (payload) => {},
});
```

## Deeper Reference

- @references/basic-tasks.md — core task patterns in detail
- @references/advanced-tasks.md — debouncing, idempotency, tags, error handling
- @references/scheduled-tasks.md — cron patterns, dynamic schedules
- @references/triggering-patterns.md — all trigger and batch methods
