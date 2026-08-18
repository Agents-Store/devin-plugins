# Advanced Task Patterns

## Debouncing

Consolidate rapid triggers into a single execution:

```ts
await myTask.trigger(
  { userId: "123" },
  {
    debounce: {
      key: "user-123-update",
      delay: "5s",
      mode: "trailing",  // Use latest payload (default: "leading")
    },
  }
);
```

Modes:
- `leading` — executes immediately, ignores subsequent triggers during delay
- `trailing` — waits for delay, uses the most recent payload

## Idempotency

Prevent duplicate executions:

```ts
import { task, idempotencyKeys } from "@trigger.dev/sdk";

export const paymentTask = task({
  id: "process-payment",
  run: async (payload: { orderId: string }) => {
    const key = await idempotencyKeys.create(`payment-${payload.orderId}`);

    await chargeCustomer.trigger(payload, {
      idempotencyKey: key,
      idempotencyKeyTTL: "24h",
    });
  },
});
```

## Error Handling

### AbortTaskRunError (no retry)

```ts
import { AbortTaskRunError } from "@trigger.dev/sdk";

export const strictTask = task({
  id: "strict-task",
  run: async (payload) => {
    if (!payload.isValid) {
      throw new AbortTaskRunError("Invalid payload — will NOT retry");
    }
  },
});
```

### catchError (custom retry logic)

```ts
export const smartRetry = task({
  id: "smart-retry",
  retry: { maxAttempts: 10 },
  catchError: async ({ payload, error, ctx, retryAt }) => {
    if (error.message.includes("rate limit")) {
      return { retryAt: new Date(Date.now() + 60000) };  // Retry in 1 min
    }
    if (error.message.includes("fatal")) {
      return { skipRetrying: true };  // Stop retries
    }
    // Return undefined → use normal retry strategy
  },
  run: async (payload) => { /* ... */ },
});
```

### retry.onThrow (inline retries)

```ts
import { retry } from "@trigger.dev/sdk";

const result = await retry.onThrow(
  async () => unstableApiCall(payload),
  { maxAttempts: 3, factor: 2, minTimeoutInMs: 500 }
);
```

### retry.fetch (HTTP retries)

```ts
const response = await retry.fetch("https://api.example.com/data", {
  timeoutInMs: 5000,
  retry: {
    byStatus: {
      "429": { strategy: "headers", limitHeader: "x-ratelimit-limit" },
      "500-599": { strategy: "backoff", maxAttempts: 10 },
    },
    timeout: { maxAttempts: 5, factor: 1.8 },
  },
});
```

## Concurrency Patterns

### Task-level concurrency

```ts
export const oneAtATime = task({
  id: "sequential-task",
  queue: { concurrencyLimit: 1 },
  run: async (payload) => {},
});
```

### Shared queue

```ts
import { queue } from "@trigger.dev/sdk";

const apiQueue = queue({
  name: "external-api",
  concurrencyLimit: 3,
});

export const apiCall = task({
  id: "api-call",
  queue: apiQueue,
  run: async (payload) => {},
});
```

### Per-tenant concurrency (at trigger time)

```ts
await childTask.trigger(payload, {
  queue: {
    name: `user-${userId}`,
    concurrencyLimit: 2,
  },
});
```

## Wait Patterns

### Duration waits

```ts
import { wait } from "@trigger.dev/sdk";

await wait.for({ seconds: 30 });
await wait.for({ minutes: 5 });
await wait.for({ hours: 1 });
await wait.until({ date: new Date("2024-12-25") });
```

> Waits > 5 seconds are checkpointed — they don't consume compute time.

### Wait for token (human-in-the-loop)

```ts
const result = await wait.forToken<{ approved: boolean }>("approval-123");

if (result.ok) {
  console.log("Approved:", result.output.approved);
} else {
  console.log("Token timed out:", result.error);
}

// Or use .unwrap() to throw on timeout:
const approval = await wait.forToken<{ approved: boolean }>("approval-123").unwrap();
```

Complete the token via SDK or REST API:

```ts
import { wait } from "@trigger.dev/sdk";
await wait.completeToken<{ approved: boolean }>("approval-123", { approved: true });
```

## Trigger Options Reference

| Option | Type | Description |
|--------|------|-------------|
| `delay` | string/datetime | Delay before execution ("5m", "2h", ISO datetime) |
| `tags` | string[] | Up to 10 tags, each < 128 chars |
| `machine` | object | Machine preset override |
| `maxAttempts` | integer | Max retry attempts |
| `maxDuration` | number | Max run duration in seconds |
| `ttl` | string/integer | Time-to-live before auto-cancel (default "10m") |
| `idempotencyKey` | string | Prevent duplicate runs |
| `queue` | object | Override queue name and concurrency |
| `debounce` | object | Debounce config (key, delay, mode) |
