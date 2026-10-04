---
name: jobs-queue
description: This skill should be used when the user asks about "Payload jobs queue", "Payload background tasks", "Payload workflows", "Payload cron scheduling", "Payload task retries", "Payload runJobs", "Payload autoRun", "queue a job in Payload", or needs to run any background or scheduled work in PayloadCMS.
---

# PayloadCMS — Jobs Queue

Payload ships a built-in job queue: durable background work backed by your DB. Two primitives:

- **Task** — a single unit of work with typed input/output, retries, and timeout.
- **Workflow** — a sequence of inline tasks composed in code. Failures resume from the last successful step.

Jobs are stored in the `payload-jobs` collection (auto-created). You don't run a separate worker process unless you want to — Payload can execute jobs in-process on a schedule, or you can trigger them with `payload.jobs.run()` from a cron or webhook.

> **Breaking since 3.89.0 — `payload-jobs` is closed by default.** The collection ships with `create`, `read`, `update` and `delete` all returning `false` (and stays hidden in the Admin Panel), because job inputs, outputs, errors and logs can hold sensitive data. REST/GraphQL CRUD on `payload-jobs` and Local API calls with `overrideAccess: false` are rejected. `payload.jobs.queue/run/runByID/cancel/handleSchedules` keep working, and so do `GET /api/payload-jobs/run` and `GET /api/payload-jobs/handle-schedules` — the endpoints are gated by `jobs.access.run`, not by the collection's access. To open the collection deliberately, see "Access to `payload-jobs`" below.

## Defining a Task

```ts
// src/tasks/sendOrderConfirmation.ts
import type { TaskConfig } from 'payload'

export const sendOrderConfirmation: TaskConfig<'sendOrderConfirmation'> = {
  slug: 'sendOrderConfirmation',
  inputSchema: [
    { name: 'orderId', type: 'text', required: true },
    { name: 'email', type: 'email', required: true },
  ],
  outputSchema: [
    { name: 'messageId', type: 'text' },
    { name: 'sentAt', type: 'date' },
  ],
  retries: 3,                         // Attempts after first failure
  handler: async ({ input, req }) => {
    const order = await req.payload.findByID({
      collection: 'orders',
      id: input.orderId,
      req,
    })

    const result = await req.payload.sendEmail({
      to: input.email,
      subject: `Order ${order.id} confirmed`,
      html: `<p>Thanks for your order.</p>`,
    })

    return {
      output: {
        messageId: (result as any).messageId,
        sentAt: new Date().toISOString(),
      },
    }
  },
}
```

Register tasks under `jobs.tasks` in `payload.config.ts`:

```ts
import { sendOrderConfirmation } from './tasks/sendOrderConfirmation'
import { renderPDF } from './tasks/renderPDF'

export default buildConfig({
  // …
  jobs: {
    tasks: [sendOrderConfirmation, renderPDF],
  },
})
```

## Queueing a Task

From a hook, endpoint, or anywhere with a Payload instance:

```ts
await req.payload.jobs.queue({
  task: 'sendOrderConfirmation',
  input: {
    orderId: order.id,
    email: order.customer.email,
  },
  waitUntil: new Date(Date.now() + 60_000),   // Delay 60s
  // queue: 'default',                          // Optional named queue
})
```

Returns a `Job` document — query `payload-jobs` to see status, retries, output.

## Workflows — Multi-Step Jobs

A workflow runs a sequence of inline tasks. State is persisted between steps so retries pick up where they left off:

```ts
import type { WorkflowConfig } from 'payload'

export const onboardUser: WorkflowConfig<'onboardUser'> = {
  slug: 'onboardUser',
  inputSchema: [{ name: 'userId', type: 'text', required: true }],
  handler: async ({ job, req, tasks }) => {
    // Step 1: provision account
    const provisioned = await tasks.inline({
      task: 'provisionAccount',
      input: { userId: job.input.userId },
      retries: 2,
    })

    // Step 2: send welcome email
    await tasks.inline({
      task: 'sendWelcomeEmail',
      input: { userId: job.input.userId, plan: provisioned.output.plan },
    })

    // Step 3: notify Slack
    await tasks.inline({
      task: 'notifySlack',
      input: { event: 'user.onboarded', userId: job.input.userId },
    })
  },
}
```

Register under `jobs.workflows`:
```ts
jobs: {
  tasks: [provisionAccount, sendWelcomeEmail, notifySlack],
  workflows: [onboardUser],
},
```

Queue it:
```ts
await payload.jobs.queue({
  workflow: 'onboardUser',
  input: { userId: newUser.id },
})
```

If `sendWelcomeEmail` fails, retrying the job re-runs from `sendWelcomeEmail` — `provisionAccount` is skipped because Payload remembers its output.

## Running Queued Jobs

> **Scheduled publish depends on this.** `versions.drafts.schedulePublish` enqueues publish/unpublish jobs — without a running processor (autoRun, `payload jobs:run`, or the run endpoint) those events never fire.

### In-process autoRun

For low-volume apps, let Payload poll and run jobs automatically:

```ts
jobs: {
  tasks: [/* … */],
  autoRun: [
    {
      cron: '*/5 * * * *',           // Every 5 minutes
      limit: 10,                      // Up to 10 jobs per tick
      queue: 'default',
      // disableScheduling: true,     // Skip enqueueing due `schedule` entries on this tick
    },
    {
      cron: '0 * * * *',              // Hourly
      queue: 'heavy',
    },
  ],
  shouldAutoRun: (payload) => process.env.ENABLE_JOBS === 'true',  // receives the payload instance
  // Processing order: FIFO by default ('createdAt'); flip per queue:
  processingOrder: { default: 'createdAt', queues: { nightly: '-createdAt' } },  // LIFO for 'nightly'
},
```

Set `ENABLE_JOBS=true` on exactly one server instance — otherwise multiple replicas race for the same jobs.

### External cron / webhook

For higher throughput or dedicated workers, hit Payload's job endpoint from outside:

```bash
# GET only (POST reaches it solely via the 'X-Payload-HTTP-Method-Override: GET' header);
# query params: limit (default 10), queue (default 'default'), allQueues=true
curl 'https://app.example.com/api/payload-jobs/run?limit=100&queue=nightly' \
  -H "Authorization: Bearer $CRON_SECRET"
```

Gate the endpoint via `jobs.access.run` in config — check the Authorization header (e.g. Vercel Cron's `CRON_SECRET`):

```ts
jobs: {
  access: {
    run: ({ req }): boolean => {
      const authHeader = req.headers.get('authorization')
      return authHeader === `Bearer ${process.env.CRON_SECRET}`
    },
  },
},
```

Vercel cron config:
```jsonc
// vercel.json
{ "crons": [{ "path": "/api/payload-jobs/run", "schedule": "*/5 * * * *" }] }
```

Or call from a Node script / Trigger.dev / GitHub Actions workflow:
```ts
const { results } = await payload.jobs.run({
  queue: 'default',
  limit: 50,
})
```

### Bin scripts (dedicated worker)

Run jobs in a **separate process** — no impact on API response times:

```bash
# Drain queues on a schedule (flags: --queue, --limit, --cron, --handle-schedules, --all-queues)
pnpm payload jobs:run --queue default --limit 10 --cron "*/5 * * * *"

# Enqueue due scheduled jobs only (no execution)
pnpm payload jobs:handle-schedules --cron "*/5 * * * *"
```

This is the recommended runner on dedicated servers. See the `cli-recipes` skill for flag details.

### Cron-only tasks (scheduled work)

Combine `cron` with `autoRun` to schedule recurring tasks:
```ts
jobs: {
  tasks: [
    {
      slug: 'cleanupExpiredSessions',
      retries: 0,
      handler: async ({ req }) => {
        await req.payload.delete({
          collection: 'sessions',
          where: { expiresAt: { less_than: new Date().toISOString() } },
          req,
        })
        return { output: {} }
      },
    },
  ],
  autoRun: [{ cron: '0 3 * * *', queue: 'cron' }],
},
```

### Declarative job schedules (`schedule`)

Newer Payload versions let a task or workflow declare its own recurring schedule with a `schedule` array, instead of wiring every cron in the central `autoRun`. Scheduling only **enqueues** jobs — you still need a runner (`autoRun`, a bin script, or an API trigger) to execute them.

```ts
// src/jobs/SendDigestEmail.ts
import type { TaskConfig } from 'payload'

export const SendDigestEmail: TaskConfig = {
  slug: 'SendDigestEmail',
  schedule: [
    {
      cron: '0 0 * * *',        // every day at midnight (5- or 6-field cron)
      queue: 'nightly',         // queue the enqueued job lands in
      hooks: {
        // beforeSchedule: control concurrency / inject dynamic input
        // afterSchedule: log or emit metrics after queueing
      },
    },
  ],
  handler: async () => {
    /* … */
    return { output: {} }
  },
}
```

Use `schedule` when the cadence belongs with the task definition; use `autoRun` when you want one place to govern which queues run in this process. They compose — `schedule` decides *when to enqueue*, `autoRun`/`payload.jobs.run()` decides *when to drain*.

Details worth knowing:

- `queue` is **required** in each `ScheduleConfig` entry; the cron expression supports **seconds precision** (6-field form).
- Due-schedule tracking lives in the auto-created `payload-jobs-stats` global.
- `beforeSchedule` can return `{ shouldSchedule, input }` — use the provided `countRunnableOrActiveJobsForQueue` helper to cap concurrency.
- Scheduling is executed by autoRun ticks (unless the autoRun entry sets `disableScheduling: true`), by `payload jobs:run --handle-schedules`, by `GET /api/payload-jobs/handle-schedules`, or programmatically via `await payload.jobs.handleSchedules()`.

## Concurrency Control

Prevent two jobs that touch the same record from running at once — or collapse a burst of identical jobs into the latest one. Opt in globally, then give a task or workflow a `concurrency` key:

```ts
jobs: {
  enableConcurrencyControl: true,   // adds an indexed `concurrencyKey` field to payload-jobs
  tasks: [
    {
      slug: 'syncCustomer',
      inputSchema: [{ name: 'customerId', type: 'text', required: true }],
      // Shorthand: return the key; only one job per key runs at a time (exclusive: true)
      concurrency: ({ input }) => `customer:${input.customerId}`,
      handler: async ({ input }) => ({ output: {} }),
    },
    {
      slug: 'rebuildSearchIndex',
      // Object form: also drop older *pending* jobs with the same key when a new one is queued
      concurrency: {
        key: ({ input }) => 'search-index',
        exclusive: true,     // default true
        supersedes: true,    // default false; running jobs are never cancelled
      },
      handler: async () => ({ output: {} }),
    },
  ],
},
```

`enableConcurrencyControl` changes the `payload-jobs` schema, so on SQL adapters run `pnpm payload generate:types`, `pnpm payload migrate:create` and `pnpm payload migrate` after enabling it. It defaults to `false`; the Payload source marks it to default to `true` in Payload 4.

## Access to `payload-jobs`

Because the collection denies everything by default (3.89.0+), decide explicitly who may see jobs. Trusted server code needs nothing: the Local API defaults to `overrideAccess: true` in v3, so existing `payload.find({ collection: 'payload-jobs' })` calls keep working — but pass `overrideAccess: true` explicitly, because the 4.0 canary flips the Local API default to `false` (do not run the canary in production). To let administrators inspect jobs in the Admin Panel, override the collection with the `@experimental` `jobsCollectionOverrides` and open **read only**:

```ts
// src/payload.config.ts
export default buildConfig({
  jobs: {
    tasks: [/* … */],
    jobsCollectionOverrides: ({ defaultJobsCollection }) => ({
      ...defaultJobsCollection,
      access: {
        ...defaultJobsCollection.access,                       // create/update/delete stay () => false
        read: ({ req }) => Boolean(req.user?.roles?.includes('admin')),
      },
      admin: { ...defaultJobsCollection.admin, hidden: false },   // show it in the nav
    }),
  },
})
```

Opening `create`/`update`/`delete` exposes execution-control fields (retry state, queue, `processing`, `hasError`) to API clients — prefer read-only for trusted admins, and never `() => true`. The run endpoints are separate: keep gating them with `jobs.access.run` (see "External cron / webhook").

## Retries, Timeouts, Failure Handling

```ts
{
  slug: 'fetchExternalAPI',
  retries: {
    attempts: 5,
    backoff: { type: 'exponential', delay: 1000 },   // 1s, 2s, 4s, 8s, 16s
  },
  timeout: 30_000,                                    // 30s max
  handler: async ({ input, req }) => {
    // …
  },
  onFail: async ({ job, req }) => {
    req.payload.logger.error({ msg: 'job permanently failed', jobId: job.id })
    await req.payload.create({
      collection: 'alerts',
      data: { type: 'job.failed', jobId: job.id, reason: job.error?.message },
      req,
    })
  },
}
```

After `attempts` exhausted, the job is marked `failed` and `onFail` fires.

## Querying Jobs

Reading `payload-jobs` directly is trusted-server-code only (the collection is closed by default since 3.89.0 — see "Access to `payload-jobs`"). Pass `overrideAccess: true` explicitly so the code survives the Payload 4 canary's `overrideAccess: false` default:

```ts
// Pending jobs
const pending = await payload.find({
  collection: 'payload-jobs',
  overrideAccess: true,
  where: { hasError: { not_equals: true }, processing: { not_equals: true }, completedAt: { exists: false } },
})

// Failed jobs (eligible for manual retry)
const failed = await payload.find({
  collection: 'payload-jobs',
  overrideAccess: true,
  where: { hasError: { equals: true } },
})

// Manually retry a single job
await payload.jobs.run({ where: { id: { equals: jobId } } })

// Run one job by ID
await payload.jobs.runByID({ id: jobId })

// Cancel jobs matching a query / one job by ID
await payload.jobs.cancel({ where: { taskSlug: { equals: 'sendOrderConfirmation' } } })
await payload.jobs.cancelByID({ id: jobId })
```

The `payload-jobs` collection is hidden from the Admin Panel and denies all access by default (3.89.0+). To browse jobs at `/admin/collections/payload-jobs`, open it read-only through `jobsCollectionOverrides` — see "Access to `payload-jobs`".

## Patterns

### Fire-and-forget from a hook

```ts
afterChange: [
  ({ doc, req, operation }) => {
    if (operation === 'create') {
      req.payload.jobs.queue({
        task: 'sendOrderConfirmation',
        input: { orderId: doc.id, email: doc.email },
      })
    }
    return doc
  },
],
```

Use a one-off task — do not `await` inside the response path if you don't need to.

### Idempotent tasks

If the same task may be queued twice (retries, webhooks):
```ts
handler: async ({ input, req }) => {
  const already = await req.payload.find({
    collection: 'emails',
    where: { orderId: { equals: input.orderId } },
    limit: 1,
  })
  if (already.docs.length > 0) return { output: { skipped: true } }
  // …
}
```

### Long-running tasks

Don't block a single task for hours. Break into a workflow with checkpoint steps so retries pick up partway.

## See Also

- The `hooks` skill — queueing jobs from `afterChange`.
- The `adapters` skill — transaction semantics affect job persistence.
- `nextjs-integration` skill — invoking `payload.jobs.run()` from a Vercel cron or scheduled function.
