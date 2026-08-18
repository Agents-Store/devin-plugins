# Basic Task Patterns

## Task Function

The `task()` function is the core building block:

```ts
import { task } from "@trigger.dev/sdk";

export const myTask = task({
  id: "my-task",              // Unique identifier (kebab-case)
  retry: { ... },             // Optional retry config
  queue: { ... },             // Optional queue/concurrency
  machine: { preset: "..." }, // Optional machine preset
  maxDuration: 300,           // Optional max seconds
  run: async (payload) => {   // The task function
    return { result: "done" };
  },
});
```

## Schema Task (with validation)

```ts
import { schemaTask } from "@trigger.dev/sdk";
import { z } from "zod";

export const processEmail = schemaTask({
  id: "process-email",
  schema: z.object({
    to: z.string().email(),
    subject: z.string().min(1),
    body: z.string(),
    priority: z.enum(["low", "normal", "high"]).default("normal"),
  }),
  run: async (payload) => {
    // payload is typed and validated before run() executes
    return { sent: true, to: payload.to };
  },
});
```

## Task with Full Configuration

```ts
export const processOrder = task({
  id: "process-order",
  retry: {
    maxAttempts: 5,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 30000,
  },
  machine: { preset: "small-1x" },
  queue: {
    name: "order-processing",
    concurrencyLimit: 10,
  },
  maxDuration: 300,
  run: async (payload: { orderId: string; items: string[] }) => {
    return { processed: true };
  },
});
```

## Core Imports

```ts
// Task definition
import { task, schemaTask, schedules, wait, queue, metadata, tags, logger } from "@trigger.dev/sdk";

// Error handling
import { retry, AbortTaskRunError, idempotencyKeys } from "@trigger.dev/sdk";

// Triggering from backend
import { tasks, configure, runs, batch } from "@trigger.dev/sdk";

// Configuration
import { defineConfig } from "@trigger.dev/sdk";

// Build extensions
import { prismaExtension } from "@trigger.dev/build/extensions/prisma";
import { syncEnvVars } from "@trigger.dev/build/extensions/core";

// React hooks (frontend)
import { useRealtimeRun, useRealtimeBatch } from "@trigger.dev/react-hooks";
```

## Logging

Use `logger` from `@trigger.dev/sdk` for structured, searchable logs:

```ts
import { task, logger } from "@trigger.dev/sdk";

export const myTask = task({
  id: "my-task",
  run: async (payload) => {
    logger.info("Starting processing", { payloadSize: payload.items.length });
    logger.warn("Slow API response detected", { latencyMs: 3200 });
    logger.error("Failed to process item", { itemId: "123" });
    logger.debug("Debug details", { raw: payload });
  },
});
```

`console.log`/`console.error` also work and appear in the run trace, but `logger` creates structured logs that are easier to search and filter in the dashboard.
```

## Task with Tags

```ts
import { task, tags } from "@trigger.dev/sdk";

export const processUser = task({
  id: "process-user",
  run: async (payload: { userId: string }) => {
    await tags.add(`user_${payload.userId}`);
    // Tags can be used to filter runs in the dashboard and via API
  },
});

// Trigger with tags
await processUser.trigger(
  { userId: "123" },
  { tags: ["priority", "user_123"] }  // Up to 10 tags, each < 128 chars
);
```

## Task with Metadata

```ts
import { task, metadata } from "@trigger.dev/sdk";

export const longTask = task({
  id: "long-task",
  run: async (payload) => {
    metadata.set("status", "starting");
    metadata.set("progress", 0);

    // Update progress as you go
    for (let i = 0; i < 100; i++) {
      await doWork(i);
      metadata.set("progress", i + 1);
    }

    metadata.set("status", "completed");
  },
});
```

Metadata is visible in the dashboard and via the Realtime API.
