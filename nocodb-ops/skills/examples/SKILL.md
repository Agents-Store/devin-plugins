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
Tool: mcp__nocodb__getTablesList
Parameters: (none)
```

Returns every table name and ID in the connected base.

### Query records with a filter

```
Tool: mcp__nocodb__queryRecords
Parameters:
  tableId: "m_contacts"
  where: "(Status,eq,Active)~and(Created,isWithin,pastMonth)"
  pageSize: 50
```

Returns active contacts created in the last 30 days, up to 50 per page.

### Create a new record

```
Tool: mcp__nocodb__createRecords
Parameters:
  tableId: "m_deals"
  records: [{"Title": "Enterprise License", "Value": 25000, "Stage": "Proposal"}]
```

Inserts one deal record with the specified field values.

### Count records matching a condition

```
Tool: mcp__nocodb__countRecords
Parameters:
  tableId: "m_tasks"
  where: "(Status,neq,Done)"
```

Returns the number of incomplete tasks.

### Run an aggregation

```
Tool: mcp__nocodb__aggregate
Parameters:
  tableId: "m_deals"
  aggregation: [{"field": "Value", "type": "sum"}]
  where: "(Stage,eq,Closed Won)"
```

Returns the total value of all closed-won deals.

### Get a table schema

```
Tool: mcp__nocodb__getTableSchema
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
- **Use getTableSchema** before querying to confirm exact field names (they are case-sensitive).
- **Paginate large results** -- set `pageSize` to 50 or 100 instead of fetching everything.
- **Combine filters** with `~and` and `~or` to narrow results precisely.
- **Use countRecords** before queryRecords to know how many results to expect.
