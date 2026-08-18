# Views, Filters, Sorts — CLI Reference

Imported from the official NocoDB agent-skills CLI. View management requires Enterprise (self-hosted or cloud); filter and sort APIs are available on the Free plan.

## Views

```bash
nc view:list pdef5678uvw mghi9012rst                                  # → vwmno7890abc
nc view:get  vwmno7890abc
nc view:update vwmno7890abc '{"title":"Renamed"}'
nc view:delete vwmno7890abc
```

### Create per view type

Grid:

```bash
nc view:create:grid pdef5678uvw mghi9012rst '{"title":"All Customers"}'
```

Form:

```bash
nc view:create:form pdef5678uvw mghi9012rst '{
  "title": "Intake Form",
  "subheading": "Tell us about your company"
}'
```

Gallery (needs an Attachment cover field):

```bash
nc view:create:gallery pdef5678uvw mghi9012rst '{
  "title": "Catalog",
  "fk_cover_image_col_id": "c_image_id"
}'
```

Kanban (needs a SingleSelect group field):

```bash
nc view:create:kanban pdef5678uvw mghi9012rst '{
  "title": "Pipeline",
  "fk_grp_col_id": "c_status_id"
}'
```

Calendar (needs a Date / DateTime range field):

```bash
nc view:create:calendar pdef5678uvw mghi9012rst '{
  "title": "Schedule",
  "calendar_range": [
    { "fk_from_column_id": "c_start_id", "fk_to_column_id": "c_end_id" }
  ]
}'
```

Map (needs a Geometry field):

```bash
nc view:create:map pdef5678uvw mghi9012rst '{
  "title": "Locations",
  "fk_geo_data_col_id": "c_geo_id"
}'
```

### View column visibility & order

```bash
nc view:column:list   vwmno7890abc
nc view:column:update vwmno7890abc <viewColumnId> '{"show":true,"order":3}'
```

## Filters (per view)

```bash
nc filter:list   vwmno7890abc
nc filter:create vwmno7890abc '{
  "fk_column_id": "c_status_id",
  "comparison_op": "eq",
  "value": "Active"
}'
nc filter:update <filterId> '{"value":"Archived"}'
nc filter:delete <filterId>
```

Logical groups — set `is_group: true` and nest children:

```bash
nc filter:create vwmno7890abc '{
  "is_group": true,
  "logical_op": "and",
  "children": [
    { "fk_column_id": "c_status_id",   "comparison_op": "eq", "value": "Active" },
    { "fk_column_id": "c_priority_id", "comparison_op": "eq", "value": "High" }
  ]
}'
```

`logical_op`: `and` | `or` | `not`. NocoDB supports up to 3 levels of nesting (see `FilterGroupLevel*` schemas in `nocodb-openapi.json`).

## Sorts (per view)

```bash
nc sort:list   vwmno7890abc
nc sort:create vwmno7890abc '{
  "fk_column_id": "c_created_at_id",
  "direction": "desc"
}'
nc sort:update <sortId> '{"direction":"asc"}'
nc sort:delete <sortId>
```

`direction`: `asc` | `desc`.

## View Sharing

```bash
nc view:share:create vwmno7890abc '{"meta":{"allowCSVDownload":true}}'
nc view:share:list  pdef5678uvw mghi9012rst
nc view:share:delete vwmno7890abc <sharedViewUuid>
```

## Filter Operator Reference

| Category | Operators |
|----------|-----------|
| Comparison | `eq`, `neq`, `gt`, `lt`, `gte`, `lte` |
| Range | `btw`, `nbtw` |
| Text | `like`, `nlike` |
| List | `in`, `allof`, `anyof`, `nallof`, `nanyof` |
| Empty | `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty` |
| Checkbox | `checked`, `notchecked` |
| Date keywords | `today`, `tomorrow`, `yesterday`, `oneWeekAgo`, `oneWeekFromNow`, `oneMonthAgo`, `oneMonthFromNow`, `daysAgo`, `daysFromNow`, `exactDate`, `isWithin` |

For a deeper filter syntax catalog, see `nocodb-ops/skills/cli-reference/references/filter-syntax.md`.
