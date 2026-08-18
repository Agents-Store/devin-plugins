---
name: observability
description: Query Trigger.dev data with TRQL, build dashboards, and inspect automatically-tracked LLM metrics. Use when the user asks about "trigger.dev query", "TRQL", "trigger.dev dashboards", "LLM metrics", "llm_metrics table", "how many runs failed this week", "cost per task", "query runs table", "span details", or "metrics table".
---

# Observability — Query, Dashboards, LLM Metrics

Trigger.dev v4.4.4 introduced first-class analytics on top of the runs + spans ClickHouse store: **TRQL** (Trigger.dev Query Language), built-in and custom **dashboards**, and automatic **LLM cost tracking** for GenAI spans.

## When to Use

- Answering "how many runs failed in the last 7d?" style questions
- Tracking LLM cost, token usage, and latency per model or task
- Building dashboards from metrics (CPU, memory, event-loop, heap, custom otel metrics)
- Drilling into a specific run's spans to inspect AI enrichment (model, tokens, cost)

## Data Model

Three tables are exposed via TRQL — all backed by ClickHouse under the hood.

| Table | Contains | Used for |
|-------|----------|----------|
| `runs` | Run status, timing, task identifier, tags, compute cost, output, error | Run-level analytics, failure analysis |
| `metrics` | Process metrics (CPU, memory, event-loop, heap) + custom `otel.metrics` | Infrastructure monitoring, custom gauges/counters |
| `llm_metrics` | LLM token usage, cost (USD), latency, model, finish reason | AI cost / usage analytics |

> **Requires SDK ≥ 4.4.1** for the automatic process + runtime metrics. LLM metrics populate automatically for spans with GenAI semantic conventions (Vercel AI SDK, OpenAI SDK with the Trigger otel instrumentation).

### `metrics` table columns

| Column | Type | Description |
|--------|------|-------------|
| `metric_name` | string | Metric identifier (`process.cpu.utilization`, `process.memory.usage`, custom name) |
| `metric_type` | string | `gauge`, `sum`, or `histogram` |
| `metric_value` | number | The observed value (**note: this is `metric_value`, not `value`** — the v4.4.4 changelog fixed a doc bug) |
| `bucket_start` | datetime | 10-second aggregation bucket start time |
| `run_id` | string | Associated run ID |
| `task_identifier` | string | Task slug |
| `attempt_number` | number | Attempt number |
| `machine_id` / `machine_name` | string | Machine that produced the metric |
| `worker_version` | string | Worker version |
| `environment_type` | string | `PRODUCTION`, `STAGING`, `DEVELOPMENT`, `PREVIEW` |
| `attributes` | json | Raw JSON attributes for custom data — use dot notation |

### Pretty formatting

`prettyFormat(col, type)` — supported types: `bytes`, `percent`, `duration`, `durationSeconds`, `quantity`, `costInDollars`.

```sql
SELECT
  timeBucket(),
  prettyFormat(avg(metric_value), 'bytes') AS avg_memory
FROM metrics
WHERE metric_name = 'process.memory.usage'
GROUP BY timeBucket()
ORDER BY timeBucket()
```

## Three Ways to Run Queries

### 1. MCP-first (recommended for agents)

```
1. get_query_schema(table="runs")    → discover columns
2. query({
     query: "SELECT status, count() FROM runs GROUP BY status",
     period: "7d"
   })                                  → text table result
```

Why MCP first: schema responses are cached server-side since v4.4.4, results come back as compact text tables (~50% fewer tokens than JSON), and the `read:query` JWT scope is handled automatically.

### 2. SDK (backend code)

```ts
import { query, type QueryTable } from "@trigger.dev/sdk";

// Basic query — results are untyped
const result = await query.execute(
  "SELECT run_id, status FROM runs LIMIT 10"
);
console.log(result.results);

// Type-safe query with column inference
type Row = QueryTable<"runs", "run_id" | "status" | "triggered_at">;
const typed = await query.execute<Row>(
  "SELECT run_id, status, triggered_at FROM runs LIMIT 10"
);
typed.results.forEach(r => console.log(r.run_id, r.status));
```

Query options:

```ts
await query.execute("SELECT ...", {
  scope: "project",            // "environment" (default) | "project" | "organization"
  period: "7d",                // shorthand
  // from: new Date("2026-04-01"),
  // to: new Date("2026-04-30"),
  format: "json",              // "json" (default) | "csv"
});
```

### 3. REST API

```bash
curl -X POST "${TRIGGER_API_URL}/api/v1/query" \
  -H "Authorization: Bearer ${TRIGGER_SECRET_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT run_id, status FROM runs LIMIT 10",
    "scope": "environment",
    "period": "7d",
    "format": "json"
  }'
```

## Dashboards

Built-in dashboards ship with widgets for common metrics (runs volume, failure rate, LLM cost, memory). You can also create custom dashboards — each widget is a TRQL query + visualization.

### Widget visualization types

- **Line / Area chart** — trends over time
- **Bar chart** — compare values across categories
- **Table** — detailed rows
- **Single value** — count / sum / average

### MCP-driven flow

```
1. list_dashboards()                                     → dashboardId + widgetIds
2. run_dashboard_query(dashboardId, widgetId, period)    → data
```

### Creating custom dashboards (UI)

1. Sidebar → "+" next to "Dashboards"
2. "Add chart" → write TRQL → pick visualization
3. Resize / reposition widgets

### Limits

- 10 000 rows max per query
- 30 concurrent widget queries per project
- Memory, execution time, and AST complexity limits (`AST too complex` errors)

## Automatic LLM Cost Tracking

Since v4.4.4, spans carrying the GenAI semantic conventions (`gen_ai.system`, `gen_ai.request.model`, token counts) are automatically enriched with cost data from an internal pricing registry. The result:

- Span attributes gain `trigger.llm.cost_usd`, `trigger.llm.input_tokens`, `trigger.llm.output_tokens`, `trigger.llm.model`, `trigger.llm.finish_reason`.
- `get_span_details(runId, spanId)` returns these fields alongside timing.
- A dedicated `llm_metrics_v1` ClickHouse table (surfaced as `llm_metrics` in TRQL) aggregates usage by model, task, and period.

No configuration required — point your AI SDK at the default OpenTelemetry exporter and deploy.

## Scopes and Time Ranges

### Scopes

- `environment` (default) — current environment
- `project` — all envs in the project
- `organization` — all projects in the org

### Period shorthand

`1h`, `6h`, `12h`, `1d`, `7d`, `30d`, `90d`, etc. Prefer the built-in time filter over putting `triggered_at` in the WHERE clause — the filter is applied everywhere the query is executed (dashboard, API, SDK).

## Example Queries

### Failed runs in the last 24 hours

```sql
SELECT task_identifier, run_id, error, triggered_at
FROM runs
WHERE status = 'Failed'
ORDER BY triggered_at DESC
```

Set period = `24h`.

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
ORDER BY day DESC, task_identifier
```

### Top 10 most expensive runs

```sql
SELECT run_id, task_identifier, compute_cost, usage_duration, triggered_at
FROM runs
WHERE compute_cost > 0
ORDER BY compute_cost DESC
LIMIT 10
```

### Daily LLM cost by model

```sql
SELECT
  toDate(bucket_start) AS day,
  model,
  sum(cost_usd)        AS total_cost_usd,
  sum(input_tokens)    AS input_tokens,
  sum(output_tokens)   AS output_tokens
FROM llm_metrics
GROUP BY day, model
ORDER BY day DESC, total_cost_usd DESC
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

## Best Practices

- **Use the built-in time filter** — don't put `triggered_at BETWEEN ...` inside the TRQL string.
- **LIMIT everything** — especially table widgets.
- **Prefer `uniq()` over `uniqExact()`** for large-cardinality counts.
- **Cache your schema** — `get_query_schema(table)` is fast but still a call; fetch once per table, then reuse.
- **Read the `attributes` / `output` / `error` columns with dot notation** (`output.externalId`), not `JSONExtract*` — those are for raw string columns, not the already-JSON columns here.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "AST too complex" | Query too big | Simplify joins, split into multiple queries |
| "Row limit exceeded" | > 10k rows | Add `LIMIT` and a time filter |
| "Concurrent queries exceeded" | Dashboard spam | Stagger widget refresh, reduce dashboard widget count |
| Widget shows "No data" | Filter mismatch | Run the query standalone in the Query page first |
| `metric_value` column missing | Old SDK < 4.4.1 | Upgrade SDK; column is standard in v4.4.4 docs |

## Deeper Reference

- @references/trql-reference.md — full TRQL syntax and function catalogue
- Sibling skills: **mcp-patterns** (query/dashboard MCP tools), **managed-prompts** (prompt versioning)
- Trigger.dev docs: https://trigger.dev/docs/observability/query and /observability/dashboards
