# NocoDB Meta API — Endpoint Reference (v3)

Authoritative reference for the **Meta API** at `/api/v3/meta/...` and the Documents API at `/api/v3/docs/...`. All paths are documented in `nocodb-meta-openapi.json` (bundled in this directory). The Data API (records / links / attachments) lives under `/api/v3/data/...` and is documented in `nocodb-openapi.json`.

On Cloud / licensed self-hosted the MCP server exposes most of these write operations as tools (`listTools(category)` → `callTool`, see the **mcp-patterns** skill); the REST endpoints below are the path on Community Edition and the fallback elsewhere.

All requests use:

```
Header:  xc-token: ${NOCODB_TOKEN}            (or: Authorization: Bearer ${NOCODB_TOKEN})
Header:  Content-Type: application/json
Base:    ${NOCODB_URL}
```

> Probe the spec for full per-operation details:
> ```bash
> SPEC=skills/api-reference/references/nocodb-meta-openapi.json
> jq '.paths."/api/v3/meta/bases/{baseId}/tables/{tableId}/views"' "$SPEC"
> jq '.components.schemas.HookV3Create' "$SPEC"
> ```

## Path Structure

Almost every Meta endpoint nests under `/api/v3/meta/bases/{baseId}/...`. The exceptions are workspace-level (`/api/v3/meta/workspaces/...`), organization-level (`/api/v3/meta/orgs/...`), global token-level (`/api/v3/meta/tokens`) and the Documents API (`/api/v3/docs/{baseId}/...`).

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

Workspace member bodies are **arrays** — one object per user (`WorkspaceUserCreate` / `WorkspaceUserUpdate` / `WorkspaceUserDelete`). A new member is identified by `user_id` **or** `email` (not both); updates and deletes key on `user_id`:

```json
// POST   /workspaces/{workspaceId}/members
[ { "email": "user@example.com", "workspace_role": "workspace-level-editor" } ]

// PATCH  /workspaces/{workspaceId}/members
[ { "user_id": "<userId>", "workspace_role": "workspace-level-viewer" } ]

// DELETE /workspaces/{workspaceId}/members
[ { "user_id": "<userId>" } ]
```

`workspace_role`: `workspace-level-owner`, `workspace-level-creator`, `workspace-level-editor`, `workspace-level-viewer`, `workspace-level-commenter`, `workspace-level-no-access`.

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

Base member bodies are **arrays** too (`BaseMemberCreate` / `BaseMemberUpdate` / `BaseMemberDelete`). An invite carries `user_id` **or** `email` (not both), a `base_role`, and optionally `user_name`; updates and deletes key on `user_id`:

```json
// POST   /bases/{base_id}/members
[ { "email": "user@example.com", "base_role": "editor" } ]

// PATCH  /bases/{base_id}/members
[ { "user_id": "<userId>", "base_role": "viewer" } ]

// DELETE /bases/{base_id}/members
[ { "user_id": "<userId>" } ]
```

`base_role`: `owner`, `creator`, `editor`, `viewer`, `commenter`, `no-access`.

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
| `/api/v3/meta/bases/{baseId}/fields/{fieldId}/options` | `POST` | Add choices to a SingleSelect / MultiSelect field |
| `/api/v3/meta/bases/{baseId}/fields/{fieldId}/options` | `DELETE` | Remove choices (by title) from a select field |

> List fields by reading the parent table's `GET /tables/{tableId}` — the response includes the `fields` array.

Create-field payload (`CreateField` — discriminated by `type`, see `field-types.md` for all 35 types). Type-specific settings go inside `options`; only `title`, `type`, `description`, `default_value` and `unique` sit at the top level:

```json
{ "title": "Phone", "type": "PhoneNumber" }
{ "title": "Price", "type": "Currency", "options": { "currency_code": "USD", "currency_locale": "en-US" } }
{ "title": "Status", "type": "SingleSelect", "options": { "choices": [
  {"title":"New"}, {"title":"Active"}, {"title":"Archived"}
]}}
{ "title": "Customer", "type": "LinkToAnotherRecord",
  "options": { "relation_type": "bt", "related_table_id": "m_customers_id" } }
```

Update-field payload (`FieldUpdate`):

```json
{ "title": "Mobile" }
{ "type": "LongText" }
```

NocoDB validates type changes against existing data — incompatible changes return 422.

Select choices (`FieldOptionsAddReq` / `FieldOptionsDeleteReq`) — the add call is idempotent (existing titles are skipped), the delete call ignores unknown titles, removing a choice clears it from existing records, and at least one choice must remain:

```json
// POST   .../fields/{fieldId}/options
{ "choices": [ { "title": "Blocked", "color": "#fee2d5" } ] }

// DELETE .../fields/{fieldId}/options
{ "choices": [ { "title": "Archived" } ] }
```

## Views

> **One endpoint, nine view types.** The `POST /views` endpoint accepts a `type` discriminator (`grid`, `gallery`, `kanban`, `calendar`, `map`, `form`, `gantt`, `timeline`, `list`) — there are no per-type endpoints. `lock_type` is `collaborative` (default), `locked` or `personal`.

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | `GET` | List views on a table |
| `/api/v3/meta/bases/{baseId}/tables/{tableId}/views` | `POST` | Create view (any type) |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `GET` | Get view schema |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `PATCH` | Update view (rename, options, fields) |
| `/api/v3/meta/bases/{baseId}/views/{viewId}` | `DELETE` | Delete view |

Create-view payloads (`ViewCreate` — `oneOf` per view type, discriminator on `type`; per-type settings go inside `options`):

```json
// Grid
{ "title": "All", "type": "grid",
  "options": { "row_height": "medium", "groups": [ { "field_id": "c_status_id", "direction": "asc" } ] } }

// Form
{ "title": "Intake", "type": "form",
  "options": { "form_title": "Contact us", "form_description": "Tell us about your company",
               "thank_you_message": "Thanks!", "reset_form_after_submit": true } }

// Gallery — needs an Attachment cover
{ "title": "Catalog", "type": "gallery",
  "options": { "cover_field_id": "c_image_id" } }

// Kanban — REQUIRES options.stack_by (a SingleSelect)
{ "title": "Pipeline", "type": "kanban",
  "options": { "stack_by": { "field_id": "c_status_id" }, "cover_field_id": "c_image_id" } }

// Calendar — REQUIRES options.date_ranges with at least one Date / DateTime range
{ "title": "Schedule", "type": "calendar",
  "options": {
    "date_ranges": [
      { "start_date_field_id": "c_start_id", "end_date_field_id": "c_end_id" }
    ]
  }}

// Timeline — REQUIRES options.date_ranges (several ranges allowed)
{ "title": "Roadmap", "type": "timeline",
  "options": { "date_ranges": [ { "start_date_field_id": "c_start_id", "end_date_field_id": "c_end_id" } ] } }

// Gantt — REQUIRES options.date_dependency (null = table default); date_ranges is rejected
{ "title": "Plan", "type": "gantt",
  "options": { "date_dependency": null } }

// List — hierarchy of linked tables
{ "title": "Outline", "type": "list",
  "options": { "levels": [ { "level": 1, "table_id": "m_parent_id" } ], "show_empty_parents": false } }

// Map — needs a GeoData field
{ "title": "Locations", "type": "map",
  "options": { "geo_data_field_id": "c_geo_id" } }
```

Optional on create (and on `PATCH`): `sorts: []`, `filters: {...}`, `fields: [...]` (the complete ordered field list with `show`, `width`, `aggregation` — every field you omit is hidden), `row_coloring: {...}`.

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

Filter group (`FilterGroup` — `group_operator` is `AND` or `OR`; groups nest up to 3 levels deep):

```json
{
  "group_operator": "AND",
  "filters": [
    { "field_id": "c_status_id",   "operator": "eq", "value": "Active" },
    { "field_id": "c_priority_id", "operator": "eq", "value": "High" }
  ]
}
```

`PUT` replaces the entire view's filter set; `POST` appends. For Date / DateTime fields add a `sub_operator` (for example `"exactDate"` with `value: "2026-06-01"`, or `"today"` with no value).

## Sorts (per view)

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | `GET` | List sorts on a view |
| `/api/v3/meta/bases/{baseId}/views/{viewId}/sorts` | `POST` | Add a sort |
| `/api/v3/meta/bases/{baseId}/sorts/{sortId}` | `PATCH` | Update a sort |
| `/api/v3/meta/bases/{baseId}/sorts/{sortId}` | `DELETE` | Delete a sort |

Sort payload (`SortCreate`):

```json
{ "field_id": "c_created_at_id", "direction": "desc" }
```

`direction`: `asc` | `desc` (default `asc`).

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

Required: `title`, `operation`, `notification`. Hook APIs need a cloud Business plan or a licensed self-hosted deployment.

| Key | Values | Notes |
|-----|--------|-------|
| `event` | `record` (default) \| `manual` | `record` fires on the chosen `operation`(s); `manual` fires only when explicitly invoked from a Button or Script |
| `operation` | array of `insert`, `update`, `delete` | One hook can listen to multiple operations |
| `trigger_fields` | array of column IDs | Optional — for `update`, only fire when one of these fields changed |
| `notification` | `HookNotificationV3` (oneOf) | URL / Email / Slack-style messaging / Script |

> The v3 hook shape **changed** from earlier NocoDB versions. In v3 there is no `before`/`after` distinction (all hooks are async-after); no top-level `condition` field — use `trigger_fields` for change-based gating, or use a Script notification for richer logic.

Notification subschemas (`HookNotificationV3*`, discriminated by `type`):

```json
// URL
{ "type": "URL", "payload": {
  "method": "POST",
  "path":   "https://hooks.example.com/nocodb",
  "body":   "{\"id\": \"{{record.Id}}\"}",
  "headers": [{"name":"Authorization","value":"Bearer ${KEY}","enabled":true}]
}}

// Email — requires SMTP plugin configured; to, subject and body are all required
{ "type": "Email", "payload": {
  "to":      "ops@example.com",
  "subject": "{{record.Title}}",
  "body":    "<p>{{record.Description}}</p>"
}}

// Messaging — type is the service: Slack | Discord | Telegram | Whatsapp | Twilio
{ "type": "Slack", "payload": { "body": ":rocket: {{record.Title}}" } }

// Script — requires an existing Script on the same base
{ "type": "Script", "payload": { "scriptId": "<scriptId>" } }
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

`comment` is markdown, max 10000 chars.

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

- The `Button` field type (`options: { "type": "script", "script_id": "<scriptId>" }`).
- The `Script` hook notification (`{"type":"Script","payload":{"scriptId":"..."}}`).

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
| `WidgetOptionsBarChart` | Bar chart (`chart_type: "bar"`) |
| `WidgetOptionsLineChart` | Line chart (`chart_type: "line"`) |
| `WidgetOptionsPieChart` | Pie chart (`chart_type: "pie"`) |
| `WidgetOptionsDonutChart` | Donut chart (`chart_type: "donut"`) |
| `WidgetOptionsScatter` | Scatter chart (`chart_type: "scatter"`) |
| `WidgetOptionsMetric` | Single metric (KPI tile) |
| `WidgetOptionsText` | Markdown text block |
| `WidgetOptionsIframe` | Embedded URL |

Create payload (`WidgetCreateReq`):

`type` is `chart`, `metric`, `text` or `iframe`; chart kinds are selected by `options.chart_type`. `table_id` / `view_id` and `position` (`x`, `y`, `w`, `h` on a 12-column grid) are top-level keys:

```json
{
  "title": "Customers",
  "type":  "metric",
  "table_id": "<tableId>",
  "options": { "data_source": "table", "metric": { "type": "count", "aggregation": "count" } }
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
  "trigger_data": { "<data for the workflow trigger>": "..." }
}
```

The response is `{ "id": "<execution id>" }`. Executions list as `{ "list": [...] }` (`limit`, `offset`), and `status` is `running`, `waiting`, `completed`, `error`, `cancelled` or `skipped`.

> Workflow **creation/editing** is not a REST operation in this spec — this API surface is for listing, executing, and inspecting executions. On Cloud / licensed self-hosted, drafts are authored through MCP (`createWorkflow`, `updateWorkflow`, node and edge tools, `validateWorkflowNode`, `publishWorkflow`; enabling and `run_as` stay in the UI). The `WorkflowDraft*`, `WorkflowNode*`, `WorkflowEdge` schemas describe the node graph for read responses.

## Documents

Document pages inside a base (Business plan and above, or licensed self-hosted).

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/docs/{baseId}` | `GET` | List documents (`parent_id` query parameter walks the hierarchy; content is omitted) |
| `/api/v3/docs/{baseId}` | `POST` | Create a document (`title`, `content`, `parent_id`) |
| `/api/v3/docs/{baseId}/{docId}` | `GET` | Get a document with its content |
| `/api/v3/docs/{baseId}/{docId}` | `PATCH` | Update title / content |
| `/api/v3/docs/{baseId}/{docId}` | `DELETE` | Delete a document |
| `/api/v3/docs/{baseId}/{docId}/reorder` | `PATCH` | Move / reorder within the hierarchy |

Probe `DocumentCreate` / `DocumentUpdate` in the spec for the exact body shape.

## Environments

| Path | Method | Purpose |
|------|--------|---------|
| `/api/v3/meta/workspaces/{workspaceId}/environments` | `GET` / `POST` | List / create environments |
| `/api/v3/meta/workspaces/{workspaceId}/environments/{environmentId}` | `PATCH` / `DELETE` | Update / delete |
| `/api/v3/meta/orgs/{orgId}/environments` | `GET` / `POST` | Org-level list / create (Org Owner to write) |
| `/api/v3/meta/orgs/{orgId}/environments/{environmentId}` | `PATCH` / `DELETE` | Org-level update / delete |

Bodies: `EnvironmentCreateV3Req` / `EnvironmentUpdateV3Req`. Available on self-hosted Enterprise and on cloud-hosted plans with organizations.

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

Same as the Data API — `xc-token` or `Authorization: Bearer ...`. Error bodies are `{ "error", "message" }` for 400 / 401 / 403 / 404; 422 is returned for schema-validation failures (e.g. incompatible field type change, malformed view options).

## Notes

- All Meta endpoints accept either header scheme.
- `PATCH` requests should include only the keys you're changing.
- `DELETE` is destructive — confirm before scripting. On Cloud / licensed, deleted tables, fields, views and (on NocoDB-managed sources) records land in the base trash and can be restored until the retention window ends (`listTrash` / `restoreFromTrash` over MCP); do not count on it for external sources.
- Path-parameter casing is inconsistent in the spec: `{baseId}` vs `{base_id}`. Both refer to the same NocoDB ID format (prefix `p`); the casing is purely a quirk of this OpenAPI document.
- v3 represents a clean break from older NocoDB Meta API versions (`/api/v1/db/meta/...`, `/api/v2/meta/...`) — older paths may still respond on legacy instances but are not documented here.
