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
// The result is `{ id, runs }`, not an array
const { runs } = await childTask.batchTriggerAndWait([
  { payload: { data: "item1" } },
  { payload: { data: "item2" } },
]);

const succeeded = runs.filter((r) => r.ok).map((r) => r.output);
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
  machine: "medium-1x",   // a string here; the task definition also accepts { preset }
  maxAttempts: 5,
  maxDuration: 300,
  ttl: "30m",
  idempotencyKey: "unique-key",
  queue: { name: "high-priority" },
});
```

## From a Route Handler or Server Action (Next.js)

```ts
// app/api/jobs/enrich/route.ts
import { tasks } from "@trigger.dev/sdk";
import { isAuthorized } from "@/lib/webhook-auth"; // your check: a secret in a header, or the signed-in user
import type { enrichItem } from "@/trigger/enrich-item"; // a type import: no task code in the Next.js bundle

export async function POST(request: Request) {
  // Authenticate the caller first: this public endpoint starts runs, and runs cost money
  if (!(await isAuthorized(request))) return Response.json({ error: "Unauthorized" }, { status: 401 });

  const { keys } = (await request.json()) as { keys: string[] };

  // One request for the whole list (up to 1,000 items); every item has its own idempotency key
  const batch = await tasks.batchTrigger<typeof enrichItem>(
    "enrich-item",
    keys.map((itemId) => ({
      payload: { itemId },
      options: { idempotencyKey: `enrich-${itemId}`, idempotencyKeyTTL: "10m" },
    })),
  );
  return Response.json({ batchId: batch.batchId, runs: batch.runCount });
}
```

- **Authenticate the caller before triggering.** A route handler is a public URL and a Server Action is a public endpoint, and each trigger starts a run. Check a shared secret sent in a header (compare with `timingSafeEqual`, never in the URL) or the signed-in user, and decide which tasks the caller may start. The receiver in the `stack-directus-nextjs-trigger` plugin (`directus-to-trigger`) is a complete example: header secret, `timingSafeEqual`, an allow-list of collections, debounced runs.
- **Import the task as a type.** A value import pulls the task module and everything it imports (AI clients, image libraries) into the framework bundle. `tasks.trigger<typeof enrichItem>("enrich-item", ...)` takes the payload and output types from the type alone. For a single run, `tasks.trigger` returns `handle.id` and `handle.publicAccessToken` (see the **realtime** skill for handing the token to a browser).
- **Make the call inside the handler.** Importing `@trigger.dev/sdk` reads no environment variable. The first API call does, and throws `You need to set the TRIGGER_SECRET_KEY environment variable` when it is missing, so a build that fails with that message is running a trigger at module top level or while prerendering. Move the call into the handler or the Server Action. A `POST` handler and a Server Action are never prerendered.
- **Set `TRIGGER_API_URL` in the environment of the code that triggers.** Without it the SDK falls back to Trigger.dev Cloud and sends your key there, where it is rejected.
- **A key is remembered until its TTL ends.** `enrich-${itemId}` alone refuses every later legitimate run for that item for as long as it is remembered; build the key from the item and a version of it (`updated_at`), or give it a short `idempotencyKeyTTL` as above.
- **Wrap the arrow in an event handler.** `onClick={() => startJob(id)}`, not `onClick={startJob}`: React passes the click event as the first argument.

## Waiting for a Result Outside a Task

`triggerAndWait()` and `tasks.triggerAndSubscribe()` work only inside a running task (the SDK throws `can only be used from inside a task.run()` anywhere else), and there is no `triggerAndPoll`. From backend code that really needs the output, trigger and then poll:

```ts
// lib/run-and-wait.ts: for scripts and admin tools, not for a user-facing request
import { runs, tasks } from "@trigger.dev/sdk";
import type { enrichItem } from "@/trigger/enrich-item";

export async function enrichAndWait(itemId: string) {
  const handle = await tasks.trigger<typeof enrichItem>("enrich-item", { itemId });
  const run = await runs.poll(handle, { pollIntervalMs: 2000 }); // resolves when the run reaches a final status
  if (run.status !== "COMPLETED") throw new Error(`run ${run.id} ended as ${run.status}`);
  return run.output;
}
```

A request that waits for a task defeats the reason to run it as a task. For a user-facing request return `handle.id` and `handle.publicAccessToken` and subscribe in the browser (**realtime** skill).

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
