---
name: scheduled-tasks
description: Schedule Trigger.dev tasks with cron — declarative schedules defined on schedules.task, imperative per-user schedules created through the SDK or API, timezones, spreading windows, retries and idempotency of scheduled runs, testing, and why a schedule did not fire. Use when the user asks to "schedule a trigger.dev task", "run a task on a cron", "create a schedule", "dynamic or per-user schedules", "schedules:attach", "attach a schedule to production", "my schedule did not run", or "my cron runs a few minutes late".
---

# Scheduled Tasks

Run Trigger.dev tasks on a cron. A schedule is either **declarative** (the cron lives on the task and is synced when you run `dev` or `deploy`) or **imperative** (created at runtime through the SDK, the API or the dashboard, for per-user or per-tenant schedules). A scheduled task can have both kinds at once. SDK 4.x, `@trigger.dev/sdk`; all snippets type-check against 4.7.2.

Scheduled tasks are for **recurring** work. For one run at a later time use the `delay` option of `trigger()` (see `references/triggering-patterns.md` in **task-development**); for work started by an event use `task()` and `trigger()`.

## There is no "attach" step for a declarative schedule

A `schedules.task` with a `cron` is created, updated and removed when the CLI syncs it, on `dev` and on `deploy`. Nothing has to be attached afterwards. The CLI has no `schedules:attach` command (`npx trigger.dev schedules:attach` answers `unknown command`), and `deploy` has no flag for it. The "attach" wording in the docs applies only to a scheduled task defined **without** `cron`: it waits for imperative schedules, which you create in the dashboard or with `schedules.create()`.

A declarative schedule runs in **every** environment unless you limit it with `environments` (below). If a nightly job must not fire from a developer's `dev` session or from staging, say so in the cron object.

## Declarative schedule

```ts
// trigger/daily-digest.ts
import { schedules, logger } from "@trigger.dev/sdk";

export const dailyDigest = schedules.task({
  id: "daily-digest",
  cron: {
    pattern: "0 8 * * 1-5", // 08:00 on weekdays
    timezone: "Europe/Berlin", // evaluated in this zone, follows daylight saving
    environments: ["PRODUCTION"], // omit to run in every environment
  },
  maxDuration: 600,
  run: async (payload, { ctx }) => {
    logger.info("digest starting", {
      scheduledFor: payload.timestamp.toISOString(),
      previous: payload.lastTimestamp?.toISOString() ?? null,
      runId: ctx.run.id,
    });
    return { sentAt: new Date().toISOString() };
  },
});
```

A plain string is UTC: `cron: "0 0 * * *"`. Editing or deleting `cron` updates the synced schedule on the next `dev` or `deploy`. The dashboard lists it on the task's **Schedules** tab (Tasks page, open the task); declarative schedules are read-only there.

### The payload

| Field | Meaning |
|-------|---------|
| `timestamp` | `Date`, the scheduled (nominal) time in UTC. A few milliseconds earlier than `new Date()` inside the run |
| `lastTimestamp` | `Date` of the previous run, `undefined` the first time |
| `timezone` | IANA zone of the schedule, `"UTC"` by default |
| `scheduleId` | id of the schedule that fired (a task can have many) |
| `externalId` | your own id from `schedules.create()`, `undefined` for a declarative schedule |
| `type` | `"DECLARATIVE"` or `"IMPERATIVE"` |
| `upcoming` | the next five nominal times |

Print the time in the schedule's zone with `payload.timestamp.toLocaleString("en-US", { timeZone: payload.timezone })`.

## Cron syntax

Five fields: minute, hour, day of month, month, day of week (`0` or `7` is Sunday). `L` means last: `L` in day of month is the last day, `1L` in day of week the last Monday. **No seconds field**, so the finest schedule is one minute.

| Pattern | Meaning |
|---------|---------|
| `*/15 * * * *` | every 15 minutes |
| `0 * * * *` | every hour, on the hour |
| `0 8 * * 1-5` | weekdays at 08:00 |
| `0 0 1 * *` | midnight on the 1st of each month |
| `0 0 L * *` | midnight on the last day of each month |
| `0 2 * * 0` | Sunday at 02:00 |

Give a timezone when the schedule follows a calendar people live by (store hours, a customer's morning). Leave UTC for system jobs.

## Spread window (server ≥ 4.6.0)

Since server 4.6.0 a **new** schedule is not started at its exact cron time: runs are spread over a window after it, so that many schedules sharing `0 9 * * *` do not all start at once. The offset is stable per schedule, and `payload.timestamp` and `upcoming` always show the nominal cron time, not the real start. If a daily job "runs a few minutes late", that is why. Set the window yourself:

```ts
// trigger/exact-report.ts
import { schedules } from "@trigger.dev/sdk";

export const exactReport = schedules.task({
  id: "exact-report",
  cron: { pattern: "0 9 * * *", window: "0m" }, // "0m" or "0%": start at the cron time
  run: async () => {},
});

export const spreadReport = schedules.task({
  id: "spread-report",
  cron: { pattern: "0 9 * * *", window: "30m" }, // somewhere in the 30 minutes after 09:00
  run: async () => {},
});
```

A window is a whole number of minutes or hours up to 24 hours (`"30m"`, `"2h"`) or a percentage of the interval between runs (`"30%"`); an absolute window never reaches past the next cron time. Imperative schedules take the same `window` in `schedules.create()` and `schedules.update()`. The free-plan minimum on Cloud does not apply to self-hosted. Retrieving a schedule shows `nextRun` (nominal) and `nextRunEffectiveAt` (the assigned start).

## Imperative schedules: one per user or tenant

Define the task once, then attach as many schedules as you need. `deduplicationKey` is required: a second `create()` with the same key updates that schedule instead of adding another.

```ts
// trigger/send-user-report.ts
import { schedules } from "@trigger.dev/sdk";

export const sendUserReport = schedules.task({
  id: "send-user-report", // no cron: it runs only for the schedules you attach
  run: async (payload) => {
    if (!payload.externalId) throw new Error("schedule has no externalId");
    const userId = payload.externalId;
    // load the user, build the report, send it
    return { userId };
  },
});
```

```ts
// lib/report-schedules.ts (server code: an API route or a Server Action)
import { schedules } from "@trigger.dev/sdk";

export async function scheduleWeeklyReport(userId: string, hour: number, timezone: string) {
  const schedule = await schedules.create({
    task: "send-user-report", // the id of a task defined with schedules.task()
    cron: `0 ${hour} * * 1`, // Mondays at <hour>:00 in the user's zone
    timezone,
    externalId: userId, // arrives as payload.externalId
    deduplicationKey: `weekly-report-${userId}`,
  });
  return schedule.id; // keep it next to the user so you can change or delete it later
}

export async function pauseWeeklyReport(scheduleId: string) {
  await schedules.deactivate(scheduleId); // schedules.activate() resumes it
}

export async function removeWeeklyReport(scheduleId: string) {
  await schedules.del(scheduleId);
}
```

The management calls are `create`, `retrieve`, `list`, `update`, `deactivate`, `activate`, `del` and `timezones()` (the list of valid IANA zones, for a dropdown). They need `TRIGGER_SECRET_KEY` (and `TRIGGER_API_URL` on self-hosted) in the environment of the code that makes them. The REST form is in `references/scheduled-tasks.md` in **task-development**.

**The deduplication key is scoped to the project, not to the environment.** Using the same key in production and staging gives one schedule, and the last call decides where it appears. Put the environment name in the key for imperative schedules that exist in several environments, or use a declarative schedule with `environments` for fixed ones.

A schedule's `externalId` is the only thing that ties a run to a user. Treat it as an untrusted lookup key in the run (load the user, check that it still exists and still wants the report), because a schedule outlives the user's settings.

## When a schedule does not fire

- **In dev** a schedule fires only while the `dev` CLI is running. Stop the CLI and the schedule stops.
- **In staging and production** it fires only for a task that is in the **current** deployment. A task that was removed in the newest deploy, or exists only in an older version, is not triggered.
- An imperative schedule that was `deactivate`d, or whose task is not deployed to that environment, does not fire either.
- On a server before 4.6.0 there is no default spread; on 4.6.0 and later a run can start minutes after the cron time (see above). Compare `payload.timestamp` with the run's start time before concluding the schedule is late.
- On the dashboard's **Test schedule** the `scheduleId` is always `sched_1234`.

## Stale runs: `ttl`

A schedule that fires every minute while the previous run is still going queues a run behind it. Give the task a `ttl` so queued runs that nobody dequeued in time expire (status `EXPIRED`) instead of piling up:

```ts
// trigger/frequent-poll.ts
import { schedules } from "@trigger.dev/sdk";

export const frequentPoll = schedules.task({
  id: "frequent-poll",
  cron: "*/5 * * * *",
  ttl: "4m",
  run: async () => {},
});
```

Precedence and the global default are in **task-development** (TTL) and **config-and-build**.

## Idempotent scheduled runs

A scheduled run is retried on failure and can be replayed from the dashboard, so every write must survive repetition.

- **Check, then act.** Key the work on the nominal time and look it up first. `payload.timestamp` is the same on every retry and every replay of one occurrence.
- **Upsert on a natural key** (`report_type` and `date`), not a blind create.
- **Fan-out with idempotency keys.** When the run triggers child tasks, build each key from the item and the occurrence, so a retry of the parent does not start the children twice.

```ts
// trigger/nightly-sync.ts
import { schedules, tasks } from "@trigger.dev/sdk";
import type { syncAccount } from "@/trigger/sync-account";

export const nightlySync = schedules.task({
  id: "nightly-sync",
  cron: "0 2 * * *",
  run: async (payload) => {
    const occurrence = payload.timestamp.toISOString();

    const done = await fetch(`${process.env.RECORDS_API_URL}/sync-runs?occurrence=${encodeURIComponent(occurrence)}`, {
      headers: { Authorization: `Bearer ${process.env.RECORDS_API_TOKEN}` },
    });
    if (!done.ok) throw new Error(`lookup failed: ${done.status}`); // a 4xx is not "nothing found"
    if (((await done.json()) as { data: unknown[] }).data.length > 0) return { skipped: true };

    const accountIds = ["a1", "b2"]; // load them from your system of record
    await tasks.batchTrigger<typeof syncAccount>(
      "sync-account",
      accountIds.map((accountId) => ({
        payload: { accountId },
        options: { idempotencyKey: `sync-${accountId}-${occurrence}` },
      })),
    );
    return { started: accountIds.length };
  },
});
```

`lastTimestamp` is documented as the time of the previous run, not of the last successful one. Do not use it as the only cursor for "what changed since last time": a run that failed leaves a gap. Keep a cursor in the system you write to (the newest `date_updated` you processed) and use `lastTimestamp` as a hint.

## Testing

- **Dashboard:** Tasks page, open the scheduled task, **Test schedule**. It builds a valid payload and lets you pick a recent run to fill it in.
- **Dev:** run `npx trigger.dev@<version> dev`; the declarative schedules of the project fire while it runs.
- **From the MCP `trigger_task` tool or REST:** the payload is plain JSON, so `timestamp` arrives as a string, not a `Date` (not checked against a live server). If a task must survive a manual trigger, read it as `new Date(payload.timestamp)`. The tool is `trigger_task` (`taskId`, `payload`, `environment`, default `dev`); there is no `run_task`.

## Operating schedules

- Enable, disable, edit and delete imperative schedules from the task's **Schedules** tab or the SDK, without a deploy. Declarative ones change only in code.
- Alerts on failed runs are configured per project in the dashboard.
- A deploy creates a new version: runs already started finish on the old one, new occurrences use the new one.

## Anti-patterns

| Don't | Do |
|-------|-----|
| Look for `schedules:attach` or a deploy flag for schedules | Put `cron` on the task; it syncs on `dev` and `deploy` |
| Assume a cron fires at the exact minute on server ≥ 4.6.0 | Set `window: "0m"`, or accept the spread |
| One imperative `deduplicationKey` for every environment | Include the environment in the key |
| A blind create on every run | Check for the occurrence, or upsert on a natural key |
| Trust `lastTimestamp` as the only cursor | Keep your own cursor in the system of record |
| A schedule every minute with no `ttl` on a slow task | `ttl` shorter than the interval |
| Read `payload.externalId` as trusted | Validate it against your data in the run |
