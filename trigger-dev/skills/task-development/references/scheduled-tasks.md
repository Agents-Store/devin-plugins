# Scheduled Tasks (Cron)

Declarative schedules (`cron` on `schedules.task`), cron syntax, timezones, the spread window, per-user schedules through `schedules.create()`, idempotent scheduled runs, testing and "why did my schedule not fire" are in the **scheduled-tasks** skill. This file keeps the REST form of the schedule calls.

## REST API Schedule Management

```bash
# Create schedule (the task must already exist and be a schedules.task)
curl -X POST "${TRIGGER_API_URL}/api/v1/schedules" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "daily-report",
    "cron": "0 9 * * *",
    "timezone": "Europe/Berlin",
    "externalId": "report-daily",
    "deduplicationKey": "report-daily"
  }'

# List schedules
curl "${TRIGGER_API_URL}/api/v1/schedules" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}"
```

`deduplicationKey` is required and is scoped to the project, not the environment: a second request with the same key updates the schedule. The SDK equivalents are `schedules.create()`, `schedules.list()`, `schedules.update()`, `schedules.del()`, `schedules.deactivate()` and `schedules.activate()`.
