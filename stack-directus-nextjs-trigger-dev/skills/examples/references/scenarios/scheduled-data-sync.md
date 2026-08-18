# Scenario: Scheduled Data Sync

Every day at 02:00 UTC, pull the latest currency exchange rates from a public API and upsert them into a Directus collection. A Next.js dashboard reads from Directus and revalidates after the sync finishes.

## Flow

```
Trigger.dev scheduler fires at 02:00 UTC
    ↓
schedules.task("daily-rate-sync"):
  - fetch rates from external API
  - upsert each rate into Directus (createItem or updateItem)
  - POST /api/revalidate to invalidate the dashboard route
    ↓
Dashboard at /rates shows fresh data on next render
```

## Directus Collection

### `exchange_rates`

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `base` | String | Base currency code (e.g. `USD`) |
| `quote` | String | Quote currency code (e.g. `EUR`) |
| `rate` | Decimal | Exchange rate value |
| `fetched_at` | Datetime | When the rate was pulled |
| `date_created` | Timestamp (auto) | First insert |
| `date_updated` | Timestamp (auto) | Last update |

Add a composite unique index on `(base, quote)` so upserts work.

Grant the API token role read + create + update on `exchange_rates`.

## Trigger.dev Scheduled Task

```typescript
// trigger/daily-rate-sync.ts
import { schedules, logger } from '@trigger.dev/sdk/v3';
import { createDirectus, rest, staticToken, readItems, createItem, updateItem } from '@directus/sdk';
import type { Schema } from '@/types/directus';

// Major currency pairs to sync
const PAIRS = [
  { base: 'USD', quote: 'EUR' },
  { base: 'USD', quote: 'GBP' },
  { base: 'USD', quote: 'JPY' },
  { base: 'EUR', quote: 'GBP' },
];

export const dailyRateSyncTask = schedules.task({
  id: 'daily-rate-sync',
  // Every day at 02:00 UTC
  cron: {
    pattern: '0 2 * * *',
    timezone: 'UTC',
  },
  maxDuration: 300,
  run: async (payload, { ctx }) => {
    logger.log('Starting daily rate sync', { runAt: payload.timestamp });

    const directus = createDirectus<Schema>(process.env.NEXT_PUBLIC_DIRECTUS_URL!)
      .with(staticToken(process.env.DIRECTUS_ADMIN_TOKEN!))
      .with(rest({ cache: 'no-store' }));

    let updated = 0;
    let created = 0;
    const fetchedAt = new Date().toISOString();

    for (const pair of PAIRS) {
      // 1. Fetch from external API (example using exchangerate.host)
      const res = await fetch(
        `https://api.exchangerate.host/latest?base=${pair.base}&symbols=${pair.quote}`
      );
      if (!res.ok) {
        logger.error('API fetch failed', { pair, status: res.status });
        continue;
      }
      const data = (await res.json()) as { rates: Record<string, number> };
      const rate = data.rates[pair.quote];

      // 2. Check if this pair exists in Directus
      const existing = await directus.request(
        readItems('exchange_rates', {
          filter: {
            base: { _eq: pair.base },
            quote: { _eq: pair.quote },
          },
          limit: 1,
        })
      );

      // 3. Upsert
      if (existing.length > 0) {
        await directus.request(
          updateItem('exchange_rates', existing[0].id, {
            rate,
            fetched_at: fetchedAt,
          })
        );
        updated++;
      } else {
        await directus.request(
          createItem('exchange_rates', {
            base: pair.base,
            quote: pair.quote,
            rate,
            fetched_at: fetchedAt,
          })
        );
        created++;
      }
    }

    // 4. Revalidate the Next.js dashboard
    await fetch(
      `${process.env.NEXT_PUBLIC_SITE_URL}/api/revalidate?secret=${process.env.REVALIDATION_SECRET}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ collection: 'exchange_rates' }),
      }
    );

    logger.log('Daily rate sync complete', { created, updated, pairs: PAIRS.length });
    return { created, updated, pairs: PAIRS.length };
  },
});
```

## Attach the Schedule to an Environment

After deploying the task (`npx trigger.dev@latest deploy --self-hosted --profile prod`), go to the Trigger.dev dashboard → Schedules → `daily-rate-sync` → Attach to environment → select **Production**.

Alternatively, use the CLI:

```bash
npx trigger.dev@latest schedules:attach daily-rate-sync --env prod
```

Schedules are NOT attached by default after deploy — this is a deliberate guard against accidentally running production crons in dev.

## Next.js Dashboard

```typescript
// app/rates/page.tsx
import directus from '@/lib/directus';
import { readItems } from '@directus/sdk';

// This page will be revalidated on-demand when the task finishes,
// and at most every hour as a safety fallback.
export const revalidate = 3600;

export const metadata = {
  title: 'Exchange Rates',
};

export default async function RatesPage() {
  const rates = await directus.request(
    readItems('exchange_rates', {
      sort: ['base', 'quote'],
      fields: ['base', 'quote', 'rate', 'fetched_at'],
    })
  );

  const lastFetched = rates[0]?.fetched_at
    ? new Date(rates[0].fetched_at).toLocaleString()
    : 'Never';

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
              <td>{r.rate.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
```

## Environment Variables in Trigger.dev Dashboard

Set in Trigger.dev dashboard → Production env vars:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_DIRECTUS_URL` | Production Directus URL |
| `DIRECTUS_ADMIN_TOKEN` | Token with read + create + update on `exchange_rates` |
| `NEXT_PUBLIC_SITE_URL` | Production Next.js URL |
| `REVALIDATION_SECRET` | Same secret used by `/api/revalidate` |

## Local Testing

Run the task on-demand from the Trigger dev server without waiting for 02:00:

```bash
npx trigger.dev@latest dev
```

Then in the dashboard UI (or via MCP): test-run the task with a fake schedule payload. The dev server executes it against local env vars, so the upsert lands in your dev Directus instance.

## Verification

- [ ] Task deployed (`npx trigger.dev@latest deploy --self-hosted`)
- [ ] Schedule attached to production environment
- [ ] Test-run from dashboard: task completes successfully, logs show `{ created, updated, pairs }`
- [ ] `exchange_rates` in Directus has one row per pair with today's `fetched_at`
- [ ] `/rates` page renders the rates
- [ ] After next scheduled run (or a second manual test), `date_updated` on each row advances
- [ ] `/api/revalidate` receives a POST after the task; next `/rates` fetch shows the new `fetched_at`
- [ ] Disable a pair's external API access — task logs the error and skips that pair without failing the whole run

## Variations

- **Multiple schedules** — define one task per data source, each with its own `cron` pattern. Don't cram unrelated syncs into one task.
- **Dynamic schedules** — create schedules from a Server Action via `schedules.create()` when a user configures a new sync source. Store the schedule ID in Directus so you can disable/delete it later.
- **Hourly instead of daily** — `cron: '0 * * * *'` for every hour, `'*/15 * * * *'` for every 15 minutes. Do not use sub-minute crons — Trigger.dev enforces minimums.
- **Timezone-aware** — set `cron.timezone: 'America/New_York'` to run based on a market timezone instead of UTC.
