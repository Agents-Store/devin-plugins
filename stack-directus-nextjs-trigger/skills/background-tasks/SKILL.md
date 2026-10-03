---
name: background-tasks
description: This skill should be used when the user wants to "offload work to trigger.dev from next.js", "run a background job from a server action", "trigger a task from a route handler", "delegate slow work to trigger.dev", "decide what runs in a Server Action and what in a task", "show a task's progress in next.js", "give the browser a token for a trigger.dev run", "keep task environment variables apart from next.js", "fix a TRIGGER_SECRET_KEY build error", or needs the rules where a Next.js App Router app hands work to Trigger.dev and gets the result back.
---

# Background Tasks: The Next.js and Trigger.dev Boundary

Slow, flaky or long work leaves Next.js and runs as a durable Trigger.dev task: it retries, it is observable, and it outlives the HTTP request. This skill owns the boundary only: what is offloaded, what crosses, who holds which credential, where the environment variables live. The SDK itself is taught by `trigger-dev`: starting runs from a route handler or Server Action, batches and idempotency in `task-development` (`references/triggering-patterns.md`); tokens and hooks for the browser in `realtime`; tasks, retries and queues in `task-development`.

## When to Offload

Run work inline in a Server Action or Server Component when it finishes in under half a second, is deterministic and rarely fails, and the user is waiting for the result. Delegate to a task when any of these apply:

| Signal | Why |
|--------|-----|
| A call to an LLM or AI API | Latency of 2 to 60 seconds, rate limits, retries needed |
| Image, video or PDF processing | CPU heavy, likely longer than 5 seconds |
| A third-party call that can fail (payment, email, webhook) | Retries and a trace per run come with the task |
| A webhook receiver that does real work | Answer `200` fast and work asynchronously, so the sender does not retry |
| A bulk operation over many records | Fan-out, with its own retry and status per record |
| Work that must outlive the request (serverless limits are 10 to 60 seconds) | A task runs on its own workers |
| Work on a schedule | `schedules.task` (`trigger-dev` → `scheduled-tasks`) |

An HTTP call on a schedule with no logic of your own does not need a task: a Directus Flow with a Schedule trigger does it.

## What Crosses the Boundary

| From → to | What travels | Rule |
|-----------|--------------|------|
| Next.js → task | Ids, and `requestedBy` for the audit trail | Never a token, never a copy of the item: the task reads the current record |
| Next.js → browser | The run id, the **run-scoped** public token, `NEXT_PUBLIC_TRIGGER_API_URL` | Never `TRIGGER_SECRET_KEY`; a browser hook needs `baseURL` on self-hosted |
| Task → Directus | Reads and writes with the **task user's** token | Not the Next.js server's token, not an administrator's |
| Task → Next.js | `POST /api/revalidate` when needed (below) | Secret in the `x-revalidate-secret` header |
| Directus Flow → Next.js → task | Item keys | `directus-to-trigger` |

## Start a Task from a Server Action

The action authenticates and **authorizes** first, then starts the task with ids, then returns the run's handle. Authorizing by writing is the simplest check: the user's own token does a small write the policy must allow (here the status field), and Directus answers `403` when it does not:

```typescript
// app/articles/actions.ts
'use server';
import { auth, tasks } from '@trigger.dev/sdk';
import { updateItem, withToken } from '@directus/sdk';
import directus from '@/lib/directus';
import { requireUser } from '@/lib/session';
import type { enrichArticle } from '@/trigger/enrich-article'; // a type import: no task code in the Next.js bundle

export async function regenerateSummary(articleId: string) {
  const session = await requireUser(); // authenticate

  // Authorize: the user's own token marks the article pending; Directus applies that user's policy
  await directus.request(
    withToken(session.accessToken, updateItem('articles', articleId, { processing_status: 'pending' })),
  );

  const handle = await tasks.trigger<typeof enrichArticle>(
    'enrich-article',
    { itemId: articleId, requestedBy: session.user.id, force: true },
    { tags: [`user-${session.user.id}`] }, // lets the browser's token be refreshed without a run id lookup
  );
  return { runId: handle.id, publicAccessToken: handle.publicAccessToken };
}

/** Called by the browser when its run token runs out. It can only read this user's own runs. */
export async function refreshRunToken(): Promise<string> {
  const session = await requireUser();
  return auth.createPublicToken({
    scopes: { read: { tags: [`user-${session.user.id}`] } },
    expirationTime: '15m',
  });
}
```

- **Authorize before the trigger.** The task does not decide whether this user may do this: the action did. On the Better Auth path there is no user token, so check role or ownership in code before `tasks.trigger()`.
- **Make the call inside the action or handler.** Importing the SDK reads no environment variable; the first call does. A build that fails with `You need to set the TRIGGER_SECRET_KEY environment variable` runs a trigger at module level or while prerendering: move the call into the function. A `POST` handler and a Server Action are never prerendered, so no `export const dynamic = 'force-dynamic'` is needed for them.
- **`TRIGGER_API_URL` must be set where the call runs.** Without it the SDK falls back to Trigger.dev Cloud and sends your key there.
- **A user-started task has a user; a Flow-started one does not.** `requestedBy` is for the trail, not for authorization (`authentication` → "Authenticated Tasks").

## Show the Run in the Browser

A Client Component takes the handle from the action and subscribes with `useRealtimeRun`. The code, the self-hosted `baseURL`, the token lifetime and `refreshAccessToken` (here: `refreshRunToken` above) are in `trigger-dev` → `realtime` → "From a Next.js App with Self-Hosted Trigger.dev". What the stack decides:

- The only thing sent to the browser is the run's public token (read-only, one run, short-lived), plus the server address from `NEXT_PUBLIC_TRIGGER_API_URL`.
- The action that mints a replacement token authorizes the caller first. A tag scope on the user's id, as above, makes that check structural: the token cannot read anyone else's runs.
- Wrap handlers in an arrow function (`onClick={() => regenerateSummary(id)}`), or React passes the click event as the first argument.

## The Task Side

- **Its own environment.** A task runs on the Trigger.dev workers and sees none of the Next.js host's variables. `DIRECTUS_URL` and `DIRECTUS_TOKEN` (the task user's token) are set in the Trigger.dev project per environment (`deployment` has the table), and in `.env.trigger.local` for `trigger dev`.
- **Its own Directus client.** A task never imports `lib/directus.ts`: that module has `import 'server-only'`, which throws outside Next.js, and its token is the Next.js server's. The task-side client is in `directus-to-trigger`.
- **Idempotent work.** A task is retried and replayed, and an editor saves the same item many times: it reads the record, skips what is done, and writes results that are safe to write twice.

## Closing the Loop: Fresh Pages After a Task Writes

A task that writes Directus items changes what the pages show. Two ways to expire the tag, and the first needs no code in the task:

1. **The revalidation Flow does it** (default). It fires for every `items.update`, whoever made it, so a task's write to a collection the Flow lists expires the tag like an editor's save does. Add the collection to the Flow and to `COLLECTION_TAGS` of `/api/revalidate` (`deployment`; Step 6 of `full-feature`).
2. **The task calls `/api/revalidate` itself** (`revalidateSite()` in `directus-to-trigger`). Use it when the collection is not in the Flow, when the task changes data that never passes through Directus items, or when the site must not depend on a Flow that is easy to deactivate. It needs `NEXT_PUBLIC_SITE_URL` and `REVALIDATION_SECRET` in the Trigger.dev environment.

A task that writes many items makes the Flow call the route once per write; that is fine for tens of items, and a reason for option 2 with batched writes for thousands.

## Anti-Patterns

| Don't | Do |
|-------|-----|
| A token in a task payload | Ids and `requestedBy`; the task has its own token |
| `await` a run's result in a user-facing Server Action | Return `runId` and the token, subscribe in the browser |
| `import { myTask }` in Next.js code | `import type { myTask }` |
| A trigger at module level | Trigger inside the handler or action |
| `import 'server-only'` code in a task | A task-side client built from the task's environment |
| Assume the task sees `.env.local` | Set the variables in the Trigger.dev project (deployed) or `.env.trigger.local` (dev) |
| `TRIGGER_SECRET_KEY` in client code, or in a `NEXT_PUBLIC_` variable | The run's public token only |
| A refresh action that mints a token for any run id it is given | Authorize first, or scope the token to the user's tag |
| Retry a failed trigger in a loop inside the handler | Keep the handler thin; the task's `retry` does the retrying |

## Examples

<example>
User: "I need a Server Action that transcodes an uploaded video. Can I just await ffmpeg in the action?"
Response: "Transcoding is exactly what to offload: ffmpeg can run for minutes and a serverless action is cut off after 10 to 60 seconds. Create a `transcode-video` task. The action calls `requireUser()`, checks that this user may touch the file (a small write with `withToken`, or a role check), starts the task with `{ fileId, requestedBy }` and returns `handle.id` and `handle.publicAccessToken`. Show progress in a Client Component with `useRealtimeRun`, passing `baseURL` from `NEXT_PUBLIC_TRIGGER_API_URL`. Import the task as a type, so ffmpeg stays out of the Next.js bundle, and give the task its own Directus token."
</example>

<example>
User: "My CI build fails with 'You need to set the TRIGGER_SECRET_KEY environment variable' on a route that calls tasks.trigger()."
Response: "Importing the SDK reads no variable; the first API call does. Something calls `tasks.trigger()` while Next.js builds: a trigger at module level, or in a route that is prerendered. Move the call into the handler or action body: a `POST` handler and a Server Action are never prerendered, so no `dynamic` export is needed. Do not put a key into the build environment to silence it."
</example>

<example>
User: "After my task writes to Directus, the Next.js page still shows the old data."
Response: "Check the chain in this order. Is the collection in the revalidation Flow and in `COLLECTION_TAGS` of `/api/revalidate`? Does the page's read carry that collection's tag (expanded relations included)? Is `REVALIDATION_SECRET` the same in the Directus container and the Next.js host, with `FLOWS_ENV_ALLOW_LIST` naming it? If the collection cannot be in the Flow, call the route from the task with `revalidateSite()` and check its response."
</example>
