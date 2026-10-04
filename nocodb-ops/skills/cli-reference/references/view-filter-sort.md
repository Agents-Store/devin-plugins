# Views, Filters, Sorts -- curl Recipes (read side)

Recipes on the Meta API v3 for **reading** views and their saved filters and sorts. The view APIs are available on cloud-hosted Enterprise and licensed self-hosted deployments (Business plan and above); filter and sort reads work on every plan. The `nocodb_api METHOD /path ['body']` wrapper is defined in `../SKILL.md`.

Creating and changing views (all nine types), their filters, sorts and field lists is the job of the **nocodb-dev** plugin (`view-management`), on MCP (`createView`, `createFilter`, `addSort`, ... via `listTools` / `callTool`) or REST.

## Views

```bash
nocodb_api GET /meta/bases/$BASE_ID/tables/$TABLE_ID/views              # → vwmno7890abc
nocodb_api GET /meta/bases/$BASE_ID/views/$VIEW_ID
```

View types: `grid`, `gallery`, `kanban`, `calendar`, `form`, `map`, `gantt`, `timeline`, `list`.

Pass a view's ID as `viewId` to the record endpoints (`GET /data/{baseId}/{tableId}/records?viewId=...`, MCP `queryRecords` / `countRecords`) to get exactly the rows, order and fields that view shows; a `sort` or `where` you add on top takes precedence over the view's own sorting and is applied over its filters.

## Filters (per view)

```bash
nocodb_api GET /meta/bases/$BASE_ID/views/$VIEW_ID/filters
```

A saved filter looks like this -- `field_id`, `operator`, `value`, plus a `sub_operator` on date fields:

```jsonc
{ "field_id": "cjkl3456opq", "operator": "eq", "value": "active" }
{ "field_id": "cdue123abcd", "operator": "gte", "sub_operator": "exactDate", "value": "2026-06-01" }
```

Groups use `group_operator` (`AND` | `OR`) with a nested `filters` array.

Operators: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `like`, `nlike`, `in`, `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty`, `checked`, `notchecked`, `allof`, `anyof`, `nallof`, `nanyof`, `isWithin`. `btw` / `nbtw` exist but the record tools reject them on numeric, date, rating, duration and checkbox fields -- prefer two bounds with `gte` and `lte`.

The string grammar used by `where` in record queries is in `filter-syntax.md`.

## Sorts (per view)

```bash
nocodb_api GET /meta/bases/$BASE_ID/views/$VIEW_ID/sorts
```

A saved sort looks like this:

```json
{ "field_id": "cjkl3456opq", "direction": "desc" }
```

`direction` is `asc` (default) or `desc`. (Record queries use the same object with a field **name**: `{"field": "Name", "direction": "desc"}`.)

## Scripts, Teams, API Tokens (Enterprise only)

```bash
nocodb_api GET /meta/bases/$BASE_ID/scripts
nocodb_api GET /meta/workspaces/$WORKSPACE_ID/teams
nocodb_api GET /meta/tokens
```

Creating or deleting these is an administrator task.
