---
name: api-reference
description: |
  NocoDB REST API reference for schema-development work — curl on Meta API v3. Loaded only on explicit cite. Use when:
  - "NocoDB REST API"
  - "API endpoints for tables/fields/views"
  - "create a table via API"
  - "what's in the OpenAPI spec"
  - "Meta API endpoints"
  - "field type schemas"
  - "Hook v3 payload"
  - "dashboard / widget API"
disable-model-invocation: true
---

# NocoDB REST API — Schema Reference

Authoritative API reference for `nocodb-dev`. On Cloud / licensed self-hosted the MCP server can write schema too (`listTools(category)` → `callTool`, see **mcp-patterns**); REST is the only schema-write path on Community Edition and the fallback everywhere else.

Two bundled OpenAPI specs (taken from NocoDB's `swagger-v3.json`):

| File | Surface | Path prefix | Purpose |
|------|---------|-------------|---------|
| `references/nocodb-openapi.json` | **Data API v3** (7 paths, 12 operations) | `/api/v3/data/...` | Records, links, attachments, count, button actions |
| `references/nocodb-meta-openapi.json` | **Meta API v3** + Docs API (49 paths, 100 operations) | `/api/v3/meta/...`, `/api/v3/docs/...` | Schema CRUD — tables, fields, field options, views, hooks, comments, scripts, dashboards, workflows, documents, environments, workspaces, members, teams, tokens |

For full payload shapes and per-endpoint details, see the bundled JSON files. Domain-grouped quick reference for the Meta API is in `references/meta-api-endpoints.md`. Per-type field config is in `references/field-types.md`.

## Authentication

Both APIs accept the same two header schemes:

| Scheme | Header | Notes |
|--------|--------|-------|
| `xc-token` | `xc-token: <api-token>` | Default — the API token from NocoDB → Team & Settings → API Tokens. Export it as `NOCODB_TOKEN`. |
| `bearerAuth` | `Authorization: Bearer <api-token>` | Equivalent — same token, different header. |
| `xc-shared-base-id` | `xc-shared-base-id: <uuid>` | For shared-base read flows only — not used by dev work. |

```bash
curl -sS \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}"
```

## Base URL

All requests go against `${NOCODB_URL}`. The default server in the spec is `https://app.nocodb.com`; for self-hosted instances substitute your own host.

## Plan Availability

Per the descriptions in the bundled spec:

| API | Available on |
|-----|--------------|
| Bases, tables, fields, filters, sorts, records, links, attachments | All plans |
| Hooks, comments, workflows, documents, base collaboration | Cloud-hosted Business and above; licensed self-hosted (Business and above) |
| Views, dashboards, widgets, scripts | Cloud-hosted Enterprise; licensed self-hosted (Business and above) |
| API tokens | All cloud-hosted plans; licensed self-hosted |
| Workspaces — list / create | All plans; read / update / delete of one workspace needs Business and above |
| Environments | Self-hosted Enterprise and cloud-hosted plans with organizations |

## API Surface Map

`nocodb-dev` focuses on the **Meta API** because schema modification is its purpose. The Data API is bundled so dev workflows can verify data after schema changes without leaving the plugin.

### Data API v3 — Quick Index

| Path | Methods | Operation |
|------|---------|-----------|
| `/api/v3/data/{baseId}/{tableId}/records` | `GET` | List Table Records |
| `/api/v3/data/{baseId}/{tableId}/records` | `POST` | Create Table Records |
| `/api/v3/data/{baseId}/{tableId}/records` | `PATCH` | Update Table Records |
| `/api/v3/data/{baseId}/{tableId}/records` | `DELETE` | Delete Table Records |
| `/api/v3/data/{baseId}/{tableId}/records/upsert` | `POST` | Upsert Table Records |
| `/api/v3/data/{baseId}/{tableId}/records/{recordId}` | `GET` | Read Table Record |
| `/api/v3/data/{baseId}/{tableId}/count` | `GET` | Count Table Records |
| `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` | `GET`/`POST`/`DELETE` | List/Link/Unlink |
| `/api/v3/data/{baseId}/{tableId}/actions/{columnId}` | `POST` | Trigger Button Action |
| `/api/v3/data/{baseId}/{modelId}/records/{recordId}/fields/{fieldId}/upload` | `POST` | Upload Attachment to Cell |

### Meta API v3 — Quick Index (by domain)

> See `references/meta-api-endpoints.md` for full request / response shapes.

**Workspaces** (5 ops): `GET`/`POST` `/workspaces`, `GET`/`PATCH`/`DELETE` `/workspaces/{workspaceId}`, plus `?include[]=members` and member endpoints.

**Bases** (3 + 4 ops): `GET`/`PATCH`/`DELETE` `/bases/{baseId}`; member invite/update/delete under `/bases/{base_id}/members`; list bases via `/workspaces/{workspaceId}/bases`.

**Tables** (5 ops): `GET`/`POST` `/bases/{base_id}/tables`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/tables/{tableId}`.

**Fields** (4 ops + 2 option ops): `POST` `/bases/{baseId}/tables/{tableId}/fields`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/fields/{fieldId}`; `POST`/`DELETE` `/bases/{baseId}/fields/{fieldId}/options` add or remove select choices without resending the whole list.

**Views** (5 ops, single endpoint with `type` discriminator — **nine** types: grid, gallery, kanban, calendar, map, form, gantt, timeline, list): `GET`/`POST` `/bases/{baseId}/tables/{tableId}/views`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/views/{viewId}`.

**Filters** (5 ops): per-view `GET`/`POST`/`PUT` `/views/{viewId}/filters`, `PATCH`/`DELETE` `/filters/{filterId}`. Groups use `group_operator` (`AND`/`OR`).

**Sorts** (4 ops): per-view `GET`/`POST` `/views/{viewId}/sorts`, `PATCH`/`DELETE` `/sorts/{sortId}`. Sorts use `field_id` + `direction`.

**Hooks** (5 ops, V3 shape): `GET`/`POST` `/tables/{tableId}/hooks`, `GET`/`PATCH`/`DELETE` `/hooks/{hookId}`. `event` is `record`|`manual`; `operation` is an array of `insert`/`update`/`delete`; uses `trigger_fields` (not a top-level `condition`).

**Comments** (5 ops): `GET`/`POST` `/records/{recordId}/comments`, `PATCH`/`DELETE` `/comments/{commentId}`, `POST` `/comments/{commentId}/resolve`.

**Scripts** (5 ops): `GET`/`POST` `/scripts`, `GET`/`PATCH`/`DELETE` `/scripts/{script_id}`. Referenced by Button fields and Script hook notifications.

**Dashboards + Widgets** (3 + 5 ops + 2 data endpoints): full `/dashboards` and per-dashboard `/widgets` CRUD plus `/data` GET on both.

**Workflows + Executions** (5 ops, read-and-execute over REST): `GET` `/workflows`, `GET` `/workflows/{workflow_id}`, `POST` `/execute`, list/get executions. Workflow **authoring** is not a REST operation — on Cloud/licensed it is available through MCP (`createWorkflow`, `updateWorkflow`, node tools, `publishWorkflow`).

**Documents** (6 ops, `/api/v3/docs/...`): `GET`/`POST` `/docs/{baseId}`, `GET`/`PATCH`/`DELETE` `/docs/{baseId}/{docId}`, `PATCH` `/docs/{baseId}/{docId}/reorder`.

**Teams** (7 ops): `/workspaces/{workspaceId}/teams` lifecycle plus per-team membership.

**Environments** (8 ops): `/workspaces/{workspaceId}/environments[/{environmentId}]` and `/orgs/{orgId}/environments[/{environmentId}]`.

**API Tokens** (3 ops): `GET`/`POST` `/tokens`, `DELETE` `/tokens/{tokenId}`. The token is returned **once** on create — store it immediately.

## Reading the OpenAPI Files

Probe the meta spec when looking up an endpoint or schema:

```bash
META=skills/api-reference/references/nocodb-meta-openapi.json
DATA=skills/api-reference/references/nocodb-openapi.json

# All meta + docs paths
jq -r '.paths | keys[]' "$META"

# A specific path's methods
jq '.paths."/api/v3/meta/bases/{baseId}/tables/{tableId}/views"' "$META"

# Hook payload shape
jq '.components.schemas.HookV3Create' "$META"

# All field-type option schemas
jq -r '.components.schemas | keys[] | select(startswith("FieldOptions_"))' "$META"

# A specific field type
jq '.components.schemas.FieldOptions_Formula' "$META"

# View option schemas (grid, kanban, calendar, gantt, timeline, list, …)
jq -r '.components.schemas | keys[] | select(startswith("ViewOptions"))' "$META"

# Widget option types
jq -r '.components.schemas | keys[] | select(startswith("WidgetOptions"))' "$META"
```

## Field Types Catalog

The Meta API knows **35 field types** (`FieldBase.type`), including the four system types that populate themselves and `AutoNumber`. Full per-type `options` payloads are in `references/field-types.md`. Quick list:

`SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email`, `Number`, `Decimal`, `Currency`, `Percent`, `Duration`, `Date`, `DateTime`, `Time`, `Year`, `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox`, `Attachment`, `JSON`, `Geometry`, `Links`, `LinkToAnotherRecord`, `Lookup`, `Rollup`, `Button`, `Formula`, `Barcode`, `QrCode`, `User`, `AutoNumber`, plus system: `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy`.

Type-specific configuration lives in an `options` object next to `title` and `type` (only `title`, `type`, `description`, `default_value` and `unique` sit at the top level).

## Common Request Patterns

The patterns below assume `BASE_ID`, `TABLE_ID`, … are exported and use `curl` directly. A one-line wrapper makes repeated calls shorter:

```bash
nocodb_api() {   # nocodb_api METHOD /meta/... ['{"json":"body"}']  — paths are under /api/v3
  local m="$1" p="$2" b="${3:-}"
  if [ -n "$b" ]; then
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" -d "$b" "${NOCODB_URL}/api/v3${p}"
  else
    curl -sS -X "$m" -H "xc-token: ${NOCODB_TOKEN}" -H "Content-Type: application/json" "${NOCODB_URL}/api/v3${p}"
  fi
}
```

### Get base info

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}"
```

### List tables

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables"
```

### Create a table

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customers",
    "fields": [
      { "title": "Name",  "type": "SingleLineText" },
      { "title": "Email", "type": "Email" }
    ]
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables"
```

### Create a field

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Phone", "type": "PhoneNumber" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/fields"
```

### Update a field (rename)

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Mobile" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}"
```

### Add select choices

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "choices": [ { "title": "Blocked", "color": "#fee2d5" } ] }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/fields/${FIELD_ID}/options"
```

### Create a Kanban view

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pipeline",
    "type":  "kanban",
    "options": { "stack_by": { "field_id": "<singleSelectFieldId>" } }
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/views"
```

### Create a hook

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Slack on new high-priority bug",
    "event": "record",
    "operation": ["insert"],
    "notification": {
      "type": "Slack",
      "payload": { "body": ":bug: {{record.Title}}" }
    },
    "active": true
  }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/hooks"
```

### List records (Data API)

```bash
curl -sS -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/data/${BASE_ID}/${TABLE_ID}/records?limit=10"
```

## Errors

Error bodies are `{ "error": "...", "message": "..." }`:

| HTTP | Meaning | Typical cause |
|------|---------|----------------|
| 400 | Bad Request | Malformed JSON, missing required field, invalid filter syntax |
| 401 | Unauthorized | Token missing or invalid |
| 403 | Forbidden | Token has no access to that base / table / field, or the plan does not include the API |
| 404 | Not Found | Wrong `baseId`, `tableId`, `fieldId`, or `recordId` |
| 422 | Unprocessable | Value doesn't match field type, system field write attempted, incompatible type change, or invalid view options for the chosen view type |

For schema-specific symptoms, see the **troubleshoot** skill.

## See Also

- `references/nocodb-meta-openapi.json` — full Meta API + Docs API spec (49 paths, 100 operations)
- `references/nocodb-openapi.json` — full Data API spec (7 paths, 12 operations)
- `references/meta-api-endpoints.md` — domain-grouped Meta API reference with payload shapes
- `references/field-types.md` — every field type with a minimal payload example
- **mcp-patterns** skill — the same operations through MCP on Cloud / licensed
- **cli-reference** skill — `curl` recipes by resource and the optional official `nocodb.sh`
- **table-management** / **field-management** / **view-management** / **webhooks** / **dashboards** / **workflows** — task-oriented skills built on this reference
