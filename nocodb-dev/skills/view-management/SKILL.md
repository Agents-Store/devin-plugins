---
name: view-management
description: |
  Create, configure, and delete NocoDB views — Grid, Form, Gallery, Kanban, Calendar, Map. Use when:
  - "create a kanban view"
  - "add a calendar view"
  - "build a form for intake"
  - "make a gallery of products"
  - "set up filters on a view"
  - "delete a view"
  - "show / hide columns on a view"
---

# View Management

NocoDB tables can have multiple views — different lenses on the same data. View management requires Enterprise (self-hosted or cloud-hosted Enterprise plan) for create/update/delete; reads are available on Free.

## Six View Types

| Type | Best for | Required field |
|------|----------|----------------|
| **Grid** | Spreadsheet-style browsing, bulk edits | none |
| **Form** | Data collection, intake | none |
| **Gallery** | Card layout for catalogs / portfolios | Attachment cover field (recommended) |
| **Kanban** | Status tracking, pipeline stages | SingleSelect group field |
| **Calendar** | Scheduling, deadlines | Date or DateTime field |
| **Map** | Geo-located records | Geometry field |

## Discover First

```
mcp__nocodb__getTableSchema  tableId: <tableId>
```

The `views` array in the response lists every existing view with its name, type, ID, and config.

## Create a View

In the Meta API v3, **all view types use one endpoint** — `POST /api/v3/meta/bases/{baseId}/tables/{tableId}/views` — with a `type` discriminator (`grid`, `gallery`, `kanban`, `calendar`, `map`, `form`). Type-specific config goes inside `options`.

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '<JSON payload>' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/tables/$TABLE_ID/views"
```

The CLI still exposes per-type subcommands (`nc view:create:grid`, `nc view:create:kanban`, etc.) which generate the right `type` field internally.

### Grid

```bash
nc view:create:grid <baseId> <tableId> '{"title":"All Customers"}'
```

API payload:

```json
{ "title": "All Customers", "type": "grid" }
```

### Form

```bash
nc view:create:form <baseId> <tableId> '{
  "title": "Intake Form",
  "subheading": "Tell us about your company"
}'
```

API payload (`ViewOptionsForm` keys go inside `options`):

```json
{
  "title": "Intake Form",
  "type":  "form",
  "options": {
    "subheading":         "Tell us about your company",
    "success_msg":        "Thanks!",
    "redirect_url":       "https://example.com/thanks",
    "redirect_after_secs": 5,
    "show_blank_form":     true,
    "submit_another_btn":  true,
    "email":               "ops@example.com"
  }
}
```

### Gallery

```bash
nc view:create:gallery <baseId> <tableId> '{
  "title": "Product Catalog",
  "fk_cover_image_col_id": "<attachmentColumnId>"
}'
```

API payload:

```json
{
  "title": "Product Catalog",
  "type":  "gallery",
  "options": { "fk_cover_image_col_id": "<attachmentColumnId>" }
}
```

### Kanban

Requires a `SingleSelect` group field.

```bash
nc view:create:kanban <baseId> <tableId> '{
  "title": "Pipeline",
  "fk_grp_col_id": "<singleSelectColumnId>"
}'
```

API payload — `options` is **required** for kanban:

```json
{
  "title": "Pipeline",
  "type":  "kanban",
  "options": { "fk_grp_col_id": "<singleSelectColumnId>" }
}
```

### Calendar

Requires at least one Date / DateTime field; optional second field for end-of-event.

```bash
nc view:create:calendar <baseId> <tableId> '{
  "title": "Schedule",
  "calendar_range": [
    { "fk_from_column_id": "<startDateColumnId>", "fk_to_column_id": "<endDateColumnId>" }
  ]
}'
```

API payload — `options` is **required**:

```json
{
  "title": "Schedule",
  "type":  "calendar",
  "options": {
    "calendar_range": [
      { "fk_from_column_id": "<startDateColumnId>", "fk_to_column_id": "<endDateColumnId>" }
    ]
  }
}
```

### Map

Requires a `Geometry` field.

```bash
nc view:create:map <baseId> <tableId> '{
  "title": "Office Locations",
  "fk_geo_data_col_id": "<geometryColumnId>"
}'
```

API payload:

```json
{
  "title": "Office Locations",
  "type":  "map",
  "options": { "fk_geo_data_col_id": "<geometryColumnId>" }
}
```

### Optional create-time extras

The same `POST` accepts initial sorts, filters, fields, and row colouring:

```json
{
  "title": "Active high-priority",
  "type":  "grid",
  "filters": {
    "logical_op": "and",
    "filters": [
      { "field_id": "<statusId>",   "operator": "eq", "value": "Active" },
      { "field_id": "<priorityId>", "operator": "eq", "value": "High"   }
    ]
  },
  "sorts":  [ { "field_id": "<createdAtId>", "order": "desc" } ],
  "fields": [ { "field_id": "<idField>", "show": true } ],
  "row_coloring": { "type": "select", "field_id": "<priorityId>" }
}
```

## Update a View

```bash
nc view:update <viewId> '{"title":"Renamed"}'
```

API:

```bash
curl -sS -X PATCH \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Renamed"}' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/views/$VIEW_ID"
```

Type-specific config (e.g. Kanban's group column, Calendar's range) updates through `options`:

```json
{ "options": { "fk_grp_col_id": "<newColumnId>" } }
```

Changing a Kanban's group column does not migrate cards — they regroup automatically by the new column's value, with any unmatched values landing in the "Uncategorized" column.

## Show / Hide / Reorder Columns Per View

Each view holds its own column-visibility table.

```bash
nc view:column:list   <viewId>
nc view:column:update <viewId> <viewColumnId> '{"show":true,"order":3}'
```

A new field added to a table is visible by default in every view; you can hide it per-view.

## Filters and Sorts

See **`cli-reference/references/view-filter-sort.md`** for the full grammar. Quick recipes:

Filter (e.g., "Active customers only") — Meta API v3 uses `field_id` and `operator`:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "field_id": "<statusColumnId>", "operator": "eq", "value": "Active" }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/views/$VIEW_ID/filters"
```

Sort (e.g., "Newest first") — Meta API v3 uses `field_id` and `order`:

```bash
curl -sS -X POST \
  -H "xc-token: $NOCODB_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "field_id": "<createdAtColumnId>", "order": "desc" }' \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/views/$VIEW_ID/sorts"
```

Filter group (AND of two conditions):

```json
{
  "logical_op": "and",
  "filters": [
    { "field_id":"<statusId>",   "operator":"eq", "value":"Active" },
    { "field_id":"<priorityId>", "operator":"eq", "value":"High" }
  ]
}
```

`PUT /views/{viewId}/filters` replaces the whole filter set atomically; `POST` appends. NocoDB supports up to 3 levels of nested filter groups (per `FilterGroupLevel*` schemas in `nocodb-meta-openapi.json`).

> The CLI (`nc filter:create`, `nc sort:create`) historically used `fk_column_id` / `comparison_op` / `direction` — the names you'll see in older NocoDB tooling. The Meta API v3 uses `field_id` / `operator` / `order`. The CLI translates between them.

## Delete a View

**Destructive — confirm first.** Note: every table must keep at least one view; NocoDB rejects the delete if it would leave the table with zero views.

```bash
nc view:delete <viewId>
```

API:

```bash
curl -sS -X DELETE \
  -H "xc-token: $NOCODB_API_TOKEN" \
  "$NOCODB_URL/api/v3/meta/bases/$BASE_ID/views/$VIEW_ID"
```

## Sharing a View

Share-link generation:

```bash
nc view:share:create <viewId> '{"meta":{"allowCSVDownload":true}}'
```

Returns a UUID; the public URL is `$NOCODB_URL/dashboard/#/nc/view/<uuid>`.

Update share settings (password, allowed actions):

```bash
nc view:share:update <viewId> '{"password":"hunter2","meta":{"allowCSVDownload":false}}'
```

Delete share link:

```bash
nc view:share:delete <viewId> <sharedViewUuid>
```

## Pre-Flight Checklist

| View type | Pre-flight |
|-----------|-----------|
| Grid | none |
| Form | none |
| Gallery | An Attachment field exists, or the cards will look bare |
| Kanban | A SingleSelect field with at least 2 options exists |
| Calendar | A Date or DateTime field exists |
| Map | A Geometry field exists with at least one record's coordinates set |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 422 "fk_grp_col_id required" | Kanban without group column | Provide `fk_grp_col_id` referencing a SingleSelect |
| 422 "Column type not supported" | Kanban group column isn't SingleSelect / Calendar field isn't Date | Use a compatible field or convert it first |
| Cards show no image | Gallery missing `fk_cover_image_col_id`, or attachment field is empty | Set the cover field; or upload an attachment to the records |
| Calendar shows nothing | Records have null Date values, or filter excludes them | Verify dates are populated; check view filters |
| Cannot delete view | Last remaining view on the table | Create another view first, then delete |
| Share link returns 404 | Share-link UUID expired or revoked | Regenerate with `view:share:create` |
