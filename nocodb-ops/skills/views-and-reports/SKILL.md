---
name: views-and-reports
description: |
  Build reports, summaries, and dashboards from NocoDB data. Use when:
  - "create a report"
  - "summarize this table"
  - "show sales by region"
  - "build a dashboard"
  - "aggregate data"
  - "what views exist on this table?"
  - "kanban board"
  - "monthly summary"
  - "count by category"
  - "average order value"
---

# Views and Reports

## Discovering Existing Views

NocoDB tables can have multiple views. To see what views already exist on a table, call `mcp__plugin_nocodb-ops_nocodb__getTableSchema` with the `tableId`. The response includes a list of views with their names and types.

```
mcp__plugin_nocodb-ops_nocodb__getTableSchema  tableId: "tbl_abc123"
```

The schema response contains a `views` section listing every view configured on that table. Each view has a name, type, and ID.

## View Types

NocoDB supports nine view types. Understanding them helps when discussing data with business users.

| View Type | Purpose | Best For |
|-----------|---------|----------|
| **Grid** | Spreadsheet-style rows and columns | General browsing, editing, bulk updates |
| **Kanban** | Cards grouped by a single-select field | Tracking status, pipeline stages, workflows |
| **Gallery** | Card layout showing images and key fields | Product catalogs, team directories, portfolios |
| **Form** | Input form for adding new records | Data collection, intake requests, surveys |
| **Calendar** | Date-based calendar display | Scheduling, deadlines, event planning |
| **Timeline** | Records as bars on a time axis | Roadmaps, resource schedules |
| **Gantt** | Timeline bars with dependencies between records | Project plans with task ordering |
| **Map** | Records plotted on a map from a geographic field | Locations, field service, stores |
| **List** | Hierarchy across linked tables | Parent / child overviews (customers and their orders) |

This plugin **reads** views (`getTableSchema` lists them; `queryRecords` and `countRecords` accept a `viewId` so the view's own filters, sorts and field visibility apply). It does not create or change them. When a user asks for a kanban board, calendar or any other view, explain what the view does and point to the NocoDB web interface, or to the **nocodb-dev** plugin (`view-management`) -- on Cloud / licensed servers its MCP tools `createView`, `createFilter` and `addSort` (via `listTools` / `callTool`) build views, and on Community Edition the REST recipes do.

## Building Reports with Aggregate

The `mcp__plugin_nocodb-ops_nocodb__aggregate` tool is the primary way to build numeric reports. It computes calculations across an entire table or within filtered segments.

### Aggregation Types

| Type | What It Calculates |
|------|-------------------|
| `sum` | Total of all values in a numeric field |
| `count` | Number of records |
| `avg` | Average (mean) value |
| `min` | Smallest value |
| `max` | Largest value |
| `median` | Middle value when sorted |
| `std_dev` | How spread out the values are |
| `range` | Difference between max and min |
| `count_empty`, `count_filled`, `count_unique` | Empty, filled and distinct values (any field type) |
| `percent_empty`, `percent_filled`, `percent_unique` | The same as percentages |
| `checked`, `unchecked`, `percent_checked`, `percent_unchecked` | Checkbox fields |
| `earliest_date`, `latest_date`, `date_range`, `month_range` | Date fields |

### Basic Aggregation

Calculate a single number across the whole table. Both `aggregations` and `filterGroups` are **required**; for one overall result use a single group with no filter:

```
mcp__plugin_nocodb-ops_nocodb__aggregate
  tableId: "tbl_abc123"
  aggregations: [
    { "field": "Amount", "type": "sum" },
    { "field": "Amount", "type": "avg" },
    { "field": "Amount", "type": "count" }
  ]
  filterGroups: [ { "alias": "All" } ]
```

This returns the total amount, average amount, and record count for the entire table, as `{ "All": { "Amount.sum": ..., "Amount.avg": ..., "Amount.count": ... } }` -- when a field carries two or more aggregations the keys are `<field>.<type>`; with one aggregation per field the key is the bare field title.

### Segmented Reports with Filter Groups

Filter groups let you break down numbers by category. Each filter group has an alias (the label) and a filter -- the structured `filter` object (preferred) or a `where` string; pass one of the two per group.

```
mcp__plugin_nocodb-ops_nocodb__aggregate
  tableId: "tbl_abc123"
  aggregations: [
    { "field": "Revenue", "type": "sum" },
    { "field": "Revenue", "type": "count" }
  ]
  filterGroups: [
    { "alias": "North", "filter": { "field": "Region", "operator": "eq", "value": "North" } },
    { "alias": "South", "filter": { "field": "Region", "operator": "eq", "value": "South" } },
    { "alias": "East",  "filter": { "field": "Region", "operator": "eq", "value": "East" } },
    { "alias": "West",  "where": "(Region,eq,West)" }
  ]
```

This returns sum and count for each region separately -- one result block per filter group, keyed by its alias. (`aggregate` splits by the filters you write; it does not group by a field on its own.)

### Counting per Distinct Value

When the question is "how many per status / region / owner", `groupByRecords` does it in one call without listing every value in advance:

```
mcp__plugin_nocodb-ops_nocodb__groupByRecords
  tableId: "tbl_orders"
  fieldId: "<status field id from getTableSchema>"
```

It returns each value with its count, so a follow-up `queryRecords` can filter to one group.

## Report Examples

### Sales Summary by Region

```
mcp__plugin_nocodb-ops_nocodb__aggregate
  tableId: "tbl_orders"
  aggregations: [
    { "field": "Total", "type": "sum" },
    { "field": "Total", "type": "avg" },
    { "field": "Total", "type": "count" }
  ]
  filterGroups: [
    { "alias": "North America", "filter": { "field": "Region", "operator": "eq", "value": "North America" } },
    { "alias": "Europe", "filter": { "field": "Region", "operator": "eq", "value": "Europe" } },
    { "alias": "Asia", "filter": { "field": "Region", "operator": "eq", "value": "Asia" } }
  ]
```

Present the results as a formatted table with columns for Region, Total Sales, Average Order, and Order Count.

### Monthly Active Records

Use date filters in filter groups to segment by time period. Date fields always carry a sub-operator; `isWithin` windows are relative to today (`pastWeek` = the last 7 days, `pastMonth` = the last 30 days -- there is no `thisMonth`), and a specific calendar month is two `exactDate` bounds:

```
mcp__plugin_nocodb-ops_nocodb__aggregate
  tableId: "tbl_activities"
  aggregations: [
    { "field": "Id", "type": "count" }
  ]
  filterGroups: [
    { "alias": "October 2026", "filter": { "group_operator": "AND", "filters": [
        { "field": "CreatedAt", "operator": "gte", "sub_operator": "exactDate", "value": "2026-10-01" },
        { "field": "CreatedAt", "operator": "lte", "sub_operator": "exactDate", "value": "2026-10-31" } ] } },
    { "alias": "Past 30 days", "where": "(CreatedAt,isWithin,pastMonth)" },
    { "alias": "Past Week", "where": "(CreatedAt,isWithin,pastWeek)" }
  ]
```

### Inventory Counts by Category

```
mcp__plugin_nocodb-ops_nocodb__aggregate
  tableId: "tbl_inventory"
  aggregations: [
    { "field": "Quantity", "type": "sum" },
    { "field": "Quantity", "type": "min" },
    { "field": "Quantity", "type": "max" }
  ]
  filterGroups: [
    { "alias": "Electronics", "filter": { "field": "Category", "operator": "eq", "value": "Electronics" } },
    { "alias": "Clothing", "filter": { "field": "Category", "operator": "eq", "value": "Clothing" } },
    { "alias": "Food", "filter": { "field": "Category", "operator": "eq", "value": "Food" } }
  ]
```

## Quick Data Summaries with Query

When you need the actual records behind a number (not just aggregates), use `mcp__plugin_nocodb-ops_nocodb__queryRecords` with sorting and field selection.

### Top 10 Highest-Value Orders

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_orders"
  fields: ["Customer", "Total", "Date"]
  sort: [{ "field": "Total", "direction": "desc" }]
  pageSize: 10
```

### Most Recent Activity

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_activities"
  fields: ["Name", "Status", "UpdatedAt"]
  sort: [{ "field": "UpdatedAt", "direction": "desc" }]
  pageSize: 5
```

### Records in a Specific Status

```
mcp__plugin_nocodb-ops_nocodb__queryRecords
  tableId: "tbl_tasks"
  where: "(Status,eq,Overdue)"
  fields: ["Title", "AssignedTo", "DueDate"]
  sort: [{ "field": "DueDate", "direction": "asc" }]
```

## Dashboard Pattern

A dashboard combines multiple calls to paint a complete picture. Run these calls together and present all results in one response.

**Step 1 -- Get totals and breakdown:**

```
mcp__plugin_nocodb-ops_nocodb__aggregate  (overall totals + filter groups by category)
```

**Step 2 -- Get record count:**

```
mcp__plugin_nocodb-ops_nocodb__countRecords  (total records, plus filtered counts for key segments)
```

**Step 3 -- Get recent and notable items:**

```
mcp__plugin_nocodb-ops_nocodb__queryRecords  (latest 5 records, sorted by date)
mcp__plugin_nocodb-ops_nocodb__queryRecords  (top 5 by value, sorted descending)
```

**Step 4 -- Present everything together** as a formatted summary:

- Overall metrics (total, average, count)
- Breakdown by segment (table format)
- Recent items list
- Top items list

## Best Practices

- **Use aggregate for numbers.** When the user asks "how much" or "how many," reach for `aggregate` first. It is faster and more accurate than fetching all records and counting manually.
- **Use queryRecords for detail.** When the user wants to see specific records, names, or lists, use `queryRecords` with field selection and sorting.
- **Use filter groups for segmentation.** Instead of making separate aggregate calls for each category, put all segments into one call using `filterGroups`. This is faster and keeps the results together. For plain counts per value, `groupByRecords` is shorter.
- **Select only needed fields.** When querying records for a report, specify the `fields` parameter to return only the columns that matter. This keeps the output clean and readable.
- **Combine calls for dashboards.** A good dashboard is 2-4 calls: one aggregate for the big numbers, one or two queries for detail lists, and optionally a count for a headline figure.
- **Format results for readability.** Always present report data in tables, bullet lists, or structured summaries. Raw tool output is hard to read.
- **Check the schema first.** Before building a report, call `mcp__plugin_nocodb-ops_nocodb__getTableSchema` to confirm field names, types, and available values. Wrong field names produce empty results, not errors.
