---
name: directus-to-trigger
description: This skill should be used when the user wants to "trigger a task from a directus flow", "run a background task when a directus item is created or updated", "forward directus webhooks to trigger.dev", "process directus items asynchronously", "build a directus automate → next.js → trigger pipeline", "have a task write back to directus after processing", or needs the pattern for wiring Directus Flow events through Next.js into Trigger.dev tasks and back.
---

# Directus → Trigger: Event-Driven Pipeline

How to kick off a Trigger.dev task whenever a Directus item changes, and how the task writes results back to Directus and refreshes the Next.js cache. This is the most common integration pattern on this stack — creating an item triggers enrichment, and the user sees the enriched result without refreshing.

## The Full Flow

```
Editor creates/updates item in Directus
    ↓
Directus Flow (Event Hook: items.create / items.update)
    ↓
POST https://yourdomain.com/api/directus-webhook/{collection}?secret=...
    ↓
Next.js route handler (force-dynamic)
  - verify shared secret
  - tasks.trigger<typeof myTask>("my-task", { itemId }, { idempotencyKey })
  - return 200 immediately
    ↓
Trigger.dev runs myTask durably:
  - build Directus SDK client inside task
  - fetch item
  - do the slow/flaky work (AI, API, image, etc.)
  - updateItem() results back to Directus
  - POST /api/revalidate
    ↓
Next.js ISR cache invalidated → users see fresh content
```

Each arrow is a boundary with its own auth/retry story. This skill covers all of them.

## Step 1: Create the Directus Flow

Directus → Settings → Flows → Create Flow

- **Name**: descriptive, e.g. `Articles — Enrich on Save`
- **Trigger Type**: **Event Hook**
- **Scope**: `items.create` and/or `items.update`
- **Collection**: the target collection (e.g. `articles`)
- **Response Body**: `$last` — so Directus waits for the webhook before continuing (Action type) OR ignore response (fire-and-forget)
- **Operation**: Webhook
  - **Method**: POST
  - **URL**: `https://yourdomain.com/api/directus-webhook/articles?secret={{ $env.REVALIDATION_SECRET }}`
  - **Headers**: `Content-Type: application/json`
  - **Body**:
    ```json
    {
      "event": "{{ $trigger.event }}",
      "collection": "{{ $trigger.collection }}",
      "keys": {{ $trigger.keys }}
    }
    ```

Save `REVALIDATION_SECRET` in Directus Settings → Environment Variables so `{{ $env.REVALIDATION_SECRET }}` interpolates correctly. Alternatively, hardcode the secret in the Flow URL — but env-var is cleaner for rotation.

**Filter vs Action**: Directus Flows run as either Filters (blocking, before save) or Actions (after save). Use **Action** for webhook triggers — you don't want a slow HTTP call blocking content editors, and a failed webhook should not prevent saves.

**`{{ $trigger.keys }}` is an array** — even for a single-item create/update, Directus sends an array of primary keys. Handle the array shape on the receiver.

## Step 2: Next.js Webhook Receiver

Create `app/api/directus-webhook/[collection]/route.ts` (or a specific route per collection for stricter typing).

```typescript
// app/api/directus-webhook/articles/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { tasks } from '@trigger.dev/sdk/v3';
import type { enrichArticleTask } from '@/trigger/enrich-article';

export const dynamic = 'force-dynamic';

interface DirectusWebhookPayload {
  event: string;
  collection: string;
  keys: string[];
}

export async function POST(request: NextRequest) {
  // 1. Verify the shared secret
  const secret = request.nextUrl.searchParams.get('secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 2. Parse payload
  let body: DirectusWebhookPayload;
  try {
    body = (await request.json()) as DirectusWebhookPayload;
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  if (!Array.isArray(body.keys) || body.keys.length === 0) {
    return NextResponse.json({ error: 'No keys in payload' }, { status: 400 });
  }

  // 3. Fan out — one task per affected item
  const handles = await Promise.all(
    body.keys.map((itemId) =>
      tasks.trigger<typeof enrichArticleTask>(
        'enrich-article',
        { itemId, event: body.event },
        {
          // Idempotent by item ID + event — retries of the same webhook
          // map to the same run, not a duplicate.
          idempotencyKey: `enrich-article-${itemId}-${body.event}`,
        }
      )
    )
  );

  // 4. Return fast so Directus doesn't timeout and retry
  return NextResponse.json({
    ok: true,
    triggered: handles.length,
    runIds: handles.map((h) => h.id),
  });
}
```

### Why `force-dynamic`

Without it, Next.js tries to statically generate this route at build time, which fails because `TRIGGER_SECRET_KEY` isn't bound in CI. Always add it to routes that call `tasks.trigger()`. (See `background-tasks` skill for the full explanation.)

### Why `idempotencyKey` keyed on item ID + event

Directus can retry the webhook if it doesn't get a 200 response quickly (and Flows have their own retry mechanism). Without an idempotency key, a retry spawns a **duplicate task run** that enriches the same article twice — wasting API calls and producing non-deterministic results. With the key, Trigger returns the existing run instead.

Include the event type in the key (`create` vs `update`) so legitimate consecutive edits still trigger new runs.

### HMAC Signature (Optional, More Secure)

If you're worried about secret leakage via URL query params (they show up in Next.js access logs), compute an HMAC signature in the Flow and verify it in the route handler:

```typescript
import crypto from 'node:crypto';

const signature = request.headers.get('x-directus-signature');
const rawBody = await request.text();
const expected = crypto
  .createHmac('sha256', process.env.REVALIDATION_SECRET!)
  .update(rawBody)
  .digest('hex');

if (signature !== expected) {
  return NextResponse.json({ error: 'Invalid signature' }, { status: 401 });
}

const body = JSON.parse(rawBody);
```

Set the `x-directus-signature` header in the Flow using a Script operation that computes the HMAC over the same body JSON. This is stricter than the URL-param approach — use it when the webhook endpoint is on the public internet.

## Step 3: The Trigger.dev Task

Build the Directus SDK client **inside** the task's `run` function. Do NOT import `lib/directus.ts` — it has `'server-only'` which throws outside a Next.js runtime.

```typescript
// trigger/enrich-article.ts
import { task, logger } from '@trigger.dev/sdk/v3';
import { createDirectus, rest, staticToken, readItem, updateItem } from '@directus/sdk';
import type { Schema } from '@/types/directus';

export const enrichArticleTask = task({
  id: 'enrich-article',
  maxDuration: 300, // 5 min
  retry: {
    maxAttempts: 3,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 30000,
  },
  run: async (payload: { itemId: string; event: string }, { ctx }) => {
    // 1. Build the Directus client
    const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
      .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
      .with(rest({ cache: 'no-store' }));

    // 2. Mark as processing + record the run ID so the admin UI can subscribe
    await directus.request(
      updateItem('articles', payload.itemId, {
        processing_status: 'processing',
        last_run_id: ctx.run.id,
      })
    );

    // 3. Fetch the item
    const article = await directus.request(
      readItem('articles', payload.itemId, {
        fields: ['id', 'title', 'body'],
      })
    );

    // 4. Do the slow work
    const enriched = await enrichContent(article);

    // 5. Write results back
    await directus.request(
      updateItem('articles', payload.itemId, {
        ai_summary: enriched.summary,
        ai_tags: enriched.tags,
        processing_status: 'done',
        ai_enriched_at: new Date().toISOString(),
      })
    );

    // 6. Revalidate the Next.js ISR cache
    await fetch(
      `${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          paths: [`/articles/${article.slug ?? payload.itemId}`, '/articles'],
        }),
      }
    );

    logger.log('Article enriched', { itemId: payload.itemId });
    return { itemId: payload.itemId, ...enriched };
  },
  catchError: async ({ payload, error, retry }) => {
    // Final failure: mark item as failed
    if (retry.attempt >= 3) {
      const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
        .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
        .with(rest({ cache: 'no-store' }));
      await directus.request(
        updateItem('articles', (payload as { itemId: string }).itemId, {
          processing_status: 'failed',
        })
      );
    }
    throw error; // re-throw so Trigger records the failure
  },
});

async function enrichContent(article: { title: string; body: string }) {
  // Replace with the actual work (LLM call, etc.)
  return { summary: '', tags: [] as string[] };
}
```

## Auth Choices for the Task's Directus Client

| Approach | When to use |
|----------|------------|
| Task-scoped static admin token (`DIRECTUS_ADMIN_TOKEN`) set in the Trigger dashboard | Default — simplest. Use a token with minimum-needed permissions, not full admin. |
| Per-user token passed in the task payload | When the task must act **as the user** who initiated it (e.g. user-scoped access). Pass the token in the payload, build the client with `staticToken(payload.userToken)`. Never log the token. |
| Service role + JWT exchange | When tasks run long enough (hours) that a static token might rotate — call `/auth/login` inside the task to get a fresh JWT. Complex; prefer static tokens if the token has a long lifetime. |

**Always** use dedicated task env vars in the Trigger.dev dashboard — don't assume the Next.js app's env vars are visible. Set `NEXT_PUBLIC_DIRECTUS_URL`, `DIRECTUS_ADMIN_TOKEN`, `NEXT_PUBLIC_SITE_URL`, and `REVALIDATION_SECRET` per environment.

## Error Routing

When a task fails after max retries:

- **In Directus**: the Flow already returned 200 (because the webhook returned 200 fast). The Flow run log shows "success". This is expected — webhooks are fire-and-forget.
- **In Trigger.dev**: the task shows as Failed in the dashboard with full error traces.
- **In your data**: the `catchError` hook marks `processing_status: 'failed'` so the UI can show the error state.
- **Alerts**: configure Trigger.dev dashboard alerts (email, Slack) to notify on failed runs.

This split is a feature — you don't want a broken enrichment task to block editors from saving content.

## Avoiding Loops

Watch out for this footgun: your task updates the item → Directus fires `items.update` again → webhook triggers another task → infinite loop.

Prevent it by **filtering in the Flow** to only fire when certain fields change:

```
Condition (Flow operation between trigger and webhook):
  {{ $trigger.payload.body }} != null
  AND {{ $trigger.payload.ai_summary }} == null
```

Or skip fields written by the task (`ai_summary`, `ai_tags`, `processing_status`, `last_run_id`, `ai_enriched_at`) in the Flow's `payload` — Directus Flows can be configured to only listen to specific field changes.

Alternatively, check inside the task and return early:

```typescript
const article = await directus.request(readItem('articles', payload.itemId, { fields: ['*'] }));
if (article.ai_summary && article.ai_enriched_at) {
  logger.log('Already enriched — skipping');
  return { skipped: true };
}
```

## Multi-Collection Webhook

If many collections need similar processing, use a catch-all route:

```typescript
// app/api/directus-webhook/[collection]/route.ts
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ collection: string }> }
) {
  const { collection } = await params;
  // ... verify secret, parse body ...

  const taskId = {
    articles: 'enrich-article',
    products: 'enrich-product',
    users: 'onboard-user',
  }[collection];

  if (!taskId) {
    return NextResponse.json({ error: 'No handler for collection' }, { status: 400 });
  }

  const handles = await Promise.all(
    body.keys.map((itemId) =>
      tasks.trigger(taskId, { itemId }, { idempotencyKey: `${taskId}-${itemId}-${body.event}` })
    )
  );

  return NextResponse.json({ ok: true, triggered: handles.length });
}
```

Point Directus Flows at `/api/directus-webhook/articles`, `/api/directus-webhook/products`, etc. — the route parameter picks the right task.

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Import `lib/directus.ts` in the task file | Build a fresh `createDirectus(...)` client inside `run()` — the lib singleton has `'server-only'` which throws |
| Skip the idempotency key | Always pass `idempotencyKey: \`{task-id}-{item-id}-{event}\`` — Directus retries webhooks on timeout |
| Block the webhook response waiting for the task to finish | Return 200 immediately after `tasks.trigger()`; use `useRealtimeRun` in the UI for status |
| Let tasks write to the same fields the Flow watches | Add a Flow condition OR check inside the task — otherwise you'll create an infinite loop |
| Use the same webhook secret as your Next.js `REVALIDATION_SECRET` without rotating | Fine to share — but rotate both together if either leaks |
| Forget to set task env vars in the Trigger dashboard | The task runs on Trigger.dev's platform, NOT Next.js — set env vars in the Trigger project separately |

## Examples

<example>
User: "When a user uploads a receipt in my app, I want OCR + categorization to run in the background, then update the receipt record. How do I wire it?"
Response: "Create a Directus Flow on `items.create` for the `receipts` collection, Action type, webhook to `/api/directus-webhook/receipts?secret=...`. The Next.js route handler calls `tasks.trigger<typeof processReceiptTask>('process-receipt', { itemId }, { idempotencyKey: \`process-receipt-${itemId}-create\` })` and returns 200 immediately. The task builds a Directus client inside `run()`, fetches the file ID from the receipt, calls the OCR API, writes back `ocr_text`, `amount`, `category`, `processing_status: 'done'`. In `catchError` on final failure, mark `processing_status: 'failed'`. POST to `/api/revalidate` at the end so the user's receipt list page shows the result. In the UI, subscribe with `useRealtimeRun(lastRunId)` for live progress."
</example>

<example>
User: "My Directus Flow keeps firing my enrichment task in a loop. The task writes `ai_summary`, which triggers `items.update`, which re-fires the webhook."
Response: "Add a Flow condition that checks `{{ $trigger.payload.ai_summary }} == null` — the Flow fires only when ai_summary is empty. Alternatively, check inside the task: `if (article.ai_summary) return { skipped: true };`. The most robust fix is both — belt and suspenders. You can also configure the Flow to listen to specific field changes instead of all updates."
</example>

<example>
User: "The webhook route is returning 401 but my secret is correct. What's wrong?"
Response: "Three common causes: (1) The Directus Flow's `{{ $env.REVALIDATION_SECRET }}` interpolation isn't set — check Directus Settings → Environment Variables and confirm `REVALIDATION_SECRET` is there. (2) The secret in `.env.local` / your hosting platform doesn't match Directus. (3) You're using URL-encoded characters that aren't decoding — use `request.nextUrl.searchParams.get('secret')` which decodes automatically. If logging the received secret shows `null`, the query string isn't being sent at all — check the Flow's URL field."
</example>
