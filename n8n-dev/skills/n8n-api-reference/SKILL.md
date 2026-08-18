---
name: n8n-api-reference
description: n8n REST API reference with all endpoints, authentication, and curl examples. Use when making direct API calls, writing scripts that interact with n8n API, or when MCP tools are unavailable. Reference-only skill.
disable-model-invocation: true
---

# n8n REST API Reference

## Overview

n8n Public API v1.1.1. OpenAPI 3.0 specification. 37 endpoints across 11 tags.

The public API allows programmatic access to workflows, executions, credentials, tags, users, variables, projects, data tables, source control, and audit features.

Full OpenAPI spec available at: `references/n8n-api.json`

---

## Authentication

All API requests require an API key passed via the `X-N8N-API-KEY` header.

### Generating an API Key

1. Open your n8n instance
2. Go to **Settings** → **API**
3. Click **Create API Key**
4. Copy the generated key

### Base URL

```
${N8N_API_URL}/api/v1
```

### Header Format

```
X-N8N-API-KEY: <your-api-key>
```

### Quick Verification

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_API_URL/api/v1/workflows?limit=1"
```

If you get a 200 response with workflow data, authentication is working.

---

## Endpoint Reference by Tag

### Workflow (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/workflows` | List all workflows. Supports cursor pagination, filtering by tags, active status. |
| `POST` | `/workflows` | Create a new workflow. Body: `{name, nodes, connections, settings}`. |
| `GET` | `/workflows/{id}` | Get a single workflow by ID. Returns full workflow definition. |
| `PUT` | `/workflows/{id}` | Update a workflow. Replaces the entire workflow definition. |
| `DELETE` | `/workflows/{id}` | Delete a workflow permanently. |
| `POST` | `/workflows/{id}/activate` | Activate (publish) a workflow so it responds to triggers. |
| `POST` | `/workflows/{id}/deactivate` | Deactivate a workflow. Stops all trigger-based execution. |
| `GET` | `/workflows/{id}/tags` | Get tags associated with a workflow. |
| `PUT` | `/workflows/{id}/tags` | Update (replace) tags on a workflow. Body: `[{id: "tag-id"}]`. |
| `PUT` | `/workflows/{id}/transfer` | Transfer workflow ownership to another project. |

**Query parameters for `GET /workflows`:**
- `limit` — Number of results (default 10, max 250)
- `cursor` — Pagination cursor from previous response
- `tags` — Filter by tag name
- `name` — Filter by workflow name (partial match)
- `active` — Filter by active status (`true`/`false`)
- `projectId` — Filter by project

### Execution (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/executions` | List executions. Filter by status, workflowId, date range. |
| `GET` | `/executions/{id}` | Get execution details including input/output data. |
| `DELETE` | `/executions/{id}` | Delete an execution record. |
| `POST` | `/executions/{id}/retry` | Retry a failed execution from the point of failure or from start. |
| `POST` | `/executions/{id}/stop` | Stop a currently running execution. |
| `POST` | `/executions/stop` | Stop multiple running executions at once. |
| `GET` | `/executions/{id}/tags` | Get tags for an execution. |
| `PUT` | `/executions/{id}/tags` | Update tags on an execution. |

**Query parameters for `GET /executions`:**
- `workflowId` — Filter by workflow ID
- `status` — Filter: `error`, `success`, `waiting`, `running`, `new`
- `limit` — Number of results (default 10, max 250)
- `cursor` — Pagination cursor
- `startedBefore` / `startedAfter` — Date range filters (ISO 8601)

### Credential (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/credentials` | List all credentials. Returns name, type, dates (no secrets). |
| `POST` | `/credentials` | Create a credential. Body: `{name, type, data}`. |
| `GET` | `/credentials/schema/{credentialTypeName}` | Get the JSON schema for a credential type. |
| `PATCH` | `/credentials/{id}` | Update a credential (partial update). |
| `DELETE` | `/credentials/{id}` | Delete a credential. |
| `PUT` | `/credentials/{id}/transfer` | Transfer credential to another project. |

**Important:** `GET /credentials` never returns secret data. Use the schema endpoint to understand required fields before creating credentials.

### DataTable (7 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/data-tables` | List all data tables. |
| `POST` | `/data-tables` | Create a new data table. |
| `GET` | `/data-tables/{id}` | Get table details including columns. |
| `PATCH` | `/data-tables/{id}` | Update table metadata. |
| `DELETE` | `/data-tables/{id}` | Delete a data table. |
| `GET` | `/data-tables/{id}/rows` | Get rows from a table. Supports pagination. |
| `POST` | `/data-tables/{id}/rows` | Insert new rows. |
| `PATCH` | `/data-tables/{id}/rows/update` | Update existing rows by ID. |
| `POST` | `/data-tables/{id}/rows/upsert` | Upsert rows (insert or update if exists). |
| `DELETE` | `/data-tables/{id}/rows/delete` | Delete rows by ID. |

### User (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users with roles and status. |
| `POST` | `/users` | Create/invite new users. Body: array of `{email, role}`. |
| `GET` | `/users/{id}` | Get user by ID or email lookup. |
| `DELETE` | `/users/{id}` | Delete a user account. |
| `PATCH` | `/users/{id}/role` | Change a user's global role. |

**Roles:** `global:owner`, `global:admin`, `global:member`

### Tags (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/tags` | List all tags. |
| `POST` | `/tags` | Create a new tag. Body: `{name}`. |
| `GET` | `/tags/{id}` | Get a single tag. |
| `DELETE` | `/tags/{id}` | Delete a tag. |
| `PUT` | `/tags/{id}` | Update a tag name. |

### Audit (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/audit` | Generate a security audit of the n8n instance. Returns risk findings. |

**Body options:**
```json
{
  "categories": ["credentials", "nodes", "database", "filesystem", "instance"]
}
```

### SourceControl (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/source-control/pull` | Pull latest changes from the connected remote repository. |

### Variables (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/variables` | List all environment variables. |
| `POST` | `/variables` | Create a variable. Body: `{key, value}`. |
| `PUT` | `/variables/{id}` | Update a variable. |
| `DELETE` | `/variables/{id}` | Delete a variable. |

Variables are accessible in workflows via `$vars.variableName`.

### Projects (4+ endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects` | List all projects. |
| `POST` | `/projects` | Create a project. Body: `{name}`. |
| `PUT` | `/projects/{id}` | Update a project (name, members, roles). |
| `DELETE` | `/projects/{id}` | Delete a project. Requires transferring resources first. |

Projects support member management — add/remove users with specific roles per project.

### Discover (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/discover` | API capability discovery. Returns available endpoints and versions. |

---

## Common curl Patterns

### List Workflows

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/workflows"
```

### Get Workflow by ID

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/workflows/123"
```

### Create Workflow

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workflow","nodes":[],"connections":{},"settings":{}}' \
  "$N8N_API_URL/api/v1/workflows"
```

### Activate Workflow

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/workflows/123/activate"
```

### Deactivate Workflow

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/workflows/123/deactivate"
```

### List Executions (filtered)

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/executions?workflowId=123&status=error&limit=10"
```

### Retry Failed Execution

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/executions/456/retry"
```

### Create Credential

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"My API Key","type":"httpHeaderAuth","data":{"name":"Authorization","value":"Bearer xxx"}}' \
  "$N8N_API_URL/api/v1/credentials"
```

### Get Credential Schema

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/credentials/schema/httpHeaderAuth"
```

### Create Tag

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"production"}' \
  "$N8N_API_URL/api/v1/tags"
```

### Tag a Workflow

```bash
curl -X PUT \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"id":"tag-id-here"}]' \
  "$N8N_API_URL/api/v1/workflows/123/tags"
```

### List Variables

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/variables"
```

### Run Security Audit

```bash
curl -X POST \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"categories":["credentials","nodes","instance"]}' \
  "$N8N_API_URL/api/v1/audit"
```

### Get Data Table Rows

```bash
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/data-tables/dt-abc123/rows?limit=50"
```

---

## Pagination

The n8n API uses **cursor-based pagination**.

### How It Works

1. First request: `GET /workflows?limit=10`
2. Response includes `nextCursor` if more results exist
3. Next request: `GET /workflows?limit=10&cursor=<nextCursor-value>`
4. Repeat until `nextCursor` is absent

### Response Structure

```json
{
  "data": [...],
  "nextCursor": "eyJsaW1pdCI6MTAsIm9mZnNldCI6MTB9"
}
```

When `nextCursor` is `null` or absent, you have reached the last page.

### Pagination Example (bash loop)

```bash
CURSOR=""
while true; do
  RESPONSE=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "$N8N_API_URL/api/v1/workflows?limit=50${CURSOR:+&cursor=$CURSOR}")
  echo "$RESPONSE" | jq '.data[]'
  CURSOR=$(echo "$RESPONSE" | jq -r '.nextCursor // empty')
  [ -z "$CURSOR" ] && break
done
```

---

## Error Responses

| Status | Meaning | Common Cause |
|--------|---------|--------------|
| 400 | Bad Request | Invalid JSON body or missing required fields |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions for this operation |
| 404 | Not Found | Resource doesn't exist or wrong endpoint URL |
| 409 | Conflict | Resource already exists (e.g., duplicate tag name) |
| 500 | Internal Server Error | Server-side issue, check n8n logs |

### Error Response Format

```json
{
  "code": 404,
  "message": "Workflow with ID \"999\" could not be found."
}
```

---

## Rate Limits and Best Practices

- No official rate limits documented, but self-hosted instances may have resource constraints
- Use pagination (`limit` + `cursor`) for large datasets instead of fetching all at once
- Cache credential schemas — they rarely change
- Use `status` and `workflowId` filters on executions to reduce response size
- Prefer `PATCH` over `PUT` for credentials to avoid overwriting unchanged fields
- When bulk-operating, add small delays between requests to avoid overloading the instance
