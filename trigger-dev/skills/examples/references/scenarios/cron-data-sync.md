# Scenario: Cron Data Sync

Scheduled data synchronization with batch processing and error handling.

## Task Definitions

```ts
// src/trigger/data-sync.ts
import { task, schedules, queue, metadata, retry } from "@trigger.dev/sdk";

const syncQueue = queue({
  name: "data-sync",
  concurrencyLimit: 3,
});

// Individual record sync
export const syncRecord = task({
  id: "sync-record",
  queue: syncQueue,
  retry: {
    maxAttempts: 3,
    factor: 2,
    minTimeoutInMs: 1000,
    maxTimeoutInMs: 10000,
  },
  run: async (payload: { id: string; source: string }) => {
    // Fetch from source
    const data = await retry.fetch(`https://api.example.com/records/${payload.id}`, {
      retry: { maxAttempts: 3, condition: (res) => res?.status === 429 || res?.status >= 500 },
    });
    const record = await data.json();

    // Transform and save to destination
    await saveToDatabase(record);

    return { id: payload.id, synced: true };
  },
});

// Main sync orchestrator (runs every hour)
export const hourlySync = schedules.task({
  id: "hourly-data-sync",
  cron: "0 * * * *",  // Every hour
  machine: { preset: "small-2x" },
  run: async (payload) => {
    console.log(`Starting sync at ${payload.timestamp}`);
    metadata.set("status", "fetching");

    // Fetch records that need syncing
    const response = await fetch("https://api.example.com/records?modified_since=1h");
    const records: { id: string }[] = await response.json();

    if (records.length === 0) {
      metadata.set("status", "no_changes");
      return { synced: 0, total: 0 };
    }

    metadata.set("status", "syncing");
    metadata.set("total", records.length);

    // Batch sync all records in parallel
    const results = await syncRecord.batchTriggerAndWait(
      records.map(r => ({ payload: { id: r.id, source: "api" } }))
    );

    const succeeded = results.filter(r => r.ok).length;
    const failed = results.filter(r => !r.ok);

    if (failed.length > 0) {
      console.error(`${failed.length} records failed to sync`);
      for (const f of failed) {
        console.error(`Failed: ${JSON.stringify(f.error)}`);
      }
    }

    metadata.set("status", "completed");

    return {
      synced: succeeded,
      failed: failed.length,
      total: records.length,
      timestamp: payload.timestamp,
    };
  },
});

async function saveToDatabase(record: any) {
  // Your database save logic here
}
```

## trigger.config.ts

```ts
import { defineConfig } from "@trigger.dev/sdk";
import { prismaExtension } from "@trigger.dev/build/extensions/prisma";

export default defineConfig({
  project: "proj_xxxxx",
  dirs: ["./src/trigger"],
  build: {
    extensions: [
      prismaExtension({ schema: "prisma/schema.prisma", migrate: true }),
    ],
  },
});
```

## Monitoring via MCP

```
# Check recent sync runs
list_runs(taskIdentifier="hourly-data-sync", period="1d", limit=24)

# Check for failures
list_runs(status="FAILED", taskIdentifier="sync-record", period="1d")

# Get details of a failed sync
get_run_details(runId="run_xxx")
```

## Dynamic Schedule (multi-tenant)

```ts
// Create per-customer sync schedules
await schedules.create({
  task: "hourly-data-sync",
  cron: "0 * * * *",
  externalId: customerId,
  deduplicationKey: `${customerId}-hourly`,
});
```
