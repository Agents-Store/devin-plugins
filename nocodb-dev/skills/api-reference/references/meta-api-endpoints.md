# NocoDB Meta API — Endpoint Reference (v3)

Authoritative reference for the **Meta API** at `/api/v3/meta/...`. All paths are documented in `nocodb-meta-openapi.json` (bundled in this directory). The Data API (records / links / attachments) lives under `/api/v3/data/...` and is documented in `nocodb-openapi.json`.

All requests use:

```
Header:  xc-token: $NOCODB_API_TOKEN          (or: Authorization: Bearer $NOCODB_API_TOKEN)
Header:  Content-Type: application/json
Base:    $NOCODB_URL
```

> Probe the spec for full per-operation details:
> ```bash
> SPEC=skills/api-reference/references/nocodb-meta-openapi.json
> jq '.paths."/api/v3/meta/bases/{baseId}/tables/{tableId}/views"' "$SPEC"
> jq '.components.schemas.HookV3Create' "$SPEC"
> ```

## Path Structure

Almost every Meta endpoint nests under `/api/v3/meta/bases/{baseId}/...`. The exceptions are workspace-level (`/api/v3/meta/workspaces/...`) and global token-level (`/api/v3/meta/tokens`).

Path parameters use snake_case (`{base_id}`, `{table_id}`) on the dashboards/scripts/workflows endpoints and camelCase (`{baseId}`, `{tableId}`) elsewhere — both refer to the same NocoDB ID.

---

## Workspaces

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/workspaces` | `GET` | List workspaces |
| `/api/v3/meta/workspaces` | `POST` | Create workspace |
| `/api/v3/meta/workspaces/{workspaceId}` | `GET` | Get workspace |
| `/api/v3/meta/workspaces/{workspaceId}` | `PATCH` | Update workspace |
| `/api/v3/meta/workspaces/{workspaceId}` | `DELETE` | Delete workspace |
| `/api/v3/meta/workspaces/{workspaceId}?include[]=members` | `GET` | List workspace members |
| `/api/v3/meta/workspaces/{workspaceId}/members` | `POST` | Add workspace members |
| `/api/v3/meta/workspaces/{workspaceId}/members` | `PATCH` | Update workspace member roles |
| `/api/v3/meta/workspaces/{workspaceId}/members` | `DELETE` | Delete workspace members |
| `/api/v3/meta/workspaces/{workspaceId}/bases` | `GET` | List bases in workspace |
| `/api/v3/meta/workspaces/{workspaceId}/bases` | `POST` | Create base |

Workspace create payload:

```json
{ "title": "New Workspace", "description": "Optional" }
```

## Bases

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}` | `GET` | Get base meta (tables + sources summary) |
| `/api/v3/meta/bases/{baseId}` | `PATCH` | Update base (rename, description, meta) |
| `/api/v3/meta/bases/{baseId}` | `DELETE` | Delete base |
| `/api/v3/meta/bases/{baseId}?include[]=members` | `GET` | List base members |
| `/api/v3/meta/bases/{base_id}/members` | `POST` | Invite base members |
| `/api/v3/meta/bases/{base_id}/members` | `PATCH` | Update base members |
| `/api/v3/meta/bases/{base_id}/members` | `DELETE` | Delete base members |

Base update payload (`BaseUpdate`):

```json
{ "title": "Renamed", "description": "New description" }
```

Base member invite (`BaseMemberCreate`):

```json
{ "email": "user@example.com", "roles": "base-editor" }
```

Roles: `base-creator`, `base-editor`, `base-commenter`, `base-viewer`.

## Tables

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/tables` | `GET` | List tables |
| `/api/v3/meta/bases/{base_id}/tables` | `POST` | Create table |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}` | `GET` | Get table schema (columns + views) |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}` | `PATCH` | Update table |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}` | `DELETE` | Delete table |

Create-table payload (`TableCreate`):

```json
{
  "title": "Customers",
  "description": "Master customer list",
  "source_id": "<optional, only for non-default sources>",
  "fields": [
    { "title": "Name",  "type": "SingleLineText" },
    { "title": "Email", "type": "Email" }
  ]
}
```

Update-table payload (`TableUpdate`):

```json
{ "title": "Renamed Customers" }
{ "description": "New description" }
{ "display_field_id": "c_abc123" }
```

## Fields

Fields are addressed under the table for create, then by their own ID for read/update/delete:

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | `POST` | Create field |
| `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | `GET` | Get field |
| `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | `PATCH` | Update field |
| `/api/v3/meta/bases/{baseId}/fields/{fieldId}` | `DELETE` | Delete field |

> List fields by reading the parent table's `GET /tables/{tableId}` — the response includes the `fields` array.

Create-field payload (`CreateField` — discriminated by `type`, see `field-types.md` for all 30 variants):

```json
{ "title": "Phone", "type": "PhoneNumber" }
{ "title": "Price", "type": "Currency", "options": { "currency_code": "USD", "currency_locale": "en-US" } }
{ "title": "Status", "type": "SingleSelect", "options": { "choices": [
  {"title":"New"}, {"title":"Active"}, {"title":"Archived"}
]}}
```

Update-field payload (`FieldUpdate`):

```json
{ "title": "Mobile" }
{ "type": "LongText" }
```

NocoDB validates type changes against existing data — incompatible changes return 422.

## Views

> **One endpoint, six view types.** The `POST /views` endpoint accepts a `type` discriminator (`grid`, `gallery`, `kanban`, `calendar`, `map`, `form`) — there are no per-type endpoints.

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | `GET` | List views on a table |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | `POST` | Create view (any type) |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `GET` | Get view schema |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `PATCH` | Update view (rename, options, fields) |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `DELETE` | Delete view |

Create-view payloads (`ViewCreate` — `oneOf` per view type, discriminator on `type`):

```json
// Grid
{ "title": "All", "type": "grid" }

// Form
{ "title": "Intake", "type": "form",
  "options": { "subheading": "Tell us about your company" } }

// Gallery — needs an Attachment cover
{ "title": "Catalog", "type": "gallery",
  "options": { "fk_cover_image_col_id": "c_image_id" } }

// Kanban — REQUIRES options.fk_grp_col_id (a SingleSelect)
{ "title": "Pipeline", "type": "kanban",
  "options": { "fk_grp_col_id": "c_status_id" } }

// Calendar — REQUIRES options with at least one Date / DateTime range
{ "title": "Schedule", "type": "calendar",
  "options": {
    "calendar_range": [
      { "fk_from_column_id": "c_start_id", "fk_to_column_id": "c_end_id" }
    ]
  }}

// Map — needs Geometry field
{ "title": "Locations", "type": "map",
  "options": { "fk_geo_data_col_id": "c_geo_id" } }
```

Optional on create (and on `PATCH`): `sorts: []`, `filters: {...}`, `fields: [...]`, `row_coloring: {...}`.

## Filters (per view)

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | `GET` | List filters on a view |
| `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | `POST` | Create a filter |
| `/api/v3/meta/bases/{baseId}/views/{viewId}/filters` | `PUT` | **Replace** all filters atomically |
| `/api/v3/meta/bases/{baseId}/filters/{filterId}` | `PATCH` | Update one filter |
| `/api/v3/meta/bases/{baseId}/filters/{filterId}` | `DELETE` | Delete one filter |

Filter create payload (`FilterCreate`):

```json
{ "field_id": "c_status_id", "operator": "eq", "value": "Active" }
```

Filter group (`FilterGroup`, up to 3 levels deep):

```json
{
  "logical_op": "and",
  "filters": [
    { "field_id": "c_status_id",   "operator": "eq", "value": "Active" },
    { "field_id": "c_priority_id", "operator": "eq", "value": "High" }
  ]
}
```

`PUT` replaces the entire view's filter set; `POST` appends.

## Sorts (per view)

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | `GET` | List sorts on a view |
| `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | `POST` | Add a sort |
| `/api/v3/meta/bases/{baseId}/sorts/{sortId}` | `PATCH` | Update a sort |
| `/api/v3/meta/bases/{baseId}/sorts/{sortId}` | `DELETE` | Delete a sort |

Sort payload (`SortCreate`):

```json
{ "field_id": "c_created_at_id", "order": "desc" }
```

`order`: `asc` | `desc`.

## Hooks (Webhooks v3)

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/hooks` | `GET` | List hooks on a table |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/hooks` | `POST` | Create a hook |
| `/api/v3/meta/bases/{baseId}/hooks/{hookId}` | `GET` | Get a hook |
| `/api/v3/meta/bases/{baseId}/hooks/{hookId}` | `PATCH` | Update a hook |
| `/api/v3/meta/bases/{baseId}/hooks/{hookId}` | `DELETE` | Delete a hook |

Create-hook payload (`HookV3Create`):

```json
{
  "title":         "<display name>",
  "description":   "Optional",
  "event":         "record",
  "operation":     ["insert", "update"],
  "notification":  { "type": "URL", "payload": { ... } },
  "trigger_fields": ["<columnId>", "<columnId>"],
  "active":        true
}
```

Required: `title`, `operation`, `notification`.

| Key | Values | Notes |
|-----|--------|-------|
| `event` | `record` (default) \| `manual` | `record` fires on the chosen `operation`(s); `manual` fires only when explicitly invoked from a Button or Script |
| `operation` | array of `insert`, `update`, `delete` | One hook can listen to multiple operations |
| `trigger_fields` | array of column IDs | Optional — for `update`, only fire when one of these fields changed |
| `notification` | `HookNotificationV3` (oneOf) | URL / Email / Messaging / Script |

> The v3 hook shape **changed** from earlier NocoDB versions. In v3 there is no `before`/`after` distinction (all hooks are async-after); no top-level `condition` field — use `trigger_fields` for change-based gating, or use a Script notification for richer logic.

Notification subschemas (`HookNotificationV3*`):

```json
// URL
{ "type": "URL", "payload": {
  "method": "POST",
  "path":   "https://hooks.example.com/nocodb",
  "body":   "{\"id\": \"{{record.Id}}\"}",
  "headers": [{"name":"Authorization","value":"Bearer ${KEY}"}]
}}

// Email — requires SMTP plugin configured
{ "type": "Email", "payload": {
  "to":      "ops@example.com",
  "subject": "{{record.Title}}",
  "body":    "<p>{{record.Description}}</p>"
}}

// Messaging — Slack / Microsoft Teams / Discord / Mattermost
{ "type": "Messaging", "payload": {
  "channel":     "Slack",
  "webhook_url": "https://hooks.slack.com/services/...",
  "body":        ":rocket: {{record.Title}}"
}}

// Script (Enterprise only) — requires an existing Script on the same base
{ "type": "Script", "payload": { "script_id": "<scriptId>" } }
```

## Comments

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/records/{recordId}/comments` | `GET` | List comments on a record |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/records/{recordId}/comments` | `POST` | Create a comment |
| `/api/v3/meta/bases/{baseId}/comments/{commentId}` | `PATCH` | Update a comment |
| `/api/v3/meta/bases/{baseId}/comments/{commentId}` | `DELETE` | Delete a comment |
| `/api/v3/meta/bases/{baseId}/comments/{commentId}/resolve` | `POST` | Mark a comment resolved |

Create payload (`CommentCreateRequest`):

```json
{ "comment": "Looks good — please verify the @customer field." }
```

`comment` is markdown, max 3000 chars.

## Scripts

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/scripts` | `GET` | List scripts |
| `/api/v3/meta/bases/{base_id}/scripts` | `POST` | Create script |
| `/api/v3/meta/bases/{base_id}/scripts/{script_id}` | `GET` | Get script (incl. body) |
| `/api/v3/meta/bases/{base_id}/scripts/{script_id}` | `PATCH` | Update script |
| `/api/v3/meta/bases/{base_id}/scripts/{script_id}` | `DELETE` | Delete script |

Create payload (`ScriptCreateReq`):

```json
{
  "title": "Daily summary",
  "description": "Compute and email today's totals",
  "script": "// JavaScript body, runs in NocoDB sandbox",
  "config": {},
  "meta": {}
}
```

Scripts are referenced by:

- The `Button` field type (`action.type: "script"`).
- The `Script` hook notification (`{"type":"Script","payload":{"script_id":"..."}}`).

## Dashboards

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/dashboards` | `GET` | List dashboards |
| `/api/v3/meta/bases/{base_id}/dashboards` | `POST` | Create dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `GET` | Get dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `PATCH` | Update dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}` | `DELETE` | Delete dashboard |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/data` | `GET` | Fetch all widget data for the dashboard |

Create payload (`DashboardCreateReq`):

```json
{ "title": "Sales overview", "description": "Live KPIs" }
```

## Widgets (per dashboard)

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets` | `GET` | List widgets |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets` | `POST` | Create widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `GET` | Get widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `PATCH` | Update widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}` | `DELETE` | Delete widget |
| `/api/v3/meta/bases/{base_id}/dashboards/{dashboard_id}/widgets/{widget_id}/data` | `GET` | Fetch widget data |

Widget options schemas (`WidgetOptions*`):

| Schema | Widget kind |
|--------|-------------|
| `WidgetOptionsBarChart` | Bar chart |
| `WidgetOptionsLineChart` | Line chart |
| `WidgetOptionsPieChart` | Pie chart |
| `WidgetOptionsDonutChart` | Donut chart |
| `WidgetOptionsMetric` | Single metric (KPI tile) |
| `WidgetOptionsText` | Markdown text block |
| `WidgetOptionsIframe` | Embedded URL |

Create payload (`WidgetCreateReq`):

```json
{
  "title": "Active customers",
  "type":  "metric",
  "options": { "table_id": "<tableId>", "aggregation": "count", "filter": "(Status,eq,Active)" }
}
```

## Workflows

NocoDB Workflows is the platform's built-in automation engine (separate from external systems like n8n).

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{base_id}/workflows` | `GET` | List workflows |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}` | `GET` | Get workflow definition |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/execute` | `POST` | Execute workflow on demand |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/executions` | `GET` | List executions |
| `/api/v3/meta/bases/{base_id}/workflows/{workflow_id}/executions/{execution_id}` | `GET` | Get one execution (with node-by-node results) |

Execute payload (`WorkflowExecuteReq`):

```json
{
  "input": { "<workflow input variables>": "..." },
  "trigger": "manual"
}
```

> Workflow **creation/editing** APIs are not in this spec — author workflows in the NocoDB UI; this API surface is for listing, executing, and inspecting executions. The `WorkflowDraft*`, `WorkflowNode*`, `WorkflowEdge` schemas describe the node graph for read responses.

## API Tokens

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/tokens` | `GET` | List API tokens for the calling user |
| `/api/v3/meta/tokens` | `POST` | Create an API token |
| `/api/v3/meta/tokens/{tokenId}` | `DELETE` | Revoke an API token |

Create payload:

```json
{ "description": "CI deploy token" }
```

Response (`ApiTokenWithTokenV3`) includes the raw token **once** — store it immediately; subsequent reads return only metadata.

## Workspace Teams

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/workspaces/{workspaceId}/teams` | `GET` | List teams |
| `/api/v3/meta/workspaces/{workspaceId}/teams` | `POST` | Create team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}` | `GET` | Get team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}` | `PATCH` | Update team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}` | `DELETE` | Delete team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}/members` | `POST` | Add members to team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}/members` | `PATCH` | Update member role in team |
| `/api/v3/meta/workspaces/{workspaceId}/teams/{teamId}/members` | `DELETE` | Remove member from team |

## Authentication & Errors

Same as the Data API — `xc-token` or `Authorization: Bearer ...`. The four error response shapes (`0`, `1`, `2`, `3`) cover 400 / 401 / 403 / 404. 422 is returned for schema-validation failures (e.g. incompatible field type change, malformed view options).

## Notes

- All Meta endpoints accept either header scheme.
- `PATCH` requests should include only the keys you're changing.
- `DELETE` is destructive and unrecoverable — confirm before scripting.
- Path-parameter casing is inconsistent in the spec: `{baseId}` vs `{base_id}`. Both refer to the same NocoDB ID format (prefix `p`); the casing is purely a quirk of this OpenAPI document.
- v3 represents a clean break from older NocoDB Meta API versions (`/api/v1/db/meta/...`, `/api/v2/meta/...`) — older paths may still respond on legacy instances but are not documented here.
