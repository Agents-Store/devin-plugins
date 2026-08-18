---
name: api-reference
description: |
  NocoDB REST API reference for schema-development work. Loaded only on explicit cite. Use when:
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

Authoritative API reference for `nocodb-dev`. Two bundled OpenAPI specs:

| File | Surface | Path prefix | Purpose |
|------|---------|-------------|---------|
| `references/nocodb-openapi.json` | **Data API v3** | `/api/v3/data/...` | Records, links, attachments, count, button actions |
| `references/nocodb-meta-openapi.json` | **Meta API v3** | `/api/v3/meta/...` | Schema CRUD — tables, fields, views, hooks, comments, scripts, dashboards, workflows, workspaces, members, tokens |

For full payload shapes and per-endpoint details, see the bundled JSON files. Domain-grouped quick reference for the Meta API is in `references/meta-api-endpoints.md`. Per-type field config is in `references/field-types.md`.

## Authentication

Both APIs accept the same two header schemes:

| Scheme | Header | Notes |
|--------|--------|-------|
| `xc-token` | `xc-token: <api-token>` | Default — use the API token from NocoDB → Account Settings → API Tokens. Set `NOCODB_API_TOKEN`. |
| `bearerAuth` | `Authorization: Bearer <api-token>` | Equivalent — same token, different header. |
| `xc-shared-base-id` | `xc-shared-base-id: <uuid>` | For shared-base read flows only — not used by dev work. |

```bash
curl -sS \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID"
```

## Base URL

All requests go against `$NOCODB_URL`. The default server in the spec is `https://app.nocodb.com`; for self-hosted instances substitute your own host.

## API Surface Map

`nocodb-dev` focuses on the **Meta API** because schema modification is its purpose. The Data API is bundled for completeness so dev workflows can verify data after schema changes without leaving the plugin.

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

**Workspaces** (5 ops): `GET`/`POST` `/workspaces`, `GET`/`PATCH`/`DELETE` `/workspaces/{workspaceId}`, plus `?include[]=members` and team membership endpoints.

**Bases** (3 + 4 ops): `GET`/`PATCH`/`DELETE` `/bases/{baseId}`; member invite/update/delete under `/bases/{base_id}/members`; list bases via `/workspaces/{workspaceId}/bases`.

**Tables** (5 ops): `GET`/`POST` `/bases/{base_id}/tables`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/tables/{tableId}`.

**Fields** (4 ops): `POST` `/bases/{baseId}/tables/{tableId}/fields`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/fields/{fieldId}`.

**Views** (4 ops, single endpoint with `type` discriminator): `GET`/`POST` `/bases/{baseId}/tables/{tableId}/views`, `GET`/`PATCH`/`DELETE` `/bases/{baseId}/views/{viewId}`.

**Filters** (5 ops): per-view `GET`/`POST`/`PUT` `/views/{viewId}/filters`, `PATCH`/`DELETE` `/filters/{filterId}`.

**Sorts** (4 ops): per-view `GET`/`POST` `/views/{viewId}/sorts`, `PATCH`/`DELETE` `/sorts/{sortId}`.

**Hooks** (5 ops, V3 shape): `GET`/`POST` `/tables/{tableId}/hooks`, `GET`/`PATCH`/`DELETE` `/hooks/{hookId}`. `event` is `record`|`manual`; `operation` is array of `insert`/`update`/`delete`; uses `trigger_fields` (not a top-level `condition`).

**Comments** (5 ops): `GET`/`POST` `/records/{recordId}/comments`, `PATCH`/`DELETE` `/comments/{commentId}`, `POST` `/comments/{commentId}/resolve`.

**Scripts** (5 ops): `GET`/`POST` `/scripts`, `GET`/`PATCH`/`DELETE` `/scripts/{script_id}`. Referenced by Button fields and Script hook notifications.

**Dashboards + Widgets** (3 + 5 ops + 2 data endpoints): full `/dashboards` and per-dashboard `/widgets` CRUD plus `/data` GET on both.

**Workflows + Executions** (5 ops, read-and-execute only): `GET` `/workflows`, `GET` `/workflows/{workflow_id}`, `POST` `/execute`, list/get executions. Workflow authoring lives in the NocoDB UI.

**Teams** (7 ops): `/workspaces/{workspaceId}/teams` lifecycle plus per-team membership.

**API Tokens** (3 ops): `GET`/`POST` `/tokens`, `DELETE` `/tokens/{tokenId}`. Token returned **once** on create — store it immediately.

## Reading the OpenAPI Files

Probe the meta spec when looking up an endpoint or schema:

```bash
META=skills/api-reference/references/nocodb-meta-openapi.json
DATA=skills/api-reference/references/nocodb-openapi.json

# All meta paths
jq -r '.paths | keys[]' "$META"

# A specific path's methods
jq '.paths."/api/v3/meta/bases/{baseId}/tables/{tableId}/views"' "$META"

# Hook payload shape
jq '.components.schemas.HookV3Create' "$META"

# All field-type option schemas
jq -r '.components.schemas | keys[] | select(startswith("FieldOptions_"))' "$META"

# A specific field type
jq '.components.schemas.FieldOptions_Formula' "$META"

# Widget option types
jq -r '.components.schemas | keys[] | select(startswith("WidgetOptions"))' "$META"
```

## Field Types Catalog

The plugin supports **30 field types** plus **4 system types** that auto-populate. Full per-type config payloads are in `references/field-types.md`. Quick list:

`SingleLineText`, `LongText`, `PhoneNumber`, `URL`, `Email`, `Number`, `Decimal`, `Currency`, `Percent`, `Duration`, `Date`, `DateTime`, `Time`, `Year`, `SingleSelect`, `MultiSelect`, `Rating`, `Checkbox`, `Attachment`, `JSON`, `Geometry`, `Links`, `LinkToAnotherRecord`, `Lookup`, `Rollup`, `Button`, `Formula`, `Barcode`, `QrCode`, `User`, plus system: `CreatedTime`, `LastModifiedTime`, `CreatedBy`, `LastModifiedBy`.

## Common Request Patterns

### Get base info

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID"
```

### List tables

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables"
```

### Create a table

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customers",
    "fields": [
      { "title": "Name",  "type": "SingleLineText" },
      { "title": "Email", "type": "Email" }
    ]
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables"
```

### Create a field

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Phone", "type": "PhoneNumber" }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/fields"
```

### Update a field (rename)

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "title": "Mobile" }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/fields/$FIELD_ID"
```

### Create a Kanban view

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pipeline",
    "type":  "kanban",
    "options": { "fk_grp_col_id": "<singleSelectColumnId>" }
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/views"
```

### Create a hook

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Slack on new high-priority bug",
    "event": "record",
    "operation": ["insert"],
    "notification": {
      "type": "Messaging",
      "payload": {
        "channel": "Slack",
        "webhook_url": "https://hooks.slack.com/services/T0/B0/XXXX",
        "body": ":bug: {{record.Title}}"
      }
    },
    "active": true
  }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/hooks"
```

### List records (Data API)

```bash
curl -sS -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/data/$BASE_ID/$TABLE_ID/records?limit=10"
```

## Errors

The error response schemas are referenced as `0`, `1`, `2`, `3` in both spec files:

| HTTP | Meaning | Typical cause |
|------|---------|----------------|
| 400 | Bad Request | Malformed JSON, missing required field, invalid filter syntax |
| 401 | Unauthorized | Token missing or invalid |
| 403 | Forbidden | Token has no access to that base / table / field |
| 404 | Not Found | Wrong `baseId`, `tableId`, `fieldId`, or `recordId` |
| 422 | Unprocessable | Value doesn't match field type, system field write attempted, incompatible type change, or invalid view options for the chosen view type |

For schema-specific symptoms, see the **troubleshoot** skill.

## See Also

- `references/nocodb-meta-openapi.json` — full Meta API spec (15 303 lines, 41 paths)
- `references/nocodb-openapi.json` — full Data API spec (10 889 lines, 7 paths)
- `references/meta-api-endpoints.md` — domain-grouped Meta API reference with payload shapes
- `references/field-types.md` — every field type with a minimal payload example
- **cli-reference** skill — equivalent operations via the `nc` command
- **table-management** / **field-management** / **view-management** / **webhooks** / **dashboards** / **workflows** — task-oriented skills built on this reference
