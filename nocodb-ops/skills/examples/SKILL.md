---
name: examples
description: |
  NocoDB workflow examples, scenario walkthroughs, and practical patterns. Use when:
  - "show me a NocoDB example"
  - "workflow examples"
  - "scenario walkthroughs"
  - "how do I use NocoDB for..."
  - "NocoDB use case"
---

# NocoDB Examples

Practical examples and scenario walkthroughs for common NocoDB operations.

## Quick Examples

### List all tables in a base

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTablesList
Parameters: (none)
```

Returns every table name and ID in the connected base.

### Query records with a filter

```
Tool: mcp__plugin_nocodb-ops_nocodb__queryRecords
Parameters:
  tableId: "m_contacts"
  filter: { "group_operator": "AND", "filters": [
    { "field": "Status", "operator": "eq", "value": "Active" },
    { "field": "Created", "operator": "isWithin", "sub_operator": "pastMonth" } ] }
  sort: [{ "field": "Created", "direction": "desc" }]
  pageSize: 50
```

Returns active contacts created in the last 30 days, newest first, up to 50 per page. The same filter as a string: `where: "(Status,eq,Active)~and(Created,isWithin,pastMonth)"`.

### Create a new record

```
Tool: mcp__plugin_nocodb-ops_nocodb__createRecords
Parameters:
  tableId: "m_deals"
  records: [{ "fields": { "Title": "Enterprise License", "Value": 25000, "Stage": "Proposal" } }]
```

Inserts one deal record with the specified field values. Each record wraps its values in `fields`; a call takes at most 100 records.

### Count records matching a condition

```
Tool: mcp__plugin_nocodb-ops_nocodb__countRecords
Parameters:
  tableId: "m_tasks"
  filter: { "field": "Status", "operator": "neq", "value": "Done" }
```

Returns the number of incomplete tasks.

### Run an aggregation

```
Tool: mcp__plugin_nocodb-ops_nocodb__aggregate
Parameters:
  tableId: "m_deals"
  aggregations: [{ "field": "Value", "type": "sum" }]
  filterGroups: [{ "alias": "Closed Won", "filter": { "field": "Stage", "operator": "eq", "value": "Closed Won" } }]
```

Returns the total value of all closed-won deals as `{ "Closed Won": { "Value": ... } }`. Both `aggregations` and `filterGroups` are required.

### Get a table schema

```
Tool: mcp__plugin_nocodb-ops_nocodb__getTableSchema
Parameters:
  tableId: "m_contacts"
```

Returns all field names, types, and configurations for the contacts table.

## Full Scenario Walkthroughs

See `references/scenarios/` for step-by-step workflows:

- **crm-data-ops.md** -- Manage contacts, deals, and pipeline data. Find contacts by status, create deals, update stages, and aggregate pipeline value.
- **inventory-report.md** -- Track stock levels, count low-stock items, aggregate by category, and build summary reports.

## Tips for Business Users

- **Start with getTablesList** to discover available tables and their IDs.
- **Use getTableSchema** before querying to confirm exact field names (they are case-sensitive in `where` strings).
- **Paginate large results** -- `pageSize` defaults to 50 and is capped at 200; fetch pages instead of everything at once.
- **Write in batches of 100 or fewer** -- create, update and delete calls reject longer arrays outright.
- **Sort with objects** -- `sort: [{ "field": "Created", "direction": "desc" }]`.
- **Dates carry a sub-operator** -- `(Due,gte,exactDate,2026-06-01)`; ranges are two bounds, not `btw`.
- **Combine filters** with `~and` and `~or` (or a structured `filter` group) to narrow results precisely.
- **Use countRecords** before queryRecords to know how many results to expect.
