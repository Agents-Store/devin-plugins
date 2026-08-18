---
name: scheduled-tasks
description: This skill should be used when the user wants to "create a scheduled task with trigger.dev", "add a cron job", "run a daily task", "sync directus on a schedule", "build a cron that reads from directus", "attach a schedule to production", "timezone-aware cron", or needs patterns for defining `schedules.task()` cron jobs that interact with Directus from the Directus + Next.js + Trigger.dev stack.
---

# Scheduled Tasks: Cron Jobs in the Stack

How to define and operate `schedules.task()` in this stack — with special attention to reading and writing Directus from inside a scheduled run, closing the loop back to Next.js, and attaching schedules to specific environments. For the full Trigger.dev schedule API, defer to the `trigger-dev` plugin's `task-development` skill.

## Quick Decision: Is This the Right Tool?

| Need | Tool |
|------|------|
| Run code on a fixed cron (daily, hourly, every 15 min) | **`schedules.task()`** (this skill) |
| Run code in response to a user action | `task()` + `tasks.trigger()` (see `background-tasks`) |
| Run code when a Directus item changes | Directus Flow → webhook → `tasks.trigger()` (see `directus-to-trigger`) |
| Fire an HTTP webhook on a schedule with no logic | Directus Flows (Schedule trigger) — simpler, no task needed |

Use `schedules.task()` when you need durable execution, retries, observability, and typed code that can talk to Directus and other services.

## Defining a Schedule

Place schedule definitions in `/trigger/schedules/` or `/trigger/` alongside regular tasks. Trigger.dev discovers them automatically.

```typescript
// trigger/schedules/daily-digest.ts
import { schedules, logger } from '@trigger.dev/sdk/v3';
import { createDirectus, rest, staticToken, readItems } from '@directus/sdk';
import type { Schema } from '@/types/directus';

export const dailyDigestTask = schedules.task({
  id: 'daily-digest',
  // Run every day at 08:00 UTC
  cron: {
    pattern: '0 8 * * *',
    timezone: 'UTC',
  },
  maxDuration: 600, // 10 minutes
  run: async (payload, { ctx }) => {
    // payload.timestamp — when the schedule fired
    // payload.lastTimestamp — previous run's timestamp
    // payload.externalId — if this schedule was created dynamically with an external ID
    // payload.upcoming — array of next few scheduled timestamps

    logger.log('Daily digest starting', {
      runAt: payload.timestamp,
      previousRun: payload.lastTimestamp,
    });

    const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
      .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
      .with(rest({ cache: 'no-store' }));

    // ... do the work ...

    return { digestSent: true };
  },
});
```

## Cron Patterns

Standard 5-field cron (minute, hour, day-of-month, month, day-of-week):

| Pattern | Meaning |
|---------|---------|
| `*/15 * * * *` | Every 15 minutes |
| `0 * * * *` | Every hour on the hour |
| `0 8 * * *` | Daily at 08:00 |
| `0 8 * * 1-5` | Weekdays at 08:00 |
| `0 0 1 * *` | First day of every month, midnight |
| `0 2 * * 0` | Every Sunday at 02:00 |

**Minimum resolution: 1 minute.** Trigger.dev does not allow sub-minute schedules — don't use `* * * * *` (every minute) unless you genuinely need it, and never try `*/30 * * * * *` (every 30 seconds).

## Timezone-Aware Scheduling

```typescript
cron: {
  pattern: '0 9 * * 1-5',
  timezone: 'America/New_York', // runs at 09:00 NY time, adjusts for DST
},
```

Use timezones when the schedule needs to match a business calendar (market open, store hours, customer-local daily digest). Use UTC for system jobs where timing doesn't depend on humans.

## Reading from Directus in a Schedule

Build a server-side Directus client **inside** the task's `run` function. Do NOT import the singleton from `lib/directus.ts` — that module has `import 'server-only'` which throws outside Next.js.

```typescript
run: async (payload, { ctx }) => {
  const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
    .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
    .with(rest({ cache: 'no-store' }));

  // Read items created since the last run
  const since = payload.lastTimestamp?.toISOString() ?? new Date(0).toISOString();
  const newItems = await directus.request(
    readItems('orders', {
      filter: { date_created: { _gte: since } },
      fields: ['id', 'customer_email', 'total'],
      sort: ['-date_created'],
      limit: 1000,
    })
  );

  logger.log('Found new items since last run', { count: newItems.length, since });
  // ... process them ...
},
```

Using `payload.lastTimestamp` gives you an incremental "what changed since last run" window for free — no state table needed on your side.

## Writing Back to Directus

```typescript
await directus.request(
  updateItem('orders', orderId, {
    digest_sent_at: new Date().toISOString(),
    digest_run_id: ctx.run.id, // store the Trigger run ID for audit
  })
);
```

**If Directus is down**, the request throws. Trigger's retry mechanism will re-run the task per the `retry` config — you don't need to add a try/catch unless you want to continue on partial failure. See "Idempotency" below for safe retries.

## Idempotency for Scheduled Runs

Scheduled tasks can be retried (automatic retries on failure, or manual re-runs from the dashboard). Any Directus writes need to be safe under repetition.

### Pattern 1: Check-then-act

```typescript
const [existing] = await directus.request(
  readItems('digests', {
    filter: {
      run_timestamp: { _eq: payload.timestamp.toISOString() },
    },
    limit: 1,
  })
);

if (existing) {
  logger.log('Digest for this timestamp already sent — skipping', { runId: existing.id });
  return { skipped: true };
}

// ... proceed to create the digest ...
```

### Pattern 2: Upsert with a deterministic key

Use a composite natural key: `(digest_type, date)`. Try to find it; if present, update; else create. Retry-safe.

### Pattern 3: Idempotency on inner task calls

If the schedule fans out to other tasks, pass `idempotencyKey` to each `tasks.trigger()`:

```typescript
await tasks.trigger<typeof enrichOrderTask>(
  'enrich-order',
  { orderId },
  { idempotencyKey: `enrich-order-${orderId}-${payload.timestamp.toISOString()}` }
);
```

## Attaching Schedules to Environments

**Schedules are NOT automatically active after deploy.** This is a deliberate safety — you don't want a production cron to start firing the first time a dev pushes new code.

Attach via the dashboard: Trigger.dev → Schedules → `{task-id}` → Attach → select environment (dev / staging / prod).

Or via CLI:

```bash
# After deploy
npx trigger.dev@latest schedules:attach daily-digest --env prod
```

You can also attach to a specific timezone per environment, e.g. run the same task on UTC in dev and on `America/New_York` in prod.

### Declarative vs Dynamic Schedules

| Declarative (what this skill shows) | Dynamic |
|------|---------|
| Schedule is defined in code with `schedules.task({ cron })` | Schedule is created at runtime via `schedules.create()` |
| Requires a deploy to change the cron | Can be changed via API call / user action |
| Best for system jobs (daily digest, hourly sync) | Best for per-tenant or user-configured schedules |
| Attached once in the dashboard | Created on demand from a Server Action |

For a user-configured schedule (e.g. "send me a weekly report at a time I choose"), use `schedules.create()` inside a Server Action:

```typescript
'use server';
import { schedules } from '@trigger.dev/sdk/v3';

export async function scheduleWeeklyReport(userId: string, hour: number, timezone: string) {
  const schedule = await schedules.create({
    task: 'send-user-report',
    cron: `0 ${hour} * * 1`, // every Monday at :00 in the given hour
    timezone,
    externalId: `user-${userId}`, // your stable identifier
    deduplicationKey: `weekly-${userId}`, // prevents duplicate creation
  });

  // Store schedule.id in Directus so you can delete/update it later
  return schedule;
}
```

Use `schedules.del(scheduleId)` when the user disables it, and `schedules.deactivate(scheduleId)` to pause without deleting.

## Close-the-Loop Revalidation

If the schedule updates Directus data that a Next.js page displays, POST to `/api/revalidate` at the end of the run so users see fresh content:

```typescript
// at the end of run()
await fetch(
  `${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ collection: 'orders' }),
  }
);
```

Without this, the page stays at its last ISR cache until the revalidate interval expires or a user navigates to an uncached variant.

## Local Testing

Run `npx trigger.dev@latest dev` in one terminal. The dev server registers all schedule tasks BUT does not automatically fire them on the real cron — that would be unpredictable during development.

Test-run from the dashboard:
1. Open the Trigger.dev dashboard → Tasks → `daily-digest`
2. Click "Test" → provide a fake payload: `{ timestamp: new Date(), lastTimestamp: new Date(Date.now() - 86400000) }`
3. The run executes against local env vars (from `.env.local` proxied through the dev server)

For CI, you can also test-run via MCP: `trigger-dev:run_task` with a synthetic payload.

## Production Operation

- **Enable/disable** from the dashboard per environment
- **Manual re-run** any past execution (e.g. to backfill after an outage)
- **Inspect logs** for each run — `logger.log()` output is searchable
- **Alerts**: configure the Trigger.dev dashboard to notify on task failure (email, Slack webhook)
- **Versioning**: each deploy creates a new task version — in-flight runs finish on the old version, new runs use the new version

## Anti-Patterns

| Don't | Do |
|-------|-----|
| `import directus from '@/lib/directus'` inside a task | Build a fresh client inside `run()` — `lib/directus.ts` has `'server-only'` which breaks outside Next.js |
| Sub-minute crons (`* * * * *` minus a few) | Minimum 1 minute resolution — fan out from a 1-min task if you truly need faster |
| Run the same cron in dev + staging + prod attached simultaneously | Attach only to the environments you want firing; dev should fire on-demand via test-run |
| Blind writes on retry (no idempotency) | Use deterministic keys + upsert, or check-then-act |
| Skip revalidation at the end of the task | Close the loop — POST to `/api/revalidate` so Next.js ISR reflects the new data |
| Hardcode `cron: '0 8 * * *'` without a timezone | Always set `cron.timezone` explicitly (UTC or a business zone) — ambiguous default drifts on DST |

## Examples

<example>
User: "Build a nightly job that archives orders older than 90 days and updates their Directus status."
Response: "Create `trigger/schedules/archive-old-orders.ts` with `schedules.task({ id: 'archive-old-orders', cron: { pattern: '0 3 * * *', timezone: 'UTC' }, run: async () => { ... } })`. Inside `run`, build a server-side Directus client, `readItems('orders', { filter: { date_created: { _lt: ninetyDaysAgo }, status: { _eq: 'completed' } } })`, then `updateItem` each to `status: 'archived'`. Make it idempotent — if `status` is already `archived`, skip. POST to `/api/revalidate` at the end. Deploy, then attach the schedule to production from the dashboard — schedules don't fire until attached."
</example>

<example>
User: "My scheduled task sometimes runs twice for the same hour. How do I prevent duplicate work?"
Response: "Trigger doesn't run the same schedule occurrence twice on its own, but manual re-runs and retries can cause it. Inside `run()`, check if the work for `payload.timestamp` already landed in Directus before doing it again — e.g. `filter: { run_timestamp: { _eq: payload.timestamp.toISOString() } }`. If present, log and return early. For fan-out to inner tasks, pass `idempotencyKey: \`<action>-<entity>-${payload.timestamp.toISOString()}\`` to `tasks.trigger()`."
</example>

<example>
User: "I want users to pick a delivery time for their daily report — how do I create schedules dynamically?"
Response: "Use `schedules.create()` inside a Server Action. Pass `task: 'send-user-report'`, `cron: '0 ${hour} * * *'`, `timezone: user.timezone`, `externalId: user.id`, and `deduplicationKey: \`daily-${user.id}\`` so re-running the Server Action doesn't create duplicates. Store the returned `schedule.id` in Directus on the user row. To cancel, call `schedules.del(scheduleId)`. To pause, `schedules.deactivate(scheduleId)`."
</example>
