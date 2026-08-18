---
name: postgresql-api
description: This skill should be used when the user wants to "query PostgreSQL directly", "use PostgREST API", "make REST calls to PostgreSQL", "use postgresql-mcp tools", "run SQL via MCP", "check database status", "inspect database schema", "analyze query performance", or needs to perform direct database operations via PostgreSQL MCP tools or PostgREST REST API in the Composable Stack.
---

# PostgreSQL MCP + PostgREST API

Two ways to interact with PostgreSQL directly in the Composable Stack:
- **PostgreSQL MCP** (`postgresql-mcp`) — 27 database administration and query tools via MCP
- **PostgREST API** — REST CRUD endpoints auto-generated from PostgreSQL schema, used from n8n/Trigger.dev/curl

## PostgreSQL MCP Tools

MCP server ID: `postgresql-mcp` (Supabase Toolbox v0.31.0)
Tool prefix: `mcp__postgresql-mcp__`

### Query & SQL

#### Execute SQL

Run any single SQL statement — SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP.

```
Tool: mcp__postgresql-mcp__execute_sql
Input: { "sql": "SELECT * FROM orders WHERE status = 'pending' LIMIT 10" }
```

```
Tool: mcp__postgresql-mcp__execute_sql
Input: { "sql": "CREATE TABLE orders (id SERIAL PRIMARY KEY, title TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now())" }
```

#### Get Query Plan

Generate EXPLAIN plan in JSON without executing the query. Safe for production use.

```
Tool: mcp__postgresql-mcp__get_query_plan
Input: { "query": "SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = 'pending'" }
```

### Schema Inspection

#### List Tables

Detailed schema info: columns, constraints, indexes, triggers, owner, comments.

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

#### List Views

```
Tool: mcp__postgresql-mcp__list_views
Input: { "view_name": "active_orders" }
```

#### List Indexes

```
Tool: mcp__postgresql-mcp__list_indexes
Input: { "table_name": "orders" }
```

Find unused indexes:

```
Tool: mcp__postgresql-mcp__list_indexes
Input: { "only_unused": true }
```

#### List Schemas

Returns schema name, owner, grants, function/table/view counts.

```
Tool: mcp__postgresql-mcp__list_schemas
```

#### Other Schema Tools

| Tool | Use For |
|------|---------|
| `list_sequences` | Sequence objects (auto-increment counters) |
| `list_triggers` | Database triggers with timing, events, handler functions |
| `list_stored_procedure` | Stored procedures/functions with definitions |
| `get_column_cardinality` | Estimated unique values per column (run ANALYZE first) |
| `list_invalid_indexes` | Broken indexes from failed CREATE INDEX CONCURRENTLY |

### Performance & Monitoring

#### Database Overview

Server version, uptime, connection counts, replica status.

```
Tool: mcp__postgresql-mcp__database_overview
```

#### Table Statistics

Row counts, sizes, scan ratios, dead tuples, vacuum times.

```
Tool: mcp__postgresql-mcp__list_table_stats
Input: { "table_name": "orders" }
```

#### Query Statistics

Requires `pg_stat_statements` extension. Execution counts, timing, buffer stats.

```
Tool: mcp__postgresql-mcp__list_query_stats
Input: { "limit": 20 }
```

#### Active Queries

Currently running queries ordered by duration.

```
Tool: mcp__postgresql-mcp__list_active_queries
Input: { "min_duration": "1 second" }
```

#### Other Monitoring Tools

| Tool | Use For |
|------|---------|
| `long_running_transactions` | Transactions exceeding time limit (default 5 min) |
| `list_top_bloated_tables` | Tables with high dead-tuple count (bloat signal) |
| `list_locks` | All locks held by active processes |
| `list_database_stats` | Cache hit ratio, transaction counts, temp files, deadlocks |

### Server Configuration

| Tool | Use For |
|------|---------|
| `list_pg_settings` | All PostgreSQL config parameters (filter by `setting_name`) |
| `list_memory_configurations` | Memory-related settings (shared_buffers, work_mem, etc.) |
| `list_autovacuum_configurations` | Autovacuum settings |

### Extensions

| Tool | Use For |
|------|---------|
| `list_installed_extensions` | Currently installed extensions with versions |
| `list_available_extensions` | All extensions available for installation |

### Replication & Infrastructure

| Tool | Use For |
|------|---------|
| `replication_stats` | Replica lag sizes (sent/write/flush/replay) |
| `list_replication_slots` | Replication slot details and WAL retention |
| `list_roles` | User-created roles with privileges (filter by `role_name`) |
| `list_tablespaces` | Tablespace names, owners, sizes |
| `list_publication_tables` | Logical replication publications |

---

## PostgREST API (v14.8)

REST API auto-generated from PostgreSQL schema. Endpoints are created dynamically for each table and function in the public schema.

**Base URL:** `${POSTGRESQL_API_URL}`
**Auth:** `Authorization: Bearer ${POSTGRESQL_API_TOKEN}`

### CRUD Operations

#### Read Records (GET)

```bash
# All records
curl "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"

# Select specific columns
curl "${POSTGRESQL_API_URL}/orders?select=id,title,status" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"

# Filter records
curl "${POSTGRESQL_API_URL}/orders?status=eq.pending&amount=gt.100" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"

# Order and paginate
curl "${POSTGRESQL_API_URL}/orders?order=created_at.desc&limit=20&offset=0" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"
```

#### Create Records (POST)

```bash
# Single record
curl -X POST "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"title": "New Order", "status": "pending"}'

# Bulk insert
curl -X POST "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{"title": "Order 1"}, {"title": "Order 2"}]'
```

#### Update Records (PATCH)

```bash
# Update by filter
curl -X PATCH "${POSTGRESQL_API_URL}/orders?id=eq.123" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"status": "completed"}'
```

#### Delete Records (DELETE)

```bash
curl -X DELETE "${POSTGRESQL_API_URL}/orders?id=eq.123" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"
```

#### Upsert (POST with conflict resolution)

```bash
curl -X POST "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates,return=representation" \
  -H "on_conflict: id" \
  -d '{"id": 123, "title": "Updated Order", "status": "active"}'
```

#### Call Stored Functions (RPC)

```bash
curl -X POST "${POSTGRESQL_API_URL}/rpc/calculate_total" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123}'
```

### Filtering Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `?status=eq.active` |
| `neq` | Not equals | `?status=neq.deleted` |
| `gt` | Greater than | `?amount=gt.100` |
| `gte` | Greater or equal | `?amount=gte.100` |
| `lt` | Less than | `?amount=lt.50` |
| `lte` | Less or equal | `?amount=lte.50` |
| `like` | LIKE pattern | `?name=like.*john*` |
| `ilike` | Case-insensitive LIKE | `?name=ilike.*john*` |
| `in` | In list | `?status=in.(active,pending)` |
| `is` | IS (null, true, false) | `?deleted_at=is.null` |
| `not` | Negate | `?status=not.eq.deleted` |
| `cs` | Contains (arrays/JSON) | `?tags=cs.{urgent}` |
| `cd` | Contained by | `?tags=cd.{urgent,important}` |

### Prefer Header Options

| Value | Effect |
|-------|--------|
| `return=representation` | Return created/updated records in response |
| `return=minimal` | Return only status code |
| `return=none` | No response body |
| `resolution=ignore-duplicates` | Skip conflicting rows on insert |
| `resolution=merge-duplicates` | Upsert — update existing, insert new |
| `count=exact` | Include exact row count in Content-Range header |

### PostgREST in n8n Workflows

Use HTTP Request node:

```
Method: GET / POST / PATCH / DELETE
URL: {{ $env.POSTGRESQL_API_URL }}/orders
Headers:
  Authorization: Bearer {{ $env.POSTGRESQL_API_TOKEN }}
  Content-Type: application/json
  Prefer: return=representation
```

### PostgREST in Trigger.dev Tasks

```typescript
const response = await fetch(
  `${process.env.POSTGRESQL_API_URL}/orders?status=eq.pending&limit=50`,
  {
    headers: {
      'Authorization': `Bearer ${process.env.POSTGRESQL_API_TOKEN}`,
      'Content-Type': 'application/json',
    },
  }
);
const orders = await response.json();
```

---

## When to Use What

| Need | Use | Why |
|------|-----|-----|
| Simple record CRUD | NocoDB MCP (`mcp__nocodb__*`) | Higher-level API, pagination, views |
| Complex SQL (JOINs, CTEs, window functions) | PostgreSQL MCP `execute_sql` | Full SQL power |
| Schema inspection and design | PostgreSQL MCP `list_tables` | Detailed constraints, indexes, triggers |
| Query performance analysis | PostgreSQL MCP `get_query_plan` + `list_query_stats` | EXPLAIN plans, execution stats |
| Database administration | PostgreSQL MCP | Roles, extensions, replication, vacuum |
| HTTP CRUD from n8n workflows | PostgREST API | Standard REST, no MCP needed in Code nodes |
| HTTP CRUD from Trigger.dev tasks | PostgREST API | Simple fetch calls, no SDK needed |
| Batch data operations | PostgreSQL MCP `execute_sql` | Single SQL with INSERT...SELECT, UPDATE...FROM |

## Best Practices

- Use NocoDB MCP for everyday record operations — it provides the simplest abstraction
- Use PostgreSQL MCP `execute_sql` for complex queries that would require multiple NocoDB MCP calls
- Use PostgREST API from n8n HTTP Request nodes when you need direct REST access without MCP
- Always use `${POSTGRESQL_API_URL}` and `${POSTGRESQL_API_TOKEN}` env vars — never hardcode URLs or tokens
- Use `Prefer: return=representation` on POST/PATCH to get the created/updated record back
- Use PostgREST filtering operators for simple lookups; use `execute_sql` for complex WHERE clauses
- Run `mcp__postgresql-mcp__list_table_stats` periodically to check for table bloat and missing indexes
