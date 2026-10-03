---
name: directus-to-trigger
description: This skill should be used when the user wants to "trigger a task from a directus flow", "run a background task when a directus item is created or updated", "forward directus webhooks to trigger.dev", "process directus items asynchronously", "build a directus flow to next.js to trigger pipeline", "have a task write back to directus", "stop a directus flow and task from looping", "read and write directus from a trigger.dev task", or needs the pattern for wiring Directus Flow events through Next.js into Trigger.dev tasks and back.
---

# Directus to Trigger.dev: The Event-Driven Pipeline

An editor saves an item in Directus, a task works on it, and the result lands in Directus and on the page. This is the most common pipeline of the stack and it has three hand-offs: Flow to Next.js, Next.js to task, task back to Directus and the site. This skill owns them. The Flow's own settings are taught by `directus-dev` → `flow-automation` (`references/send-items-to-a-worker.md`); the task API by `trigger-dev`.

```
editor creates or edits an item
  -> Directus Flow (event, action): condition "a source field changed" -> request operation
  -> POST /api/directus-webhook/<collection>    header x-webhook-secret, body {event, collection, keys}
  -> Next.js receiver: check the secret and the collection, start one debounced task per key, answer 200
  -> Trigger.dev task: read the item, skip if already done, do the work, write the result to Directus
  -> the revalidation Flow (or the task) expires the cache tag -> the next visitor gets the fresh page
```

Each arrow has its own authentication and failure story, so each is checked separately below.

## 1. The Flow

Create it through the Directus MCP `flows` and `operations` tools, or in Settings → Flows. The settings are in `directus-dev` → `flow-automation` → `references/send-items-to-a-worker.md`; what this stack fixes:

| Setting | Value |
|---------|-------|
| Trigger | Event hook, type **action** (runs after the commit), scope `items.create` and `items.update`, the collection the task works on |
| Condition | Filter rules requiring a **source** field in `$trigger.payload`: a field an editor changes and the task only reads (`body`). The fields the task writes never appear in that list, so its write-back does not restart the Flow |
| Request | `POST https://<app>/api/directus-webhook/<collection>`, header `x-webhook-secret` = `{{ $env.DIRECTUS_WEBHOOK_SECRET }}`, body with `event`, `collection` and `keys` |
| Directus container | `DIRECTUS_WEBHOOK_SECRET` set, and named in `FLOWS_ENV_ALLOW_LIST` (without it the template renders `undefined` and the receiver answers `401`) |

Use **Action**, not Filter: a slow or failed call must not block an editor's save, and the Flow must not run before the item exists. The secret is not `REVALIDATION_SECRET`: a leaked revalidation secret expires a cache, a leaked job secret starts paid work with ids of the attacker's choosing.

## 2. The Receiver

A Route Handler that proves the call comes from your Flow, checks which tasks a Flow may start, starts them and answers at once. It owns no business logic.

```typescript
// app/api/directus-webhook/[collection]/route.ts
import { timingSafeEqual } from 'node:crypto';
import { tasks } from '@trigger.dev/sdk';
import type { enrichArticle } from '@/trigger/enrich-article'; // a type import: no task code in the Next.js bundle

function secretMatches(received: string | null): boolean {
  const expected = process.env.DIRECTUS_WEBHOOK_SECRET;
  if (!expected || !received) return false;
  const a = Buffer.from(received);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function POST(request: Request, { params }: { params: Promise<{ collection: string }> }) {
  if (!secretMatches(request.headers.get('x-webhook-secret'))) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { collection } = await params;
  const body = (await request.json().catch(() => null)) as { keys?: unknown } | null;
  // Directus always sends an array, also for one item; keys are strings (UUID) or numbers (integer ids)
  const keys = (Array.isArray(body?.keys) ? body.keys : []).filter(
    (key): key is string | number => typeof key === 'string' || typeof key === 'number',
  );
  if (keys.length === 0) return Response.json({ error: 'No keys' }, { status: 400 });

  switch (collection) {
    case 'articles':
      await Promise.all(
        keys.map((key) =>
          tasks.trigger<typeof enrichArticle>(
            'enrich-article',
            { itemId: String(key) },
            // Editors save the same item again and again: collapse a burst into one run on the latest state.
            // maxDelay makes sure the run starts even while saves keep coming.
            { debounce: { key: `enrich-article-${key}`, delay: '15s', maxDelay: '2m', mode: 'trailing' } },
          ),
        ),
      );
      break;
    default:
      return Response.json({ error: 'Unknown collection' }, { status: 400 }); // the allow-list of what a Flow may start
  }

  return Response.json({ started: keys.length });
}
```

- **One `case` per collection**, so each call keeps its own payload type, and an unknown collection is refused. The route is public: the secret check and this allow-list are the whole defence.
- **Debounce, not an idempotency key.** Directus sends each save once and does not retry a failed call (`send-items-to-a-worker.md`), so duplicates come from editors saving repeatedly. `debounce` collapses a burst into one run on the latest state (`mode: 'trailing'`; keep `delay` well below `maxDelay`, which needs server 4.4.0 or later, or the trigger is rejected: `trigger-dev` → `task-development` → `references/advanced-tasks.md`); an idempotency key built from the item id would block every later edit for as long as the key is remembered, and a key takes precedence over a debounce key. A save that arrives while the run is executing starts a new run, so two runs for one item can overlap: the work must be safe to run twice.
- **The payload is ids.** The task reads the current record. An event can carry many keys at once (a bulk edit); for a bulk import that changes thousands of items, start one task that reads the range and fans out, not one run per key.
- **Answer fast.** The Flow waits for the response; the task does the slow part.
- Starting a run needs `TRIGGER_SECRET_KEY` and `TRIGGER_API_URL` in the Next.js environment (`background-tasks`).

## 3. The Task Side: Its Own Directus Client

A task builds its client from its own environment. It does not import `lib/directus.ts`, which has `import 'server-only'` and the Next.js server's token. Two helpers hold what every task needs:

```typescript
// trigger/lib/directus.ts: the task-side Directus client (no 'server-only': that package throws outside Next.js)
import { AbortTaskRunError } from '@trigger.dev/sdk';
import { createDirectus, rest, staticToken } from '@directus/sdk';
import type { Schema } from '@/types/directus';

/** A variable of the Trigger.dev environment of this run. A missing one is not fixed by retrying. */
export function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new AbortTaskRunError(`${name} is not set in the Trigger.dev environment of this run`);
  return value;
}

/** Created on first use: deploy imports the task files while the image is built, and the run's variables do not exist then. */
export function getDirectus() {
  return createDirectus<Schema>(requireEnv('DIRECTUS_URL'))
    .with(staticToken(requireEnv('DIRECTUS_TOKEN')))
    .with(rest());
}
```

`requireEnv` replaces the symptom `TypeError: Failed to parse URL from undefined/...` with the name of the variable that is missing. `DIRECTUS_TOKEN` here is the **task user's** token, set in the Trigger.dev project (`deployment`); `Schema` is the same `types/directus.ts` as the app's, so a renamed field fails `tsc` in both places.

The task itself (the part that is yours) is in the AI Enrichment scenario of `examples`. The rules that hold for every task of this pipeline:

- **Read the record, do not trust the payload.** The payload says which item; the item says what to do. An update's trigger payload held only the fields that one save changed anyway.
- **Skip what is done.** Keep a hash (or a version) of the source on the item and compare it first. A second delivery, a replay from the dashboard and a write-back that slipped past the Flow's condition then cost one read. A *regenerate* button passes `force` to bypass the check.
- **Mark the state on the item.** `processing_status` (`pending`, `processing`, `done`, `failed`) lets the page show it; `onFailure`, which runs once after the last retry, writes `failed`. Writes of the task must not include the source field.
- **Few retries for paid work.** Each retry of an AI call is paid; `retry: { maxAttempts: 2 }` and a `maxDuration`.
- **Treat model output as untrusted text.** Store it, and render it as text, never as HTML.

## Fresh Pages After the Task Wrote

The revalidation Flow already fires for the task's writes when it lists the collection, so the page refreshes without a line in the task (`background-tasks` → "Closing the Loop"). When the task has to call the route itself, because the collection is not in the Flow or the data never passes through Directus items, use one helper, with the secret in a header and its own retry so a failed call does not repeat the paid work:

```typescript
// trigger/lib/revalidate.ts: for tasks that call the site themselves
import { retry } from '@trigger.dev/sdk';
import { requireEnv } from './directus';

/** Expire the cache tag of a collection. Retries the call alone, not the task. */
export async function revalidateSite(collection: string): Promise<void> {
  const site = requireEnv('NEXT_PUBLIC_SITE_URL');
  const secret = requireEnv('REVALIDATION_SECRET');
  await retry.onThrow(
    async () => {
      const res = await fetch(`${site}/api/revalidate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-revalidate-secret': secret },
        body: JSON.stringify({ collection }),
        signal: AbortSignal.timeout(10_000),
      });
      if (!res.ok) throw new Error(`revalidate ${collection}: ${res.status}`); // fetch does not throw on a 4xx
    },
    { maxAttempts: 3 },
  );
}
```

## Scheduled Jobs That Write to Directus

A scheduled task (`trigger-dev` → `scheduled-tasks`) uses the same client and the same two ways to refresh the page. Two things belong to this stack. **Write idempotently**: Directus has no upsert, so read the existing rows first and update or create, with a unique index on the natural key so a race fails loudly instead of duplicating (the Scheduled Data Sync scenario). **Refresh once**, after the batch, not once per item, when the task calls the route itself. The scenario shows both.

## Error Routing

When a task fails after its last retry:

- **In Directus**, the Flow already ended: the receiver answered `200`, so the Flow log says success. That is expected: a broken task must not block editors.
- **In Trigger.dev**, the run shows as failed with the full trace; configure alerts on failed runs in the project.
- **In your data**, `onFailure` sets `processing_status: 'failed'`, so the page and the editors see it.

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Import `lib/directus.ts` in a task | `getDirectus()` from `trigger/lib/directus.ts`, built from the task's environment |
| Put the secret in the Flow URL (`?secret=`) | The `x-webhook-secret` header, read from `$env` through `FLOWS_ENV_ALLOW_LIST` |
| Reuse `REVALIDATION_SECRET` for the receiver | A separate `DIRECTUS_WEBHOOK_SECRET` |
| Compare secrets with `===` | `timingSafeEqual` on equal-length buffers |
| Compute an HMAC in a Run Script operation | Not possible there (no `crypto`): header secret over HTTPS, or a custom operation |
| Let the task write the field the Flow's condition watches | The condition watches source fields; the task writes result fields |
| An idempotency key built from the item id alone, for editor saves | `debounce` on the item id, and a source hash check in the task |
| A run per key for a bulk import | One task that reads the range and fans out under a queue (`trigger-dev` → `task-development` → `references/record-driven-tasks.md`) |
| A user's token in the payload | Ids; the task's own token |

## Examples

<example>
User: "When a user uploads a receipt, run OCR and categorization in the background and update the receipt."
Response: "Create a Flow on `items.create` for `receipts` (action), with a condition that the `file` field is in the payload, and a request operation to `/api/directus-webhook/receipts` with the `x-webhook-secret` header. Add a `receipts` case to the receiver that starts a `process-receipt` task with the item id. The task builds its client with `getDirectus()`, reads the receipt, runs OCR, writes `ocr_text`, `amount`, `category` and `processing_status: 'done'`, and sets `failed` in `onFailure`. It never writes `file`, so its own update does not restart the Flow. Add `receipts` to the revalidation Flow and to `COLLECTION_TAGS` so the list page refreshes."
</example>

<example>
User: "My Directus Flow keeps firing the enrichment task in a loop: the task writes `ai_summary`, which triggers `items.update`, which fires the webhook again."
Response: "Add a condition operation before the request, with filter rules that require the source field: `{ \"$trigger\": { \"payload\": { \"body\": { \"_nnull\": true } } } }`. On `items.update` the payload holds only the fields that save changed, so the task's write (`ai_summary`, `processing_status`, ...) fails the condition and the Flow ends. Also keep a hash of the source on the item and return early in the task when it matches: the condition stops the loop, the hash makes a repeated delivery cheap."
</example>

<example>
User: "The receiver answers 401 but my secret is right."
Response: "Check `FLOWS_ENV_ALLOW_LIST` on the Directus container: without the secret's name in it, `{{ $env.DIRECTUS_WEBHOOK_SECRET }}` renders as the text `undefined` and the header carries that. Then check that the receiver reads `x-webhook-secret` (a header, not the query string) and that the host environment holds the same value as the Directus container. Add a `log` operation on the request operation's reject path so the next failure is visible in the Directus logs."
</example>
