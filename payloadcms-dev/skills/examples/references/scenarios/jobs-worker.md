# Scenario — Jobs Worker

Three background-job patterns: post-upload image processing, nightly cleanup workflow, and a Vercel-cron-triggered worker that drains the queue.

## Patterns Covered

1. **Per-document task** — runs once when a new doc is created (image resize, thumbnail generation).
2. **Nightly workflow** — multi-step cleanup with retries from the last successful step.
3. **External triggering** — Vercel Cron Job → `/api/payload-jobs/run`.

## Task 1 — Image Processing After Upload

### `src/tasks/processImage.ts`

```ts
import type { TaskConfig } from 'payload'

export const processImage: TaskConfig<'processImage'> = {
  slug: 'processImage',
  retries: { attempts: 3, backoff: { type: 'exponential', delay: 1500 } },
  timeout: 60_000,
  inputSchema: [{ name: 'mediaId', type: 'text', required: true }],
  handler: async ({ input, req }) => {
    const media = await req.payload.findByID({ collection: 'media', id: input.mediaId, req })

    // Pretend: read file, run sharp pipeline, write derived images
    // (Storage adapter already generated standard sizes from `imageSizes` —
    //  this task is for *extra* processing: blurhash, palette extraction, OCR, etc.)
    const blurhash = `LE… mock …`
    const dominantColor = '#3b82f6'

    await req.payload.update({
      collection: 'media',
      id: input.mediaId,
      data: { blurhash, dominantColor },
      context: { skipHooks: true },
      req,
    })

    return { output: { blurhash, dominantColor } }
  },
}
```

### Wire into the Media collection

```ts
// src/collections/Media.ts
export const Media: CollectionConfig = {
  slug: 'media',
  upload: { mimeTypes: ['image/*'], /* … */ },
  fields: [
    { name: 'alt', type: 'text', required: true },
    { name: 'blurhash', type: 'text', admin: { readOnly: true } },
    { name: 'dominantColor', type: 'text', admin: { readOnly: true } },
  ],
  hooks: {
    afterChange: [
      ({ doc, operation, req, context }) => {
        if (context?.skipHooks) return doc
        if (operation === 'create') {
          req.payload.jobs.queue({
            task: 'processImage',
            input: { mediaId: doc.id },
          })
        }
        return doc
      },
    ],
  },
}
```

The hook fires `queue()` but doesn't `await` — the user doesn't wait on the upload response. The job picks up on the next worker tick.

## Workflow 2 — Nightly Cleanup

A multi-step workflow that:
1. Deletes expired sessions.
2. Archives old logs.
3. Sends a report email.

If step 3 fails, retrying picks up at step 3 — steps 1 and 2 don't re-run.

### `src/workflows/nightlyCleanup.ts`

```ts
import type { TaskConfig, WorkflowConfig } from 'payload'

export const deleteExpiredSessions: TaskConfig<'deleteExpiredSessions'> = {
  slug: 'deleteExpiredSessions',
  retries: 1,
  handler: async ({ req }) => {
    const deleted = await req.payload.delete({
      collection: 'sessions',
      where: { expiresAt: { less_than: new Date().toISOString() } },
      req,
    })
    return { output: { count: (deleted as any).docs?.length ?? 0 } }
  },
}

export const archiveOldLogs: TaskConfig<'archiveOldLogs'> = {
  slug: 'archiveOldLogs',
  retries: 1,
  handler: async ({ req }) => {
    const cutoff = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()
    const result = await req.payload.update({
      collection: 'request-log',
      where: { createdAt: { less_than: cutoff } },
      data: { archived: true },
      req,
    })
    return { output: { archived: (result as any).docs?.length ?? 0 } }
  },
}

export const sendCleanupReport: TaskConfig<'sendCleanupReport'> = {
  slug: 'sendCleanupReport',
  retries: { attempts: 3, backoff: { type: 'exponential', delay: 5000 } },
  inputSchema: [
    { name: 'sessionsDeleted', type: 'number' },
    { name: 'logsArchived', type: 'number' },
  ],
  handler: async ({ input, req }) => {
    await req.payload.sendEmail({
      to: 'ops@example.com',
      subject: 'Nightly cleanup report',
      text: `Sessions deleted: ${input.sessionsDeleted}\nLogs archived: ${input.logsArchived}`,
    })
    return { output: {} }
  },
}

export const nightlyCleanup: WorkflowConfig<'nightlyCleanup'> = {
  slug: 'nightlyCleanup',
  handler: async ({ tasks }) => {
    const sessions = await tasks.inline({ task: 'deleteExpiredSessions', input: {} })
    const logs = await tasks.inline({ task: 'archiveOldLogs', input: {} })
    await tasks.inline({
      task: 'sendCleanupReport',
      input: {
        sessionsDeleted: sessions.output.count,
        logsArchived: logs.output.archived,
      },
    })
  },
}
```

Register:
```ts
// payload.config.ts
import {
  processImage,
  deleteExpiredSessions, archiveOldLogs, sendCleanupReport, nightlyCleanup,
} from './tasks-and-workflows'

export default buildConfig({
  // …
  jobs: {
    tasks: [processImage, deleteExpiredSessions, archiveOldLogs, sendCleanupReport],
    workflows: [nightlyCleanup],
    autoRun: [
      { cron: '*/1 * * * *', queue: 'default', limit: 20 },     // every minute, image tasks etc.
      { cron: '0 3 * * *',   queue: 'cron',    limit: 1 },      // 3 AM daily — workflow
    ],
    shouldAutoRun: () => process.env.ENABLE_JOBS === 'true',
  },
})
```

Queue the nightly job from a cron tick:
```ts
// One-time bootstrap script or on-deploy hook
await payload.jobs.queue({ workflow: 'nightlyCleanup', input: {} })
```

For a recurring schedule you can also write a "ticker" task that runs every day at 3am and queues `nightlyCleanup`:
```ts
{
  slug: 'queueNightlyCleanup',
  retries: 0,
  handler: async ({ req }) => {
    await req.payload.jobs.queue({ workflow: 'nightlyCleanup', input: {} })
    return { output: {} }
  },
}

// autoRun:
{ cron: '0 3 * * *', queue: 'tickers' }
```

The `ticker` queue is processed by a dedicated `autoRun` block.

## Pattern 3 — External Trigger via Vercel Cron

For environments where you don't want an always-on Node process, drain the queue via Vercel Cron hitting Payload's job endpoint.

### `vercel.json`

```json
{
  "crons": [
    {
      "path": "/api/payload-jobs/run?queue=default&limit=50",
      "schedule": "*/2 * * * *"
    },
    {
      "path": "/api/payload-jobs/run?queue=cron&limit=5",
      "schedule": "0 3 * * *"
    }
  ]
}
```

Make the endpoint admin-only or protect it with a shared secret. Add a guard custom endpoint in front:

```ts
// payload.config.ts
endpoints: [
  {
    path: '/run-jobs',
    method: 'post',
    handler: async (req) => {
      const auth = req.headers.get('authorization')
      if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
        return new Response('Forbidden', { status: 403 })
      }
      const queue = new URL(req.url).searchParams.get('queue') || 'default'
      const result = await req.payload.jobs.run({ queue, limit: 50 })
      return Response.json(result)
    },
  },
],
```

Update `vercel.json` to call `/api/run-jobs` and set `CRON_SECRET` in Vercel env.

## Monitoring

Query the `payload-jobs` collection from your admin panel or a custom endpoint:

```ts
// Failed jobs eligible for manual retry
await payload.find({
  collection: 'payload-jobs',
  where: { hasError: { equals: true } },
  sort: '-createdAt',
})

// In-flight jobs (might be stuck)
await payload.find({
  collection: 'payload-jobs',
  where: { processing: { equals: true } },
})
```

Mass-retry:
```ts
await payload.jobs.run({ where: { hasError: { equals: true } } })
```

## What This Demonstrates

- One-shot tasks vs multi-step workflows.
- `afterChange` hook queueing jobs without `await`.
- Resumable workflow state — failures resume from the last successful step.
- Three triggering models: in-process `autoRun`, ticker tasks, external HTTP cron.
- Guarded job-run endpoint for production-safe external triggers.
- Querying the `payload-jobs` collection for retries / observability.
