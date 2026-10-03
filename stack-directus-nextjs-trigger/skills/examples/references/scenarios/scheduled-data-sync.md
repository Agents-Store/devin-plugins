# Scenario: Scheduled Data Sync

Every day at 02:00 UTC, pull the latest exchange rates from a rates provider and write them into a Directus collection. A Next.js dashboard reads them from Directus and shows fresh numbers after the sync. The scheduling rules (cron, windows, why a schedule did not fire, idempotent runs) are in `trigger-dev` → `scheduled-tasks`; the Directus side is in `directus-to-trigger`. This file puts them together.

## Flow

```
Trigger.dev fires the schedule at 02:00 UTC
  -> schedules.task "daily-rate-sync": fetch rates, read the existing rows, update or create each pair
  -> the revalidation Flow sees the writes and expires the `exchange_rates` tag
  -> /rates shows the new numbers on the next request
```

## Directus Collection: `exchange_rates`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `base` | String | Base currency code (`USD`) |
| `quote` | String | Quote currency code (`EUR`) |
| `rate` | Decimal | Arrives from the API as a **string**, `"0.9215"`; type it `string` and convert with `Number()` to format |
| `fetched_at` | Datetime | The schedule's occurrence this value belongs to |
| `date_created`, `date_updated` | Timestamp (auto) | System fields |

A rate pair is one row, so `(base, quote)` must be unique. The Data Model UI offers `unique` per field only: create the composite unique index in the database (a migration). With it, two overlapping runs that both try to create a missing pair make one of them fail loudly instead of leaving two rows.

The **task user's** policy reads, creates and updates `exchange_rates` and nothing else. List `exchange_rates` in the revalidation Flow and in `COLLECTION_TAGS` of `/api/revalidate` (`deployment`), so the task's writes refresh the page.

```typescript
// types/directus.ts
export interface ExchangeRate {
  id: string;
  base: string;
  quote: string;
  rate: string; // a decimal field arrives as a string
  fetched_at: string;
  date_created: string;
  date_updated: string | null;
}

export interface Schema {
  exchange_rates: ExchangeRate[];
}
```

## The Scheduled Task

```typescript
// trigger/daily-rate-sync.ts
import { logger, schedules } from '@trigger.dev/sdk';
import { createItem, readItems, updateItem } from '@directus/sdk';
import { getDirectus, requireEnv } from './lib/directus';

const PAIRS = [
  { base: 'USD', quote: 'EUR' },
  { base: 'USD', quote: 'GBP' },
  { base: 'USD', quote: 'JPY' },
  { base: 'EUR', quote: 'GBP' },
] as const;

export const dailyRateSync = schedules.task({
  id: 'daily-rate-sync',
  cron: {
    pattern: '0 2 * * *',
    timezone: 'UTC',
    environments: ['PRODUCTION'], // a developer's `trigger dev` and staging do not fire it
  },
  maxDuration: 300,
  run: async (payload) => {
    const directus = getDirectus();
    const ratesUrl = requireEnv('RATES_API_URL'); // your rates provider; most need a key, add it the same way
    // The occurrence this run belongs to: identical on every retry and replay, so a retry writes the same value
    const occurrence = payload.timestamp.toISOString();

    // One read for all existing rows, keyed by pair, instead of one lookup per pair
    const rows = await directus.request(readItems('exchange_rates', { fields: ['id', 'base', 'quote'], limit: -1 }));
    const existing = new Map(rows.map((row) => [`${row.base}/${row.quote}`, row.id]));

    let created = 0;
    let updated = 0;
    let failed = 0;
    for (const { base, quote } of PAIRS) {
      const res = await fetch(`${ratesUrl}/latest?base=${base}&symbols=${quote}`, { signal: AbortSignal.timeout(15_000) });
      if (!res.ok) {
        logger.error('rates provider failed', { base, quote, status: res.status });
        failed++;
        continue;
      }
      const { rates } = (await res.json()) as { rates?: Record<string, number> };
      const rate = rates?.[quote];
      if (typeof rate !== 'number') {
        logger.error('rates provider sent no rate', { base, quote });
        failed++;
        continue;
      }

      const fields = { rate: String(rate), fetched_at: occurrence };
      const id = existing.get(`${base}/${quote}`);
      if (id) {
        await directus.request(updateItem('exchange_rates', id, fields));
        updated++;
      } else {
        await directus.request(createItem('exchange_rates', { base, quote, ...fields }));
        created++;
      }
    }

    // One bad pair is logged and skipped; a provider that is down for every pair fails the run, so it is retried
    if (failed === PAIRS.length) throw new Error('rates provider failed for every pair');
    logger.info('rate sync done', { created, updated, failed });
    return { created, updated, failed };
  },
});
```

- **A declarative schedule syncs on `dev` and `deploy`.** There is nothing to attach afterwards (`trigger-dev` → `scheduled-tasks`). `environments: ['PRODUCTION']` limits where it fires; without it every environment that has the task fires it.
- **The start can drift.** On server 4.6.0 and later a new schedule is spread over a window after its cron time. For a daily sync that is fine; add `window: '0m'` to the `cron` object for an exact start.
- **Idempotent writes.** A retry finds the rows the first attempt created and updates them. `fetched_at` is the occurrence, not "now", so a retry or a replay of the same day writes the same value.
- **A task that fails halfway is safe to repeat**, because each pair is an upsert and the unique index stops duplicates.
- **Refreshing the page.** The task writes to a collection the revalidation Flow lists, so nothing else is needed. If the Flow does not cover it, call `revalidateSite('exchange_rates')` once at the end (`directus-to-trigger`).

### Environment of the task (Trigger.dev project, per environment)

| Variable | Value |
|----------|-------|
| `DIRECTUS_URL` | Directus address, reachable from the Trigger.dev workers |
| `DIRECTUS_TOKEN` | Static token of the **task** user (read, create, update on `exchange_rates`) |
| `RATES_API_URL` | Base address of the rates provider (plus its key, if it needs one) |

## The Dashboard

The page reads through a tagged read (`directus-to-nextjs` → "Cache"), so it is cached until the tag is expired:

```typescript
// lib/rates.ts
import 'server-only';
import { cache } from 'react';
import { readItems } from '@directus/sdk';
import { requestTagged } from '@/lib/directus-tagged';

const ONE_HOUR = 3600; // safety net: a missed webhook heals itself within the hour

export const getRates = cache(async () =>
  requestTagged(
    readItems('exchange_rates', {
      sort: ['base', 'quote'],
      fields: ['base', 'quote', 'rate', 'fetched_at'],
      limit: -1,
    }),
    ['exchange_rates'],
    ONE_HOUR,
  ),
);
```

```tsx
// app/rates/page.tsx
import { getRates } from '@/lib/rates';

export const metadata = { title: 'Exchange Rates' };

export default async function RatesPage() {
  const rates = await getRates();
  const lastFetched = rates[0]?.fetched_at ? new Date(rates[0].fetched_at).toLocaleString() : 'Never';

  return (
    <main>
      <h1>Exchange Rates</h1>
      <p>Last synced: {lastFetched}</p>
      <table>
        <thead>
          <tr>
            <th>Base</th>
            <th>Quote</th>
            <th>Rate</th>
          </tr>
        </thead>
        <tbody>
          {rates.map((r) => (
            <tr key={`${r.base}-${r.quote}`}>
              <td>{r.base}</td>
              <td>{r.quote}</td>
              <td>{Number(r.rate).toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

## Local Testing

Run `npx trigger.dev dev --env-file .env.trigger.local`, then start the task by hand: the dashboard's **Test schedule** on the task's page, or the MCP `trigger_task` tool with `taskId: "daily-rate-sync"` (a hand-made payload is plain JSON, so `payload.timestamp` arrives as a string: wrap it in `new Date()` if you test that way). The upserts land in the Directus the file points at.

## Verification

- [ ] The task is deployed (`trigger-dev` → `deployment`) and its schedule appears on the task's **Schedules** tab, type declarative, in production only
- [ ] A test run completes and logs `{ created, updated, failed }`
- [ ] `exchange_rates` holds one row per pair, with the occurrence in `fetched_at`
- [ ] `/rates` renders the rates; after a second test run the page shows the new `fetched_at` within seconds
- [ ] Break the provider address for one pair: the run logs the failure, skips that pair and still succeeds; break it for all pairs: the run fails and is retried
- [ ] Run the task twice for the same occurrence: no duplicate rows, the same `fetched_at`

## Variations

- **One task per source.** Separate schedules with their own `cron`; do not fold unrelated syncs into one task.
- **Per-user schedules.** Create them from a Server Action with `schedules.create()` and an `externalId` (`trigger-dev` → `scheduled-tasks`); keep the schedule id next to the user in Directus.
- **Hourly or every 15 minutes.** `cron: '0 * * * *'`, `'*/15 * * * *'`; the finest schedule is one minute. Give a frequent task a `ttl` shorter than its interval.
- **A calendar timezone.** `timezone: 'America/New_York'` for a market's hours; it follows daylight saving.
