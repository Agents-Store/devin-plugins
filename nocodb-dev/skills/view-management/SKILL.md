---
name: view-management
description: |
  Create, configure, and delete NocoDB views — Grid, Form, Gallery, Kanban, Calendar, Map, Gantt, Timeline, List. Use when:
  - "create a kanban view"
  - "add a calendar / gantt / timeline view"
  - "build a form for intake"
  - "make a gallery of products"
  - "set up filters on a view"
  - "delete a view"
  - "show / hide columns on a view"
---

# View Management

NocoDB tables can have multiple views — different lenses on the same data. The view APIs are available on cloud-hosted Enterprise and on licensed self-hosted deployments (Business plan and above); reading views works on every plan.

View writes go through the MCP schema tools on **Cloud / licensed** (`listTools` categories `views`, `filters`, `sorts`, `shared-views`, then `callTool`) and through the **REST API** (`curl` on Meta API v3) as the fallback. See **mcp-patterns** for the contract.

## Nine View Types

| Type | Best for | Required in `options` |
|------|----------|-----------------------|
| **grid** | Spreadsheet-style browsing, bulk edits | none |
| **form** | Data collection, intake | none |
| **gallery** | Card layout for catalogs / portfolios | `cover_field_id` (Attachment) recommended |
| **kanban** | Status tracking, pipeline stages | `stack_by.field_id` (SingleSelect) |
| **calendar** | Scheduling, deadlines | `date_ranges[]` (Date / DateTime) |
| **map** | Geo-located records | `geo_data_field_id` |
| **gantt** | Project plans with dependencies | `date_dependency` (an object, or `null` for the table default; `date_ranges` is rejected) |
| **timeline** | Roadmaps, resource schedules | `date_ranges[]` (several allowed) |
| **list** | Hierarchies across linked tables | `levels[]`, optional `show_empty_parents`, `row_height` |

Every view also takes `lock_type`: `collaborative` (default, anyone with access edits), `locked` (read-only configuration) or `personal` (only the owner sees their configuration).

## Discover First

```
mcp__plugin_nocodb-dev_nocodb__getTableSchema  tableId: <tableId>
```

The `views` array in the response lists every existing view with its name, type, ID, and config. `listViews` / `getView` read one table's views and a single view in detail.

## Create a View

In the Meta API v3, **all view types use one endpoint** — `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/views` — with a `type` discriminator. Type-specific config goes inside `options`.

REST:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '<JSON payload>' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/tables/${TABLE_ID}/views"
```

MCP (Cloud / licensed):

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "views"
mcp__plugin_nocodb-dev_nocodb__callTool   name: "createView"
  arguments: { tableId: "<tableId>", title: "All Customers", type: "grid" }
```

The MCP `createView` takes the same `title`, `type`, `lock_type`, `options` and `fields`; filters and sorts are separate tools (below). The payloads in this skill are the REST bodies — for MCP, lift the keys into `arguments` next to `tableId`.

### Grid

```json
{ "title": "All Customers", "type": "grid" }
```

Optional `options`: `row_height` (`short`, `medium`, `tall`, `extra`) and `groups` — an array of `{ "field_id", "direction" }`, outermost level first.

### Form

`ViewOptionsForm` keys go inside `options`:

```json
{
  "title": "Intake Form",
  "type":  "form",
  "options": {
    "form_title":                "Contact us",
    "form_description":          "Tell us about your company",
    "thank_you_message":         "Thanks!",
    "redirect_url":              "https://example.com/thanks",
    "form_redirect_after_secs":  5,
    "reset_form_after_submit":   true,
    "show_submit_another_button": true,
    "send_response_email_to":    "ops@example.com"
  }
}
```

`form_redirect_after_secs` has no effect unless `redirect_url` is set. Further form keys: `submit_button_label`, `form_hide_banner`, `form_hide_branding`, `form_background_color`, `banner`, `logo`, and per-field settings in `fields_by_id` (`{ "<fieldId>": { "alias": "Label", "required": true, "description": "Help text", "validators": [...] } }` — the label key is `alias`). Field order and visibility come from `fields`, not `fields_by_id`.

### Gallery

```json
{
  "title": "Product Catalog",
  "type":  "gallery",
  "options": { "cover_field_id": "<attachmentFieldId>" }
}
```

### Kanban

Requires a `SingleSelect` field. `options.stack_by` is **required**:

```json
{
  "title": "Pipeline",
  "type":  "kanban",
  "options": {
    "stack_by": { "field_id": "<singleSelectFieldId>", "stack_order": ["New", "Active", "Done"] },
    "cover_field_id": "<attachmentFieldId>"
  }
}
```

`stack_order` and `cover_field_id` are optional (the stacks default to the order the select field declares).

### Calendar

Requires at least one Date / DateTime field; the end field is optional (omit it for a single point in time). `options.date_ranges` is **required**:

```json
{
  "title": "Schedule",
  "type":  "calendar",
  "options": {
    "date_ranges": [
      { "start_date_field_id": "<startDateFieldId>", "end_date_field_id": "<endDateFieldId>" }
    ]
  }
}
```

### Map

Requires a geographic point field (`Geometry`).

```json
{
  "title": "Office Locations",
  "type":  "map",
  "options": { "geo_data_field_id": "<geometryFieldId>" }
}
```

### Gantt

`options.date_dependency` is **required** on create; pass `null` to take the table's default rule. A Gantt view rejects `date_ranges`.

```json
{
  "title": "Project Plan",
  "type":  "gantt",
  "options": {
    "date_dependency": {
      "dates": { "start_field_id": "<startFieldId>", "end_field_id": "<endFieldId>" },
      "dependency": {
        "linkrow_field_id": "<selfLinkFieldId>",
        "linkrow_role": "predecessors",
        "connection_type": "end-to-start",
        "buffer_type": "none",
        "buffer_days": 0
      },
      "include_weekends": true,
      "is_active": true
    }
  }
}
```

An update replaces the whole `date_dependency` object — send the complete rule.

### Timeline

Like Calendar, `options.date_ranges` is required, and a Timeline may carry several ranges:

```json
{
  "title": "Roadmap",
  "type":  "timeline",
  "options": {
    "date_ranges": [
      { "start_date_field_id": "<startFieldId>", "end_date_field_id": "<endFieldId>" }
    ]
  }
}
```

### List

A hierarchical list across linked tables; each level names its table and the link that leads to it:

```json
{
  "title": "Outline",
  "type":  "list",
  "options": {
    "levels": [
      { "level": 1, "table_id": "<parentTableId>" },
      { "level": 2, "table_id": "<childTableId>", "link_field_id": "<linkFieldIdOnParent>" }
    ],
    "show_empty_parents": false,
    "row_height": "short"
  }
}
```

### Optional create-time extras

The same `POST` accepts initial sorts, filters, fields, and row colouring:

```json
{
  "title": "Active high-priority",
  "type":  "grid",
  "filters": {
    "group_operator": "AND",
    "filters": [
      { "field_id": "<statusId>",   "operator": "eq", "value": "Active" },
      { "field_id": "<priorityId>", "operator": "eq", "value": "High"   }
    ]
  },
  "sorts":  [ { "field_id": "<createdAtId>", "direction": "desc" } ],
  "fields": [ { "field_id": "<idField>", "show": true } ],
  "row_coloring": { "mode": "select", "field_id": "<priorityId>" }
}
```

## Update a View

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Renamed"}' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/views/${VIEW_ID}"
```

MCP: `callTool name: "updateView"  arguments: { viewId: "<viewId>", title: "Renamed" }`. A view keeps its type — create a new view instead of changing it.

Type-specific config (e.g. Kanban's stacking field, Calendar's ranges) updates through `options`:

```json
{ "options": { "stack_by": { "field_id": "<newFieldId>" } } }
```

Changing a Kanban's stacking field does not migrate cards — they regroup automatically by the new field's value, with any unmatched values landing in the "Uncategorized" column.

## Show / Hide / Reorder Fields Per View

Each view holds its own field list. Send the **complete ordered list** in `fields` — array order sets the field order and every field you omit is hidden:

```bash
curl -sS -X PATCH \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "fields": [
        { "field_id": "<titleFieldId>",  "show": true, "width": 240 },
        { "field_id": "<statusFieldId>", "show": true },
        { "field_id": "<notesFieldId>",  "show": false }
      ] }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/views/${VIEW_ID}"
```

Read the current list first (`getView` / `GET …/views/{viewId}`) so you do not hide fields by accident. Grid views also take `width` and a footer `aggregation` per field. A new field added to a table is visible by default in every view; you can hide it per view.

## Filters and Sorts

See **`cli-reference/references/view-filter-sort.md`** for the full grammar. Quick recipes:

Filter (e.g., "Active customers only") — Meta API v3 uses `field_id` and `operator`:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "field_id": "<statusFieldId>", "operator": "eq", "value": "Active" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/views/${VIEW_ID}/filters"
```

Sort (e.g., "Newest first") — Meta API v3 uses `field_id` and `direction`:

```bash
curl -sS -X POST \
  -H "xc-token: ${NOCODB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "field_id": "<createdAtFieldId>", "direction": "desc" }' \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/views/${VIEW_ID}/sorts"
```

Filter group (AND of two conditions):

```json
{
  "group_operator": "AND",
  "filters": [
    { "field_id":"<statusId>",   "operator":"eq", "value":"Active" },
    { "field_id":"<priorityId>", "operator":"eq", "value":"High" }
  ]
}
```

`PUT /views/{viewId}/filters` replaces the whole filter set atomically; `POST` appends. NocoDB supports up to 3 levels of nested filter groups (per `FilterGroupLevel*` schemas in `nocodb-meta-openapi.json`). For Date / DateTime fields add a `sub_operator`, e.g. `{ "field_id": "<dueId>", "operator": "lt", "sub_operator": "today" }` or `"sub_operator": "exactDate", "value": "2026-06-01"`.

MCP equivalents: `createFilter {viewId, filter}`, `replaceFilters {viewId, filter}`, `updateFilter`, `deleteFilter {viewId, filterId}`; `addSort {viewId, field_id, direction}`, `updateSort`, `deleteSort {viewId, sortId}`.

## Delete a View

**Destructive — confirm first.** Note: every table must keep at least one view; NocoDB rejects the delete if it would leave the table with zero views.

```bash
curl -sS -X DELETE \
  -H "xc-token: ${NOCODB_TOKEN}" \
  "${NOCODB_URL}/api/v3/meta/bases/${BASE_ID}/views/${VIEW_ID}"
```

MCP: `callTool name: "deleteView"  arguments: { viewId: "<viewId>" }`. On Cloud / licensed the deleted view goes to the base trash and can be restored (`listTrash`, `restoreFromTrash`) until the retention window ends.

## Sharing a View

The Meta API v3 spec has no endpoint for public share links. On Cloud / licensed, use the MCP `shared-views` category:

```
mcp__plugin_nocodb-dev_nocodb__listTools  category: "shared-views"
mcp__plugin_nocodb-dev_nocodb__callTool   name: "shareView"
  arguments: { viewId: "<viewId>", password: "<optional>", allow_csv_download: false }
```

`shareView` on an already-shared view keeps the same URL and only applies the settings you pass; `unshareView { viewId }` revokes the link (a later share issues a different URL). `listSharedViews` (read tool) shows what is shared. On Community Edition, share views in the NocoDB UI.

## Pre-Flight Checklist

| View type | Pre-flight |
|-----------|-----------|
| Grid | none |
| Form | none |
| Gallery | An Attachment field exists, or the cards will look bare |
| Kanban | A SingleSelect field with at least 2 options exists |
| Calendar / Timeline | A Date or DateTime field exists (a second one for the end of a range) |
| Gantt | Start and end Date fields; for dependencies, a self-referencing link field |
| List | The linked tables and the link fields between them exist |
| Map | A Geometry field exists with at least one record's coordinates set |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 "stack_by required" | Kanban without `options.stack_by` | Provide `options.stack_by.field_id` referencing a SingleSelect |
| 422 "date_dependency required" | Gantt without `options.date_dependency` | Pass a rule, or `null` for the table default; do not send `date_ranges` |
| 422 "Column type not supported" | Kanban stack field isn't SingleSelect / Calendar field isn't Date | Use a compatible field or convert it first |
| Unknown option key rejected | A key from older NocoDB tooling, or the wrong view type's key | Use the keys listed above; check `ViewOptions*` in `nocodb-meta-openapi.json` |
| Cards show no image | Gallery missing `cover_field_id`, or the attachment field is empty | Set the cover field; or upload an attachment to the records |
| Calendar shows nothing | Records have null Date values, or a filter excludes them | Verify dates are populated; check view filters |
| Cannot delete view | Last remaining view on the table | Create another view first, then delete |
| Share link returns 404 | Link was revoked | Share again — the URL is new |
| `createView` rejected with a plan error | The plan does not include the view APIs | Cloud Enterprise or licensed self-hosted (Business and above) is required |
