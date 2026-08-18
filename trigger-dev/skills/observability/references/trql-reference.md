# TRQL Reference

Complete syntax and function reference for the Trigger.dev Query Language (TRQL). TRQL is a SQL dialect based on ClickHouse SQL, operating over three tables: `runs`, `metrics`, `llm_metrics`.

## Basic Queries

```sql
SELECT run_id, task_identifier, status
FROM runs
LIMIT 10
```

Alias columns with `AS`:

```sql
SELECT task_identifier AS task, count() AS total
FROM runs
GROUP BY task
```

> **Avoid `SELECT *`** — ClickHouse is columnar; it is cheaper to name the columns you need. `*` returns only the "core" columns to protect you from giant result sets.

## Filtering with WHERE

```sql
-- Comparison
WHERE status = 'Failed'
WHERE status != 'Completed'
WHERE attempt_count >= 3

-- Set membership
WHERE status IN ('Failed', 'Crashed')

-- Pattern matching
WHERE task_identifier LIKE 'email%'
WHERE task_identifier ILIKE '%send%'

-- Range
WHERE triggered_at BETWEEN '2026-04-01' AND '2026-04-30'

-- NULL checks
WHERE completed_at IS NOT NULL
WHERE completed_at IS NULL

-- Array columns (e.g. `tags`)
WHERE has(tags, 'user_12345')
WHERE notEmpty(tags)
WHERE hasAny(tags, array('user_12345', 'user_67890'))
WHERE hasAll(tags, array('user_12345', 'user_67890'))
WHERE indexOf(tags, 'user_12345') > 0
WHERE arrayElement(tags, 1) = 'user_12345'
```

## Sorting and Limiting

```sql
SELECT run_id, compute_cost, triggered_at
FROM runs
ORDER BY compute_cost DESC, triggered_at ASC
LIMIT 50
```

## Grouping and Aggregation

```sql
SELECT
  task_identifier,
  avg(metric_value) AS avg_memory
FROM metrics
WHERE metric_name = 'process.memory.usage'
GROUP BY task_identifier
ORDER BY avg_memory DESC
LIMIT 20
```

## Aggregate Functions

| Function | Meaning |
|----------|---------|
| `count()` | Count rows |
| `countIf(col, cond)` | Count rows matching condition |
| `countDistinct(col)` | Count unique values |
| `uniq(col)` | Approximate unique count (faster for large data) |
| `uniqExact(col)` | Exact unique count |
| `sum(col)` / `sumIf(col, cond)` | Sum / conditional sum |
| `avg(col)` | Average |
| `min(col)` / `max(col)` | Min / max |
| `median(col)` | Median (50th percentile) |
| `quantile(p)(col)` | Percentile (p in 0–1) |
| `stddevPop(col)` / `stddevSamp(col)` | Standard deviations |

Example:

```sql
SELECT
  task_identifier,
  count() AS total_runs,
  avg(usage_duration)           AS avg_duration_ms,
  median(usage_duration)        AS median_duration_ms,
  quantile(0.95)(usage_duration) AS p95_duration_ms
FROM runs
GROUP BY task_identifier
```

## Date / Time Functions

### Time bucketing

```sql
SELECT timeBucket() AS bucket, count() AS runs
FROM runs
GROUP BY bucket
```

`timeBucket()` auto-buckets based on the caller's time range.

### Extraction

```sql
SELECT
  toYear(triggered_at)       AS year,
  toMonth(triggered_at)      AS month,
  toDayOfWeek(triggered_at)  AS dow,
  toHour(triggered_at)       AS hour
FROM runs
```

### Truncation

```sql
SELECT toStartOfDay(triggered_at) AS day, count() AS runs
FROM runs
GROUP BY day
ORDER BY day DESC
```

### Arithmetic

```sql
SELECT dateAdd('day', 7, triggered_at) AS week_later FROM runs

SELECT dateDiff('minute', executed_at, completed_at) AS duration_min
FROM runs
WHERE completed_at IS NOT NULL
```

### Common helpers

- `now()` — current datetime
- `today()` — current date
- `toDate(dt)` — datetime → date
- `toStartOfDay(dt)`, `toStartOfHour(dt)`, `toStartOfMonth(dt)`
- `formatDateTime(dt, format)` — format to string

## String Functions

```sql
SELECT
  lower(status)                               AS status_lower,
  upper(status)                               AS status_upper,
  concat(task_identifier, '-', status)        AS combined,
  substring(run_id, 1, 8)                     AS short_id,
  length(task_identifier)                     AS name_length,
  trim(status)                                AS trimmed,
  replace(status, 'Failed', 'FAIL')           AS replaced,
  startsWith(task_identifier, 'email')        AS is_email_task,
  endsWith(task_identifier, '-batch')         AS is_batch
FROM runs
```

## Conditional Functions

```sql
SELECT
  run_id,
  if(status = 'Failed', 1, 0) AS is_failed,
  multiIf(
    status = 'Completed', 'ok',
    status = 'Failed',    'bad',
    'other'
  ) AS status_category,
  coalesce(completed_at, triggered_at) AS end_time
FROM runs
```

## Math Functions

```sql
SELECT
  round(compute_cost, 4)           AS cost_rounded,
  ceil(usage_duration / 1000)      AS duration_sec_up,
  floor(usage_duration / 1000)     AS duration_sec_down,
  abs(compute_cost)                AS cost_abs
FROM runs
```

## Array Functions

Useful for `tags` and similar array columns:

```sql
SELECT
  run_id,
  tags,
  length(tags)                     AS tag_count,
  has(tags, 'user_12345')          AS is_vip,
  arrayJoin(tags)                  AS individual_tag   -- expands array to rows
FROM runs
WHERE notEmpty(tags)
```

## JSON Columns

`output`, `error`, and `metrics.attributes` are already typed as JSON — use dot notation. **Do not use `JSONExtract*`** — those are for raw string columns.

```sql
SELECT
  run_id,
  output.message     AS message,
  output.count       AS count,
  output.externalId  AS external_id
FROM runs
WHERE task_identifier = 'my-task'
  AND output.externalId = 'something'
ORDER BY triggered_at DESC
LIMIT 100
```

## `prettyFormat`

```sql
SELECT
  timeBucket(),
  prettyFormat(avg(metric_value), 'bytes') AS avg_memory
FROM metrics
WHERE metric_name = 'process.memory.usage'
GROUP BY timeBucket()
```

Formats: `bytes`, `percent`, `duration` (ms), `durationSeconds`, `quantity`, `costInDollars`.

## Scopes

| Scope | Data visible |
|-------|--------------|
| `environment` | Current environment only (default) |
| `project` | All environments in the project |
| `organization` | All projects in the organization |

Set via SDK / REST option, not inside the SQL.

```ts
await query.execute("SELECT environment, count() FROM runs GROUP BY environment", {
  scope: "project",
});
```

## Time ranges

### Period shorthand

```ts
await query.execute("SELECT count() FROM runs", { period: "4d" });
```

Supported: `1h`, `6h`, `12h`, `1d`, `7d`, `30d`, `90d`, etc.

### Explicit dates

```ts
await query.execute("SELECT count() FROM runs", {
  from: new Date("2026-04-01"),
  to:   new Date("2026-04-30"),
});
```

Or unix ms:

```ts
await query.execute("SELECT count() FROM runs", {
  from: Date.now() - 7 * 24 * 60 * 60 * 1000,
  to:   Date.now(),
});
```

Avoid putting `triggered_at BETWEEN ...` inside the TRQL — the built-in time filter is applied uniformly across dashboard / API / SDK callers.

## CSV Export

```ts
const csvResult = await query.execute(
  "SELECT run_id, status, triggered_at FROM runs",
  { format: "csv", period: "7d" }
);

const lines = csvResult.results.split("\n");
console.log(lines[0]); // header row
```

## Limits

| Limit | Value |
|-------|-------|
| Row cap | 10 000 rows per query |
| Concurrency | Per-organization cap (see dashboard quotas) |
| Memory / AST complexity | Enforced server-side — simplify or split queries if exceeded |

See https://trigger.dev/docs/limits for current quotas.

## Example Queries

### Failed runs (last 24h)

```sql
SELECT task_identifier, run_id, error, triggered_at
FROM runs
WHERE status = 'Failed'
ORDER BY triggered_at DESC
```

### Task success rate by day

```sql
SELECT
  toDate(triggered_at) AS day,
  task_identifier,
  countIf(status = 'Completed') AS completed,
  countIf(status = 'Failed')    AS failed,
  round(completed / (completed + failed) * 100, 2) AS success_rate_pct
FROM runs
WHERE status IN ('Completed', 'Failed')
GROUP BY day, task_identifier
ORDER BY day DESC
```

### Top 10 most expensive runs

```sql
SELECT run_id, task_identifier, compute_cost, usage_duration, triggered_at
FROM runs
WHERE compute_cost > 0
ORDER BY compute_cost DESC
LIMIT 10
```

### Average compute duration over time

```sql
SELECT
  timeBucket() AS time,
  task_identifier,
  avg(usage_duration) AS avg_duration_ms,
  count()             AS run_count
FROM runs
WHERE usage_duration IS NOT NULL
GROUP BY time, task_identifier
ORDER BY time ASC
```

### Runs by queue and machine

```sql
SELECT
  queue,
  machine,
  count() AS run_count,
  countIf(status = 'Completed') AS completed,
  countIf(status = 'Failed')    AS failed
FROM runs
GROUP BY queue, machine
ORDER BY queue, machine
```

### CPU utilization over time

```sql
SELECT timeBucket(), avg(metric_value) AS avg_cpu
FROM metrics
WHERE metric_name = 'process.cpu.utilization'
GROUP BY timeBucket()
ORDER BY timeBucket()
LIMIT 1000
```

### Memory usage by task (past 7d)

```sql
SELECT task_identifier, avg(metric_value) AS avg_memory
FROM metrics
WHERE metric_name = 'process.memory.usage'
GROUP BY task_identifier
ORDER BY avg_memory DESC
LIMIT 20
```

### LLM cost by model (last 30d)

```sql
SELECT
  model,
  sum(cost_usd)      AS total_cost_usd,
  sum(input_tokens)  AS input_tokens,
  sum(output_tokens) AS output_tokens,
  count()            AS call_count
FROM llm_metrics
GROUP BY model
ORDER BY total_cost_usd DESC
```

### Available metric names

```sql
SELECT metric_name, count() AS sample_count
FROM metrics
GROUP BY metric_name
ORDER BY sample_count DESC
LIMIT 100
```
