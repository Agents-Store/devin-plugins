# Advanced Task Patterns

## Debouncing

Consolidate rapid triggers into a single delayed run. The first trigger with a debounce key creates a delayed run; every further trigger with the same key, while that run is still delayed, pushes its start later instead of creating a new run. The key is scoped to the task id.

```ts
await myTask.trigger(
  { userId: "123" },
  {
    debounce: {
      key: "user-123-update",
      delay: "5s",       // the run starts this long after the last trigger (minimum 1s)
      maxDelay: "2m",    // but never later than this after the first trigger (server >= 4.4.0)
      mode: "trailing",  // run with the latest payload (default: "leading")
    },
  }
);
```

Modes, which decide whose data the run uses once the delay has passed:
- `leading` (default): the run uses the data of the **first** trigger (payload, metadata, tags, `maxAttempts`, `maxDuration`, machine); later triggers only push the start later
- `trailing`: each later trigger replaces that data, so the run uses the **last** trigger's

Both modes wait for the delay. Neither runs at once.

`maxDelay` bounds the total wait. Without it a key that keeps being triggered pushes the run back for as long as the triggers keep coming, and it never starts. Keep `delay` well below `maxDelay`: a run is pushed back only while its new start stays inside `maxDelay`, so the room to push is `maxDelay` minus `delay`, and a `delay` equal to or above `maxDelay` makes the trigger fail instead of debouncing. Pass the same `maxDelay` on every trigger with that key: each call checks it against the first run's creation time, and a call that omits it has no bound. `delay` must be a duration (`"5s"`, `"1m"`, `"2h30m"`), not a date. A trigger that arrives after the run has started creates a new run, so two runs for one key can overlap. An `idempotencyKey` wins over a debounce key when both match.

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

These three forms (`concurrencyLimit` on a queue) run on every server version. SDK 4.7 deprecates them in favour of the `concurrency` option below; the replacement needs server ≥ 4.7.0.

### Concurrency 2.0 (requires server ≥ 4.7.0)

```ts
import { concurrencyLimit, concurrencyLimits, task } from "@trigger.dev/sdk";

// Cap the task itself
export const oneAtATime = task({
  id: "sequential-task",
  concurrency: { total: 1 },
  run: async (payload) => {},
});

// Per tenant (perKey) and overall (total)
export const processUpload = task({
  id: "process-upload",
  concurrency: { perKey: 1, total: 10 },
  run: async (payload) => {},
});
await processUpload.trigger(payload, { concurrencyKey: userId });

// One named limit shared by several tasks (a shared resource such as an external API)
export const openaiLimit = concurrencyLimit({ name: "openai", total: 25 });
export const summarize = task({
  id: "summarize",
  concurrency: [{ total: 5 }, openaiLimit],   // one inline shape + up to two named limits
  run: async (payload) => {},
});

// Switch a run's named limits at trigger time (the inline limit still applies)
await summarize.trigger(payload, { concurrency: ["priority"] });
```

- `total` caps all runs together; `perKey` caps each `concurrencyKey` pool; runs without a key share one pool.
- Named limits: names are 1-122 characters of letters, digits, `_` and `-`. A per-tenant cap across several tasks is `concurrencyLimit({ name: "tenant", perKey: 10 })`.
- Subtasks do not inherit the parent's limits.
- Manage named limits at runtime: `concurrencyLimits.list()`, `.retrieve(name)`, `.override(name, { total: 50 })`, `.reset(name)`, `.pause(name)`, `.resume(name)`. Anonymous inline limits appear as `task/<task-id>`.
- `queues.overrideConcurrencyLimit` / `queues.resetConcurrencyLimit` are deprecated and only work for legacy queues.

On a server older than 4.7.0 the `concurrency` option is accepted but not applied, so keep the queue form there.

## Wait Patterns

### Duration waits

```ts
import { wait } from "@trigger.dev/sdk";

await wait.for({ seconds: 30 });
await wait.for({ minutes: 5 });
await wait.for({ hours: 1 });
await wait.until({ date: new Date("2024-12-25") });
```

> On Trigger.dev Cloud a wait of 60 seconds or longer is checkpointed: it does not consume compute and releases the run's concurrency slots (a shorter wait stays `EXECUTING` and keeps them). **Self-hosted has no checkpoints**: the run stays `EXECUTING` for the whole wait. If you poll in a loop on Cloud, use an interval well above 60 seconds.

### Wait for token (human-in-the-loop)

Create the token first; its `id` starts with `waitpoint_`. Waiting on an arbitrary string does not work.

```ts
const token = await wait.createToken({
  timeout: "10m",          // default 10m
  idempotencyKey: "approval-order-123",   // optional
  tags: ["approval"],                      // optional
});
// token.id, token.url (server-to-server callback), token.publicAccessToken (browser completion)

const result = await wait.forToken<{ approved: boolean }>(token.id);

if (result.ok) {
  console.log("Approved:", result.output.approved);
} else {
  console.log("Token timed out:", result.error);
}

// Or use .unwrap() to throw on timeout:
const approval = await wait.forToken<{ approved: boolean }>(token.id).unwrap();
```

Complete the token via SDK or REST API (`POST /api/v1/waitpoints/tokens/{waitpointId}/complete`):

```ts
import { wait } from "@trigger.dev/sdk";
await wait.completeToken<{ approved: boolean }>(token.id, { approved: true });
```

## Global lifecycle hooks

Register hooks for every task in an `init.ts` file at the root of a directory listed in `dirs` — it is loaded before each run. Do not use the deprecated `onSuccess` / `onFailure` / `onStart` / `init` keys of `defineConfig`.

```ts
// src/trigger/init.ts
import { tasks } from "@trigger.dev/sdk";

tasks.onStartAttempt(({ ctx, payload, task }) => {
  console.log("Starting", ctx.task.id);
});
tasks.onSuccess(({ ctx, payload, output }) => {});
tasks.onFailure(({ ctx, payload, error }) => {});
tasks.onWait(({ ctx, payload, wait, task }) => {});
tasks.onResume(({ ctx, payload, wait, task }) => {});
tasks.middleware("db", async ({ ctx, payload, next, task }) => {
  // open resources, then continue the run
  await next();
});
```

## Trigger Options Reference

| Option | Type | Description |
|--------|------|-------------|
| `delay` | string/datetime | Delay before execution ("5m", "2h", ISO datetime) |
| `tags` | string[] | Up to 10 tags in the SDK (the MCP `trigger_task` accepts 5), each < 128 chars |
| `machine` | string | Machine preset name, for example `"medium-1x"` (an object is not accepted at trigger time; a task definition accepts both) |
| `maxAttempts` | integer | Max retry attempts |
| `maxDuration` | number | Max run duration in seconds |
| `ttl` | string/integer | Time-to-live before auto-cancel (default "10m") |
| `idempotencyKey` | string | Prevent duplicate runs |
| `queue` | string / object | Override queue name (and legacy concurrency) |
| `concurrencyKey` | string | Per-tenant pool for `perKey` limits (server ≥ 4.7.0) |
| `concurrency` | string[] | Replace the task's named limits for this run (server ≥ 4.7.0) |
| `debounce` | object | Debounce config (`key`, `delay`, `mode`, `maxDelay` on server >= 4.4.0) |
