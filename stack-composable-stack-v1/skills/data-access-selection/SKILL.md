---
name: data-access-selection
description: This skill should be used when the user needs to choose how to read or write data in the Composable Stack — "NocoDB MCP or PostgreSQL MCP", "PostgREST or MCP", "which data access should I use", "how should n8n read the database", "how should a Trigger.dev task call PostgreSQL", "complex SQL or simple CRUD", "batch data operation", or is picking between the stack's data-access paths.
---

# Data Access Selection

The Data layer has three ways in. They sit on the same PostgreSQL database, so the choice is about the caller and the job, not about where the data lives.

| Path | What it is | Who calls it |
|------|-----------|--------------|
| **NocoDB MCP** | Record tools with pagination, filters and views on top of the tables | Claude |
| **PostgreSQL MCP** | 29 database tools — SQL, schema inspection, performance, administration | Claude |
| **PostgREST API** | REST endpoints generated from the schema | n8n HTTP Request nodes, Trigger.dev tasks, `curl` |

Tool-level knowledge lives in the technology plugins:

- PostgreSQL MCP tools — see `postgresql-external-dev:postgres-mcp-tools`
- PostgREST (upsert, `Prefer` options, bulk-write guard) — see `postgresql-external-dev:postgrest-api`
- NocoDB MCP tools and filter syntax — see `nocodb-ops:mcp-patterns`

In this plugin the MCP servers are declared in `.mcp.json`, so their tools are named `mcp__plugin_stack-composable-stack-v1_<server>__<tool>` — `nocodb`, `postgresql-mcp`.

## When to Use What

| Need | Use | Why |
|------|-----|-----|
| Simple record CRUD | NocoDB MCP (`mcp__plugin_stack-composable-stack-v1_nocodb__*`) | Higher-level API, pagination, views |
| Complex SQL (JOINs, CTEs, window functions) | PostgreSQL MCP `execute_sql` | Full SQL power |
| Schema inspection and design | PostgreSQL MCP `list_tables` | Detailed constraints, indexes, triggers |
| Query performance analysis | PostgreSQL MCP `get_query_plan` + `list_query_stats` | EXPLAIN plans, execution stats |
| Database administration | PostgreSQL MCP | Roles, extensions, replication, vacuum |
| HTTP CRUD from n8n workflows | PostgREST API | Standard REST from an HTTP Request node, token in a credential |
| HTTP CRUD from Trigger.dev tasks | PostgREST API | Plain `fetch`, no SDK needed |
| Batch data operations | PostgreSQL MCP `execute_sql` | Single SQL with INSERT...SELECT, UPDATE...FROM |
| Mass `PATCH` / `DELETE` built from variable input | PostgREST with `Prefer: handling=strict,max-affected=N` | The server refuses a write that touches more rows than expected |

## Best Practices

- Use NocoDB MCP for everyday record operations — it provides the simplest abstraction
- Use PostgreSQL MCP `execute_sql` for complex queries that would need several NocoDB MCP calls
- Use PostgREST from n8n HTTP Request nodes when you need direct REST access without MCP
- Keep URLs and tokens in environment variables on the Claude side and in credentials on the n8n side (n8n 2.x blocks `$env` in expressions and Code nodes by default) — never hardcode either
- Use `Prefer: return=representation` on POST/PATCH to get the created or updated record back
- Use PostgREST filter operators for simple lookups; use `execute_sql` for complex WHERE clauses
- Run `mcp__plugin_stack-composable-stack-v1_postgresql-mcp__list_table_stats` from time to time to check for table bloat and missing indexes
- After any DDL, sync the platforms that read the database (Meta Sync in NocoDB, refresh in NocoBase) — see `postgresql-external-dev:modify-schema`
