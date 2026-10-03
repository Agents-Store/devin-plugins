---
name: postgrest-api
description: This skill should be used when the user wants to "use PostgREST", "make REST calls to PostgreSQL", "CRUD over HTTP on a PostgreSQL table", "upsert with on_conflict", "Prefer header options", "return=representation", "max-affected", "call a stored function over REST", "read PostgreSQL from an n8n HTTP Request node", or "read PostgreSQL from a Trigger.dev task with fetch".
---

# PostgREST API

PostgREST turns a PostgreSQL schema into a REST API: every table and view in an exposed schema gets endpoints, every function becomes `/rpc/<name>`. Use it when the caller is an HTTP client — an n8n HTTP Request node, a background task, `curl` — and an MCP connection is not available or not wanted. For SQL, schema inspection and administration over MCP, see `postgres-mcp-tools`. Tables you design with this plugin's `create-tables` and `relations` skills are served as they are.

**Version.** This reference was run against PostgREST 16.3 (16.4 was current on 2026-10-02) and applies to 14–16. Do not hardcode a version: the server names itself in the `Server` response header (`Server: postgrest/16.3`), and `GET /` returns the OpenAPI description of what the current role can reach. PostgREST 16 needs PostgreSQL 14 or later, and changes two things you may meet in an old config — see **Upgrading to 16**.

**Base URL:** `${POSTGRESQL_API_URL}` (no trailing slash)
**Auth:** `Authorization: Bearer ${POSTGRESQL_API_TOKEN}`

## How Access Works

A request runs as the PostgreSQL role named in the JWT `role` claim; with no token it runs as the configured anonymous role. Table and function `GRANT`s are the permission model — a missing grant answers `401` for the anonymous role and `403` for an authenticated one, with PostgreSQL code `42501` (`permission denied for table …`); it is not a PostgREST setting. After you change the schema (new table, column, grant), PostgREST must reload its schema cache (`NOTIFY pgrst, 'reload schema'` or a restart) before the API shows it.

## CRUD Operations

### Read Records (GET)

```bash
# All records (the server may cap the page: db-max-rows)
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

# One object instead of an array (406 unless exactly one row matches)
curl "${POSTGRESQL_API_URL}/orders?id=eq.123" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Accept: application/vnd.pgrst.object+json"
```

### Create Records (POST)

```bash
# Single record
curl -X POST "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"title": "New Order", "status": "pending"}'

# Bulk insert — every object needs the same keys (see "Bulk insert with missing keys")
curl -X POST "${POSTGRESQL_API_URL}/orders" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{"title": "Order 1"}, {"title": "Order 2"}]'
```

### Update Records (PATCH)

```bash
# Update by filter — always send a filter
curl -X PATCH "${POSTGRESQL_API_URL}/orders?id=eq.123" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"status": "completed"}'
```

A `PATCH` or `DELETE` **without a filter changes every row** you may touch. Add the guard from **Safety Net for Bulk Writes** to every call that is built from variable input.

### Delete Records (DELETE)

```bash
curl -X DELETE "${POSTGRESQL_API_URL}/orders?id=eq.123" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}"
```

### Upsert (POST with conflict resolution)

`on_conflict` is a **query parameter**, not a header. It names the unique column (or comma-separated columns) that decides "same row"; without it the primary key is used. The `Prefer` header only chooses what happens on a conflict.

```bash
# Merge on a unique business key, return the stored row
curl -X POST "${POSTGRESQL_API_URL}/orders?on_conflict=external_ref" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates,return=representation" \
  -d '{"external_ref": "ext-1", "title": "Updated Order", "status": "active"}'

# Conflict on the primary key (on_conflict may be omitted)
curl -X POST "${POSTGRESQL_API_URL}/orders?on_conflict=id" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: resolution=merge-duplicates,return=representation" \
  -d '{"id": 123, "title": "Updated Order", "status": "active"}'
```

An `on_conflict: external_ref` **header** is ignored: on a conflict with another unique column the call fails with `409` and PostgreSQL code `23505` (`duplicate key value violates unique constraint`). With `merge-duplicates` every column in the body is overwritten, the primary key included, so send the key you want to keep. `resolution=ignore-duplicates` skips conflicting rows instead of updating them.

### Call Stored Functions (RPC)

```bash
curl -X POST "${POSTGRESQL_API_URL}/rpc/calculate_total" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 123}'
```

A `STABLE` or `IMMUTABLE` function can also be called with `GET /rpc/calculate_total?order_id=123`. The role needs `EXECUTE` on the function.

## Filtering Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `eq` | Equals | `?status=eq.active` |
| `neq` | Not equals | `?status=neq.deleted` |
| `gt` | Greater than | `?amount=gt.100` |
| `gte` | Greater or equal | `?amount=gte.100` |
| `lt` | Less than | `?amount=lt.50` |
| `lte` | Less or equal | `?amount=lte.50` |
| `like` | LIKE pattern (`*` is the wildcard) | `?name=like.*john*` |
| `ilike` | Case-insensitive LIKE | `?name=ilike.*john*` |
| `in` | In list | `?status=in.(active,pending)` |
| `is` | IS (null, true, false) | `?deleted_at=is.null` |
| `not` | Negate | `?status=not.eq.deleted` |
| `cs` | Contains (arrays/JSON) | `?tags=cs.{urgent}` |
| `cd` | Contained by | `?tags=cd.{urgent,important}` |
| `or` | Any of several conditions | `?or=(status.eq.active,status.eq.pending)` |

## Prefer Header Options

Combine options in one header, comma separated: `Prefer: return=representation,missing=default`. The server echoes what it applied in `Preference-Applied` — check it when an option seems to do nothing.

| Value | Effect |
|-------|--------|
| `return=representation` | Return the created/updated rows in the body |
| `return=minimal` | No body, `204` (the default for writes) |
| `return=headers-only` | `201` with a `Location` header, no body (inserts) |
| `resolution=merge-duplicates` | Upsert — update the existing row, insert new ones |
| `resolution=ignore-duplicates` | Skip conflicting rows on insert |
| `count=exact` | Exact row count in `Content-Range` (`0-0/4`); also `planned` and `estimated` (cheaper, approximate) |
| `missing=default` | A key missing from a bulk-insert object takes the column `DEFAULT` instead of `NULL` — use it with `?columns=` |
| `handling=strict` | Reject an unknown or unusable preference with `400` instead of ignoring it; required for `max-affected` |
| `max-affected=N` | Fail with `400` / `PGRST124` when a write would touch more than N rows — needs `handling=strict` |
| `tx=rollback` | Run the request and roll it back (a dry run) — needs `db-tx-end = commit-allow-override`; with the default `commit` the preference is silently ignored. (`db-tx-end` takes `commit`, `commit-allow-override`, `rollback`, `rollback-allow-override`; under `rollback-allow-override` every request rolls back unless the client sends `tx=commit`.) |

`return=none` is not a PostgREST value; it is ignored and the default `minimal` applies.

### Safety Net for Bulk Writes

For any `PATCH` or `DELETE` whose filter comes from variable input (a workflow, an agent), say how many rows you expect:

```bash
curl -X PATCH "${POSTGRESQL_API_URL}/orders?status=eq.pending" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: handling=strict,max-affected=50,return=representation" \
  -d '{"status": "queued"}'
```

The same guard on a `DELETE`:

```bash
curl -X DELETE "${POSTGRESQL_API_URL}/orders?status=eq.cancelled" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Prefer: handling=strict,max-affected=50"
```

If more than 50 rows match, nothing is changed and the answer is `400` / `PGRST124` with `"The query affects N rows"`. Without `handling=strict`, `max-affected` is ignored and a filterless `DELETE` removes everything.

### Bulk Insert With Missing Keys

PostgREST rejects an array whose objects have different keys (`PGRST102`, `All object keys must match`). Name the columns once and say what a missing key means:

```bash
curl -X POST "${POSTGRESQL_API_URL}/orders?columns=id,title,status" \
  -H "Authorization: Bearer ${POSTGRESQL_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Prefer: missing=default,return=representation" \
  -d '[{"id": 101, "title": "A", "status": "paid"}, {"id": 102, "title": "B"}]'
```

The second row gets the column default for `status`; without `missing=default` it would get `NULL`.

## PostgREST in n8n Workflows

Use an **HTTP Request** node. Keep the token in a credential, not in an expression:

```
Method:         GET / POST / PATCH / DELETE
URL:            <your PostgREST base URL>/orders        (fixed in the node)
Authentication: Generic Credential Type → Header Auth
                (Name: Authorization, Value: Bearer <POSTGRESQL_API_TOKEN>)
Headers:        Content-Type: application/json
                Prefer: return=representation
```

Do not build the URL or the token with `{{ $env.POSTGRESQL_API_URL }}`: n8n 2.x blocks `$env` in expressions and Code nodes by default (`N8N_BLOCK_ENV_ACCESS_IN_NODE`; the 2.0 breaking-changes list sets it to `true`, while the environment-variable reference page still shows `false` — verify on your instance). Use a credential plus a fixed URL. If you must read the environment, set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` on purpose and accept that every workflow author can then read the container's environment. In a Code node, do the data shaping and leave the call to the HTTP Request node.

## PostgREST in Trigger.dev Tasks

Read the URL and token from the task's environment and check the status — `fetch` does not throw on a `4xx`:

```typescript
const response = await fetch(
  `${process.env.POSTGRESQL_API_URL}/orders?status=eq.pending&limit=50`,
  {
    headers: {
      Authorization: `Bearer ${process.env.POSTGRESQL_API_TOKEN}`,
      "Content-Type": "application/json",
    },
  }
);
if (!response.ok) {
  throw new Error(`PostgREST ${response.status}: ${await response.text()}`);
}
const orders = await response.json();
```

A deployed task only sees environment variables you sync to the Trigger.dev environment — see `trigger-dev:config-and-build` (`syncEnvVars`).

## Upgrading to 16

- If you set `jwt-role-claim-key`, it is now a JSON Path and must start with `$`: `.roles.read` becomes `$.roles.read`. If you never set it, nothing changes
- Filtering or ordering on an embedded table by its **table name** when the embed has an alias (`?select=alias:table(*)&table.id=eq.1`) is deprecated — use the alias (`alias.id=eq.1`); the new behaviour needs `url-use-legacy-target-names` set to `false`
- PostgreSQL 13 and older are not supported

## Best Practices

- Always use `${POSTGRESQL_API_URL}` and `${POSTGRESQL_API_TOKEN}` — never hardcode a URL or token
- Send `Prefer: return=representation` on POST/PATCH when you need the stored row back
- Pass `on_conflict` in the query string for upserts on a business key
- Guard every variable-input `PATCH`/`DELETE` with `handling=strict,max-affected=N`
- Give the JWT role the narrowest grants the job needs; the API can do exactly what that role can do
- Use filtering operators for simple lookups; use `execute_sql` (see `postgres-mcp-tools`) for JOINs, CTEs and anything that needs several round trips
