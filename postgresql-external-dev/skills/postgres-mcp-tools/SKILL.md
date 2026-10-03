---
name: postgres-mcp-tools
description: This skill should be used when the user wants to "run SQL through MCP", "use the PostgreSQL MCP tools", "execute_sql", "inspect a database schema over MCP", "list indexes, locks or bloated tables", "analyze query performance with MCP", "check database status", "get a query plan", "MCP Toolbox for Databases", or needs the tool reference of the 29-tool PostgreSQL MCP server for querying and administering a PostgreSQL database.
---

# PostgreSQL MCP Tools

Tool reference for a PostgreSQL MCP server: run SQL, inspect schemas, and watch performance and replication from an agent. Use it next to the schema skills of this plugin — `create-tables`, `modify-schema`, `relations` decide **what** SQL to write; this skill is **how** to run and inspect it over MCP. For REST access to the same database, see `postgrest-api`.

## The Server

The 29 tools below are the prebuilt `postgres` tool set of **MCP Toolbox for Databases** (Google, open source; the repository was `googleapis/genai-toolbox` and is now `googleapis/mcp-toolbox`). Checked on 2026-10-02 against release v1.13.1 and a live server: 29 tools. The set changes between releases — list the tools your server exposes before relying on one, and read the project's `UPGRADING.md` when you move a major version.

This plugin ships no `.mcp.json`: the connection is yours to configure (Toolbox over HTTP, with a bearer token if you put it behind a gateway). Tool names are therefore written in the bare form `mcp__<server>__<tool>`, where `<server>` is the name you gave the connection — `postgresql-mcp` in the examples. When the server is connected through the `stack-composable-stack-v1` plugin, its tools are `mcp__plugin_stack-composable-stack-v1_postgresql-mcp__<tool>`.

Credentials and URLs come from environment variables (`${POSTGRESQL_MCP_URL}`, `${POSTGRESQL_MCP_TOKEN}` in the stack) — never write a host or token into a file.

## Query & SQL

### Execute SQL

Runs **one** SQL statement — SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP. It runs with the rights of the database user behind the server, so treat every call as a possible write.

```
Tool: mcp__postgresql-mcp__execute_sql
Input: { "sql": "SELECT * FROM orders WHERE status = 'pending' LIMIT 10" }
```

```
Tool: mcp__postgresql-mcp__execute_sql
Input: { "sql": "CREATE TABLE orders (id serial PRIMARY KEY, title text NOT NULL, status text DEFAULT 'pending', created_at timestamp DEFAULT now(), updated_at timestamp DEFAULT now())" }
```

- One statement per call. For a multi-step change, make one call per step, in the order given in `modify-schema` (**Safe Modification Order**)
- Before `DROP`, `TRUNCATE` or a `DELETE`/`UPDATE` without a tight `WHERE`: get the user's confirmation of the exact object and take a backup — see **Before You Drop Anything** in `modify-schema`
- After DDL, sync the platforms that read this database (Meta Sync in NocoDB, refresh in NocoBase) — `modify-schema` has the steps

### Get Query Plan

Generates the planner's `EXPLAIN` in JSON **without executing** the statement (no `ANALYZE`). Safe on production. Omit the `EXPLAIN` keyword.

```
Tool: mcp__postgresql-mcp__get_query_plan
Input: { "query": "SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = 'pending'" }
```

## Schema Inspection

### List Tables

Detailed schema info as JSON: columns, constraints, indexes, triggers, owner, comments.

```
Tool: mcp__postgresql-mcp__list_tables
```

Filter specific tables:

```
Tool: mcp__postgresql-mcp__list_tables
Input: { "table_names": "orders,customers", "output_format": "detailed" }
```

Names only:

```
Tool: mcp__postgresql-mcp__list_tables
Input: { "output_format": "simple" }
```

### List Views

```
Tool: mcp__postgresql-mcp__list_views
Input: { "view_name": "active_orders" }
```

Optional: `schema_name`, `limit` (default 50).

### List Indexes

```
Tool: mcp__postgresql-mcp__list_indexes
Input: { "table_name": "orders" }
```

Find indexes that were never used:

```
Tool: mcp__postgresql-mcp__list_indexes
Input: { "only_unused": true }
```

Other filters: `schema_name`, `index_name` (both `LIKE`), `limit` (default 50).

### List Schemas

Schema name, owner, grants, function/table/view counts. Default `limit` is 10.

```
Tool: mcp__postgresql-mcp__list_schemas
```

### Other Schema Tools

| Tool | Use For |
|------|---------|
| `list_sequences` | Sequence objects (auto-increment counters) |
| `list_triggers` | Database triggers with timing, events, handler functions |
| `list_stored_procedure` | Stored procedures/functions with definitions |
| `get_column_cardinality` | Estimated unique values per column (run `ANALYZE` first) |
| `list_invalid_indexes` | Broken indexes from a failed `CREATE INDEX CONCURRENTLY` |

## Performance & Monitoring

### Database Overview

Server version, replica flag, uptime, connection limit, current and active connections, percent of connections in use.

```
Tool: mcp__postgresql-mcp__database_overview
```

### Table Statistics

Row counts, sizes, sequential versus index scans (a low `idx_scan_ratio_percent` hints at a missing index), dead tuples, vacuum times. Default schema is `public`.

```
Tool: mcp__postgresql-mcp__list_table_stats
Input: { "table_name": "orders" }
```

### Query Statistics

Needs the `pg_stat_statements` extension. Execution counts, timing, buffer hits and reads, ordered by total time.

```
Tool: mcp__postgresql-mcp__list_query_stats
Input: { "limit": 20 }
```

### Active Queries

Running queries, longest first. `min_duration` defaults to one minute — lower it to see short ones.

```
Tool: mcp__postgresql-mcp__list_active_queries
Input: { "min_duration": "1 second" }
```

### Other Monitoring Tools

| Tool | Use For |
|------|---------|
| `long_running_transactions` | Transactions exceeding a time limit (`min_duration`, default 5 minutes) |
| `list_top_bloated_tables` | Tables with high dead-tuple count (bloat signal) |
| `list_locks` | All locks held by active processes |
| `list_database_stats` | Cache hit ratio, transaction counts, temp files, deadlocks |

## Server Configuration

| Tool | Use For |
|------|---------|
| `list_pg_settings` | PostgreSQL config parameters (filter by `setting_name`) |
| `list_memory_configurations` | Memory-related settings (`shared_buffers`, `work_mem`, …) |
| `list_autovacuum_configurations` | Autovacuum settings |

## Extensions

| Tool | Use For |
|------|---------|
| `list_installed_extensions` | Currently installed extensions with versions |
| `list_available_extensions` | All extensions available for installation |

## Replication & Infrastructure

| Tool | Use For |
|------|---------|
| `replication_stats` | Replica lag sizes (sent/write/flush/replay) |
| `list_replication_slots` | Replication slot details and WAL retention |
| `list_roles` | User-created roles with privileges (filter by `role_name`) |
| `list_tablespaces` | Tablespace names, owners, sizes |
| `list_publication_tables` | Logical replication publications |

## Tool Count

29 tools: `execute_sql`, `get_query_plan` (2); `list_tables`, `list_views`, `list_indexes`, `list_schemas`, `list_sequences`, `list_triggers`, `list_stored_procedure`, `get_column_cardinality`, `list_invalid_indexes` (9); `database_overview`, `list_table_stats`, `list_query_stats`, `list_active_queries`, `long_running_transactions`, `list_top_bloated_tables`, `list_locks`, `list_database_stats` (8); `list_pg_settings`, `list_memory_configurations`, `list_autovacuum_configurations` (3); `list_installed_extensions`, `list_available_extensions` (2); `replication_stats`, `list_replication_slots`, `list_roles`, `list_tablespaces`, `list_publication_tables` (5).

## Best Practices

- Start with `list_tables` (or `database_overview`) to see what is actually there before writing SQL
- Prefer `execute_sql` for anything that would take several higher-level calls — JOINs, CTEs, window functions, `INSERT … SELECT`, `UPDATE … FROM`
- Run `get_query_plan` before a heavy query, `list_table_stats` now and then to catch bloat and missing indexes
- Keep the MCP database user as narrow as the job needs; a read-only role makes every inspection tool safe by construction
- Use `postgrest-api` instead when the caller is an HTTP client (n8n HTTP Request node, a background task) and no MCP is available
