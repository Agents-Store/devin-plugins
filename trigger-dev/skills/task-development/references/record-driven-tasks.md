# Record-Driven Tasks

Patterns for tasks that process records held in an external system of record — a database table, NocoDB, NocoBase, a PostgreSQL schema behind PostgREST. The trigger arrives from outside (a webhook, a workflow, a button, a schedule), the task does the long work, and the record carries the job status. SDK 4.x, `@trigger.dev/sdk`.

All snippets type-check against `@trigger.dev/sdk` 4.7.2 (`tsc --strict`).

## Payload: ids, not copies

Put the record id (and the table or collection) in the payload and read the record inside the task. A payload is a snapshot; the record may change before the run starts, and a large payload is stored with every run and retry.

```ts
type RecordPayload = { recordId: number; tableId: string };
```

Give the task a descriptive, stable id (`process-order-payment`, `generate-ai-summary`) — the id is what the webhook, the workflow and the MCP `trigger_task` call name.

## Status lifecycle

Keep a status field on the record (`pending` → `processing` → `completed` / `failed`). Set `processing` at the start of `run`, `completed` at the end, and `failed` in `onFailure`, which runs once the retries are used up:

```ts
import { task, queue, logger, AbortTaskRunError } from "@trigger.dev/sdk";

async function setStatus(recordId: number, status: string, detail?: string): Promise<void> {
  const res = await fetch(`${process.env.RECORDS_API_URL}/records/${recordId}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${process.env.RECORDS_API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ job_status: status, job_detail: detail ?? null }),
  });
  if (!res.ok) throw new Error(`status update failed: ${res.status}`);
}

// Declare the queue up front — the queue is shared by every run of the task
// (SDK 4.7 deprecates `concurrencyLimit` in favour of `concurrency`, which needs server >= 4.7.0 —
// see "Concurrency & Queues" in task-development/SKILL.md)
const recordQueue = queue({ name: "record-processing", concurrencyLimit: 5 });

export const processRecord = task({
  id: "process-record",
  queue: recordQueue,
  retry: { maxAttempts: 3 },
  onFailure: async ({ payload, error }) => {
    await setStatus(payload.recordId, "failed", String(error));
  },
  run: async (payload: RecordPayload) => {
    await setStatus(payload.recordId, "processing");
    logger.info("processing record", { recordId: payload.recordId });
    // 1. Read the record  2. Do the work  3. Write the result back
    // Throw AbortTaskRunError for a record that can never succeed — no retry
    await setStatus(payload.recordId, "completed");
    return { recordId: payload.recordId };
  },
});
```

A status write is a network call: `fetch` does not throw on a `4xx`, so check `res.ok`. A deployed task only sees the environment variables synced to its Trigger.dev environment — see **config-and-build** (`syncEnvVars`).

## No duplicate runs

Webhooks and workflows can fire twice for one change. Key the run on the record, and on a version of it if a second run is legitimate after a later change:

```ts
import { idempotencyKeys } from "@trigger.dev/sdk";

const key = await idempotencyKeys.create(`record-${tableId}-${recordId}-v${version}`);
await processRecord.trigger({ recordId, tableId }, { idempotencyKey: key, idempotencyKeyTTL: "1h" });
```

Over HTTP the same thing is `options.idempotencyKey` (and `idempotencyKeyTTL`) in the request body — see **mcp-patterns**, *REST Management API*.

## Many records: one child run per record

Loop inside one run only when the work per record is tiny. Otherwise fan out, so each record gets its own retries, status and trace, and the queue limits how many run at once. Never wrap `triggerAndWait` in `Promise.all` — use `batchTriggerAndWait`:

```ts
export const processRecords = task({
  id: "process-records",
  run: async (payload: { tableId: string; recordIds: number[] }) => {
    // The result is { id, runs }; every run carries `ok`
    const { runs } = await processRecord.batchTriggerAndWait(
      payload.recordIds.map((recordId) => ({
        payload: { recordId, tableId: payload.tableId },
        options: { idempotencyKey: `record-${payload.tableId}-${recordId}` },
      }))
    );
    return {
      succeeded: runs.filter((r) => r.ok).length,
      failed: runs.filter((r) => !r.ok).length,
    };
  },
});
```

A single batch holds up to 1,000 items; split a longer list. See `references/triggering-patterns.md`.

## AI processing of a record

Long model calls need a bigger machine, a hard time limit and fewer retries (each retry is paid for):

```ts
export const aiProcessRecord = task({
  id: "ai-process-record",
  machine: "medium-1x",
  maxDuration: 600,
  retry: { maxAttempts: 2 },
  run: async (payload: RecordPayload) => {
    // 1. Read the record  2. Call the model (create the client lazily — see Critical Rules)
    // 3. Write the result back  4. Set the status
  },
});
```

For token streaming and chat-style agents see **ai-agent-patterns**.

## Triggering from outside

| From | How |
|------|-----|
| A workflow tool (n8n, a webhook relay) | `POST ${TRIGGER_API_URL}/api/v1/tasks/<taskId>/trigger` with `Authorization: Bearer ${TRIGGER_SECRET_KEY}` and body `{"payload": {...}, "options": {...}}` — **mcp-patterns**, *REST Management API* |
| Backend code | `tasks.trigger<typeof processRecord>("process-record", payload)` — `references/triggering-patterns.md` |
| An agent | the MCP `trigger_task` tool, then `list_runs` / `get_run_details` — **mcp-patterns**, *Trigger and Monitor* |

In n8n 2.x use an **HTTP Request** node with a Header Auth credential for the secret key, not a Code node reading `process.env` — n8n blocks environment access from Code nodes and expressions by default.

## Checklist

- Record id and table in every payload; the status field on the record
- `onFailure` writes `failed`; retries and `AbortTaskRunError` decide what is retried
- Idempotency key built from the record id (and version)
- A queue with `concurrencyLimit` for anything that calls a rate-limited API
- `batchTriggerAndWait` for fan-out, never `Promise.all` over `triggerAndWait`
