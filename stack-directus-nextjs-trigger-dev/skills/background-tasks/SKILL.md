---
name: background-tasks
description: This skill should be used when the user wants to "offload work to trigger.dev from next.js", "run background job from a server action", "trigger a task from a route handler", "call tasks.trigger from next.js app router", "delegate slow work to trigger.dev", "show realtime task status in next.js", "fix force-dynamic error with trigger.dev", "handle onclick trigger.dev server action", or needs the integration patterns between Next.js (App Router) and Trigger.dev for event-driven background work.
---

# Background Tasks: Next.js → Trigger.dev

How to delegate slow, flaky, or long-running work from a Next.js App Router application to durable Trigger.dev tasks. This skill covers the integration seam only — for task SDK depth (retries, queues, waits, metadata, Zod), defer to the `trigger-dev` plugin's `task-development` skill.

## When to Offload

Run work inline in a Server Action or Server Component when:
- It finishes in under 500ms
- It's deterministic and rarely fails
- The user is actively waiting for the result

Delegate to a Trigger.dev task when **any** of these apply:

| Signal | Why |
|--------|-----|
| Call to an LLM or AI API | Unpredictable latency (2–60s), rate limits, retries needed |
| Image / video / PDF processing | CPU-heavy, likely >5s |
| Third-party API call that can fail (payment, webhook, email) | Retries + observability are free from Trigger |
| Webhook receiver that does non-trivial work | Return 200 fast so the sender doesn't retry; do the real work async |
| Bulk operation over many records | Batch processing + fan-out |
| Work that must outlive the HTTP request (serverless platforms often have 10–60s limits) | Trigger runs independently |
| Needs idempotency / retries / schedules / observability | Trigger provides all of these |

## Triggering from a Route Handler

The route handler receives an HTTP request, decides to offload, calls `tasks.trigger()`, and returns the run handle immediately.

```typescript
// app/api/process-order/route.ts
import { tasks } from '@trigger.dev/sdk/v3';
import { NextRequest, NextResponse } from 'next/server';
import type { processOrderTask } from '@/trigger/process-order';

// CRITICAL: prevent Next.js from trying to statically generate this route.
// Without this, CI builds fail because TRIGGER_SECRET_KEY isn't available
// at static-generation time — even though the route is obviously dynamic.
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  const body = await request.json();

  const handle = await tasks.trigger<typeof processOrderTask>(
    'process-order',
    { orderId: body.orderId },
    { idempotencyKey: `order-${body.orderId}` }
  );

  return NextResponse.json({
    ok: true,
    runId: handle.id,
    publicAccessToken: handle.publicAccessToken,
  });
}
```

### Why `force-dynamic` is mandatory

Next.js tries to pre-render every route at build time. When it hits a route that calls `tasks.trigger()`, the SDK tries to initialize during the static export — which fails because `TRIGGER_SECRET_KEY` isn't set in the CI build environment. Adding `export const dynamic = 'force-dynamic'` tells Next.js to always render this route at request time, which is correct anyway since every call produces a different run ID.

**Alternative**: `export const runtime = 'nodejs'` forces Node runtime but does NOT prevent static generation — use `force-dynamic` instead.

## Triggering from a Server Action

Server Actions (`'use server'`) are a cleaner way to offload from a form submission or button click. No route handler boilerplate.

```typescript
// app/orders/actions.ts
'use server';

import { tasks } from '@trigger.dev/sdk/v3';
import { revalidatePath } from 'next/cache';
import type { processOrderTask } from '@/trigger/process-order';

export async function submitOrder(orderId: string) {
  const handle = await tasks.trigger<typeof processOrderTask>(
    'process-order',
    { orderId },
    { idempotencyKey: `order-${orderId}` }
  );

  // Optionally: persist the run handle to Directus / DB so the UI can poll it
  // await directus.request(updateItem('orders', orderId, { last_run_id: handle.id }));

  revalidatePath('/orders');
  return { runId: handle.id, publicAccessToken: handle.publicAccessToken };
}
```

Call from a Client Component:

```tsx
'use client';

import { submitOrder } from './actions';

export function OrderButton({ orderId }: { orderId: string }) {
  // CORRECT: wrap in an arrow function — React passes the event as first arg,
  // which would be passed to submitOrder if you did `onClick={submitOrder}`.
  return (
    <button onClick={() => submitOrder(orderId)}>
      Submit Order
    </button>
  );
}
```

**Event handler gotcha** — `onClick={submitOrder}` passes the React event object to `submitOrder(orderId)` as the first arg. Always wrap: `onClick={() => submitOrder(orderId)}`.

## Triggering and Polling

If the caller needs the task result before returning, use `triggerAndPoll` (or `triggerAndWait` from inside another task). **Avoid this in Server Actions** — the HTTP request sits open, defeating the point of offloading.

```typescript
// Prefer this only for internal CLI scripts or admin tools, not user-facing routes.
const result = await tasks.triggerAndPoll<typeof processOrderTask>(
  'process-order',
  { orderId },
  { pollIntervalMs: 2000 }
);
```

For user-facing routes, return the run handle immediately and subscribe via the realtime hook (see below) or poll from the client.

## Fan-Out: Many Tasks at Once

For webhooks that affect multiple items, fan out with `Promise.all`:

```typescript
const handles = await Promise.all(
  itemIds.map((id) =>
    tasks.trigger<typeof enrichItemTask>(
      'enrich-item',
      { itemId: id },
      { idempotencyKey: `enrich-item-${id}` }
    )
  )
);
```

`Promise.all` is safe with `tasks.trigger()` because it just enqueues runs. It is **NOT safe** inside a task with `triggerAndWait()` — use `batchTriggerAndWait` there instead (see `trigger-dev` plugin).

## Importing Task Types

Import the task only as a **type** (not a value) from the triggering side. This keeps the task code out of the Next.js bundle.

```typescript
import type { processOrderTask } from '@/trigger/process-order';
// ✅ Type-only import — no runtime cost, no bundling of task code

// ❌ DON'T do this:
// import { processOrderTask } from '@/trigger/process-order';
// This pulls the task (and all its dependencies — OpenAI, Prisma, etc.) into the Next.js bundle
```

`tasks.trigger<typeof processOrderTask>('process-order', ...)` uses TypeScript's type inference to get the payload/return types without bundling the runtime code.

## Realtime Status in Client Components

After triggering, subscribe to the run with `useRealtimeRun` from `@trigger.dev/react-hooks` to show live progress.

First, the server-side code returns a `publicAccessToken` (scoped to a single run):

```typescript
// in your Server Action or route handler
const handle = await tasks.trigger<typeof processOrderTask>('process-order', { orderId });
return { runId: handle.id, publicAccessToken: handle.publicAccessToken };
```

Then the Client Component subscribes:

```tsx
'use client';

import { TriggerProvider, useRealtimeRun } from '@trigger.dev/react-hooks';

export function OrderStatusProvider({
  runId,
  publicAccessToken,
  children,
}: {
  runId: string;
  publicAccessToken: string;
  children: React.ReactNode;
}) {
  return (
    <TriggerProvider
      accessToken={publicAccessToken}
      apiUrl={process.env.NEXT_PUBLIC_TRIGGER_API_URL!}
    >
      {children}
    </TriggerProvider>
  );
}

export function OrderStatus({ runId }: { runId: string }) {
  const { run, error } = useRealtimeRun(runId);
  if (error) return <p>Error: {error.message}</p>;
  if (!run) return <p>Starting…</p>;
  return (
    <div>
      <p>Status: {run.status}</p>
      <p>Attempt: {run.attemptCount ?? 1}</p>
    </div>
  );
}
```

The public access token is scoped to ONE run and expires when the run finishes — safe to pass to the browser. Do NOT pass `TRIGGER_SECRET_KEY` to the browser.

Add `NEXT_PUBLIC_TRIGGER_API_URL=https://trigger.your-domain.com` to `.env.local` so the Provider can connect from the browser.

## Closing the Loop: Task → Next.js Revalidation

When a task finishes mutating data, it should tell Next.js to invalidate the cached routes that display that data. Two options:

### Option A: Task POSTs to `/api/revalidate`

The task itself fires a request to a Next.js API route that calls `revalidatePath()`.

```typescript
// inside the task's run() function, after writing to Directus
await fetch(
  `${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paths: ['/orders', `/orders/${orderId}`] }),
  }
);
```

The `/api/revalidate` route handler is in the base stack (see `deployment` skill). Accept an array of paths to invalidate and call `revalidatePath()` for each.

### Option B: Directus Flow → `/api/revalidate`

If the task writes to Directus and Directus has a Flow listening for `items.update`, let the Flow POST to `/api/revalidate` directly. Simpler but less control over which specific paths to invalidate.

## Task Env Vars vs Next.js Env Vars

Tasks run **on the Trigger.dev platform**, not on your Next.js hosting. They need their own copy of env vars set in the Trigger.dev dashboard. A `.env.local` variable consumed by Next.js is NOT automatically visible to a task — set it separately in the Trigger dashboard.

Typical task env vars:
- `NEXT_PUBLIC_DIRECTUS_URL`, `DIRECTUS_ADMIN_TOKEN` — for writes back to Directus
- `NEXT_PUBLIC_SITE_URL`, `REVALIDATION_SECRET` — for the revalidation callback
- `OPENAI_API_KEY` or whatever third-party key the task uses

## Anti-Patterns

| Don't | Do |
|-------|-----|
| `await triggerAndPoll` in a user-facing Server Action | Return `runId` + subscribe with `useRealtimeRun` |
| `import { myTask }` from Next.js | `import type { myTask }` |
| `onClick={myFormAction}` | `onClick={() => myFormAction(arg)}` |
| Skip `force-dynamic` on route handlers that call `tasks.trigger()` | Always add it |
| Pass `TRIGGER_SECRET_KEY` to client code | Pass only the scoped `publicAccessToken` per run |
| Retry failed triggers in a loop inside the route handler | Let Trigger's `retry` config handle it — keep the route handler thin |
| Forget to set env vars in the Trigger.dev dashboard | Set them per environment (dev/staging/prod) in the Trigger.dev dashboard |

## Examples

<example>
User: "I need a Server Action that transcodes an uploaded video — can I just await ffmpeg in the action?"
Response: "Video transcoding is exactly the kind of work to offload — FFmpeg can take minutes, and serverless Server Actions typically time out at 10-60s. Create a Trigger.dev task `transcode-video` that does the FFmpeg work, then have the Server Action call `tasks.trigger<typeof transcodeVideoTask>('transcode-video', { fileId })` and return the run ID. Show progress in a Client Component with `useRealtimeRun`. Remember to `import type` the task, not the runtime code — otherwise FFmpeg pulls into the Next.js bundle."
</example>

<example>
User: "My CI build fails with 'TRIGGER_SECRET_KEY is required' on a route that calls `tasks.trigger()`. What's wrong?"
Response: "Next.js is trying to statically generate the route at build time, which initializes the Trigger SDK before env vars are bound. Add `export const dynamic = 'force-dynamic'` at the top of the route file. This tells Next.js to render the route per request — which is correct since each call produces a new run."
</example>

<example>
User: "I want to show the task status live in the browser after kicking it off. How?"
Response: "On the server, after `tasks.trigger()`, return `{ runId: handle.id, publicAccessToken: handle.publicAccessToken }` to the client. Wrap your Client Component in `<TriggerProvider accessToken={publicAccessToken} apiUrl={process.env.NEXT_PUBLIC_TRIGGER_API_URL}>`, then use `useRealtimeRun(runId)` from `@trigger.dev/react-hooks`. The public access token is scoped to one run and expires automatically — safe to ship to the browser."
</example>
