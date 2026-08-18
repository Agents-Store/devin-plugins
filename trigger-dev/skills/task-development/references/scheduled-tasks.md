# Scheduled Tasks (Cron)

## Declarative Schedule

Define the cron pattern directly on the task:

```ts
import { schedules } from "@trigger.dev/sdk";

export const dailyCleanup = schedules.task({
  id: "daily-cleanup",
  cron: "0 0 * * *",  // Midnight UTC
  run: async (payload) => {
    // payload.timestamp  — scheduled time
    // payload.timezone   — IANA timezone
    // payload.scheduleId — schedule identifier
  },
});
```

## With Timezone

```ts
export const tokyoMorning = schedules.task({
  id: "tokyo-morning",
  cron: { pattern: "0 9 * * *", timezone: "Asia/Tokyo" },
  run: async () => {},
});
```

## Dynamic / Multi-Tenant Schedules

Create schedules programmatically via the SDK:

```ts
import { schedules } from "@trigger.dev/sdk";

// Create a schedule
await schedules.create({
  task: "reminder-task",
  cron: "0 8 * * *",
  timezone: "America/New_York",
  externalId: userId,
  deduplicationKey: `${userId}-daily`,
});

// List schedules
const all = await schedules.list({ task: "reminder-task" });

// Delete a schedule
await schedules.del(scheduleId);
```

## Common Cron Expressions

| Schedule | Cron |
|----------|------|
| Every minute | `* * * * *` |
| Every 5 minutes | `*/5 * * * *` |
| Every hour | `0 * * * *` |
| Every 6 hours | `0 */6 * * *` |
| Daily at midnight | `0 0 * * *` |
| Daily at 9 AM | `0 9 * * *` |
| Monday at 9 AM | `0 9 * * 1` |
| Weekdays at 9 AM | `0 9 * * 1-5` |
| 1st of each month | `0 0 1 * *` |
| Quarterly | `0 0 1 1,4,7,10 *` |

## REST API Schedule Management

```bash
# Create schedule
curl -X POST "${TRIGGER_API_URL}/api/v1/schedules" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "daily-report",
    "cron": "0 9 * * *",
    "externalId": "report-daily",
    "deduplicationKey": "report-daily"
  }'

# List schedules
curl "${TRIGGER_API_URL}/api/v1/schedules" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}"
```
