# Views, Filters, Sorts — curl Recipes

The view APIs are available on cloud-hosted Enterprise and licensed self-hosted deployments (Business plan and above); filter and sort reads work on every plan. The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md`. On Cloud / licensed the MCP tools `createView`, `createFilter`, `replaceFilters`, `addSort`, … take the same keys (see **mcp-patterns**).

## Views

```bash
nocodb_api GET    /meta/bases/$BASE_ID/tables/$TABLE_ID/views              # → vwmno7890abc
nocodb_api GET    /meta/bases/$BASE_ID/views/$VIEW_ID
nocodb_api PATCH  /meta/bases/$BASE_ID/views/$VIEW_ID '{"title":"Renamed"}'
nocodb_api DELETE /meta/bases/$BASE_ID/views/$VIEW_ID
```

### Create per view type

All types use `POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views`; the type goes in the body and type-specific settings go inside `options`.

Grid:

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{"title":"All Customers","type":"grid"}'
```

Form:

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Intake Form",
  "type": "form",
  "options": { "form_title": "Contact us", "form_description": "Tell us about your company" }
}'
```

Gallery (needs an Attachment cover field):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Catalog",
  "type": "gallery",
  "options": { "cover_field_id": "c_image_id" }
}'
```

Kanban (needs a SingleSelect stacking field):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Pipeline",
  "type": "kanban",
  "options": { "stack_by": { "field_id": "c_status_id" } }
}'
```

Calendar (needs a Date / DateTime range):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Schedule",
  "type": "calendar",
  "options": { "date_ranges": [ { "start_date_field_id": "c_start_id", "end_date_field_id": "c_end_id" } ] }
}'
```

Timeline (several ranges allowed):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Roadmap",
  "type": "timeline",
  "options": { "date_ranges": [ { "start_date_field_id": "c_start_id", "end_date_field_id": "c_end_id" } ] }
}'
```

Gantt (`date_dependency` is required; `null` takes the table default; `date_ranges` is rejected):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Plan",
  "type": "gantt",
  "options": { "date_dependency": null }
}'
```

Map (needs a geographic point field):

```bash
nocodb_api POST /meta/bases/$BASE_ID/tables/$TABLE_ID/views '{
  "title": "Locations",
  "type": "map",
  "options": { "geo_data_field_id": "c_geo_id" }
}'
```

List — see **view-management** for the `levels` shape. Every view also accepts `lock_type`: `collaborative` (default), `locked`, `personal`.

### View field visibility & order

Send the complete ordered list — every field you omit is hidden:

```bash
nocodb_api PATCH /meta/bases/$BASE_ID/views/$VIEW_ID '{
  "fields": [
    { "field_id": "c_title_id",  "show": true, "width": 240 },
    { "field_id": "c_status_id", "show": true },
    { "field_id": "c_notes_id",  "show": false }
  ]
}'
```

## Filters (per view)

```bash
nocodb_api GET    /meta/bases/$BASE_ID/views/$VIEW_ID/filters
nocodb_api POST   /meta/bases/$BASE_ID/views/$VIEW_ID/filters '{
  "field_id": "c_status_id",
  "operator": "eq",
  "value": "Active"
}'
nocodb_api PATCH  /meta/bases/$BASE_ID/filters/$FILTER_ID '{"value":"Archived"}'
nocodb_api DELETE /meta/bases/$BASE_ID/filters/$FILTER_ID
```

Logical groups — `group_operator` is `AND` or `OR`; members may be conditions or nested groups:

```bash
nocodb_api POST /meta/bases/$BASE_ID/views/$VIEW_ID/filters '{
  "group_operator": "AND",
  "filters": [
    { "field_id": "c_status_id",   "operator": "eq", "value": "Active" },
    { "field_id": "c_priority_id", "operator": "eq", "value": "High" }
  ]
}'
```

NocoDB supports up to 3 levels of nesting (see `FilterGroupLevel*` schemas in `nocodb-meta-openapi.json`). `PUT /meta/bases/$BASE_ID/views/$VIEW_ID/filters` replaces the whole filter set with the group you send.

Date / DateTime fields need a `sub_operator` — `today`, `yesterday`, `daysAgo` (value = number), `exactDate` (value = `YYYY-MM-DD`), `isWithin` with `pastWeek`, … — for example:

```bash
nocodb_api POST /meta/bases/$BASE_ID/views/$VIEW_ID/filters '{
  "field_id": "c_due_id", "operator": "lt", "sub_operator": "today"
}'
```

## Sorts (per view)

```bash
nocodb_api GET    /meta/bases/$BASE_ID/views/$VIEW_ID/sorts
nocodb_api POST   /meta/bases/$BASE_ID/views/$VIEW_ID/sorts '{
  "field_id": "c_created_at_id",
  "direction": "desc"
}'
nocodb_api PATCH  /meta/bases/$BASE_ID/sorts/$SORT_ID '{"direction":"asc"}'
nocodb_api DELETE /meta/bases/$BASE_ID/sorts/$SORT_ID
```

`direction`: `asc` | `desc` (default `asc`).

## View Sharing

Public share links are not part of the REST spec. On Cloud / licensed use the MCP `shareView` / `unshareView` tools (category `shared-views`); otherwise share from the NocoDB UI.

## Filter Operator Reference

| Category | Operators |
|----------|-----------|
| Comparison | `eq`, `neq`, `gt`, `lt`, `gte`, `lte` |
| Range | `btw`, `nbtw` (the MCP record tools reject them on numeric, rating, duration, date and checkbox fields — prefer two bounds with `gte` / `lte`) |
| Text | `like`, `nlike` |
| List | `in`, `allof`, `anyof`, `nallof`, `nanyof` |
| Empty | `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty` |
| Checkbox | `checked`, `notchecked` |
| Date | `isWithin`, plus a `sub_operator` from `today`, `tomorrow`, `yesterday`, `oneWeekAgo`, `oneWeekFromNow`, `oneMonthAgo`, `oneMonthFromNow`, `daysAgo`, `daysFromNow`, `exactDate`, `pastWeek`, `pastMonth`, `pastYear`, `nextWeek`, `nextMonth`, `nextYear`, `pastNumberOfDays`, `nextNumberOfDays` |

For the `where` string grammar used by record queries, see `nocodb-ops/skills/cli-reference/references/filter-syntax.md`.
