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

NocoDB tables can have multiple views. To see what views already exist on a table, call `mcp__nocodb__getTableSchema` with the `tableId`. The response includes a list of views with their names and types.

```
mcp__nocodb__getTableSchema  tableId: "tbl_abc123"
```

The schema response contains a `views` section listing every view configured on that table. Each view has a name, type, and ID.

## View Types

NocoDB supports five view types. You cannot create or modify views through the MCP tools, but understanding them helps when discussing data with business users.

| View Type | Purpose | Best For |
|-----------|---------|----------|
| **Grid** | Spreadsheet-style rows and columns | General browsing, editing, bulk updates |
| **Kanban** | Cards grouped by a single-select field | Tracking status, pipeline stages, workflows |
| **Gallery** | Card layout showing images and key fields | Product catalogs, team directories, portfolios |
| **Form** | Input form for adding new records | Data collection, intake requests, surveys |
| **Calendar** | Date-based timeline display | Scheduling, deadlines, event planning |

When a user asks about a kanban board or calendar view, explain what the view does and note that creating or configuring views is done in the NocoDB web interface.

## Building Reports with Aggregate

The `mcp__nocodb__aggregate` tool is the primary way to build numeric reports. It computes calculations across an entire table or within filtered segments.

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

### Basic Aggregation

Calculate a single number across the whole table:

```
mcp__nocodb__aggregate
  tableId: "tbl_abc123"
  aggregations: [
    { "field": "Amount", "type": "sum" },
    { "field": "Amount", "type": "avg" },
    { "field": "Amount", "type": "count" }
  ]
```

This returns the total amount, average amount, and record count for the entire table.

### Segmented Reports with Filter Groups

Filter groups let you break down numbers by category. Each filter group has an alias (the label) and a where clause (the filter).

```
mcp__nocodb__aggregate
  tableId: "tbl_abc123"
  aggregations: [
    { "field": "Revenue", "type": "sum" },
    { "field": "Revenue", "type": "count" }
  ]
  filterGroups: [
    { "alias": "North", "where": "(Region,eq,North)" },
    { "alias": "South", "where": "(Region,eq,South)" },
    { "alias": "East", "where": "(Region,eq,East)" },
    { "alias": "West", "where": "(Region,eq,West)" }
  ]
```

This returns sum and count for each region separately -- one result per filter group.

## Report Examples

### Sales Summary by Region

```
mcp__nocodb__aggregate
  tableId: "tbl_orders"
  aggregations: [
    { "field": "Total", "type": "sum" },
    { "field": "Total", "type": "avg" },
    { "field": "Total", "type": "count" }
  ]
  filterGroups: [
    { "alias": "North America", "where": "(Region,eq,North America)" },
    { "alias": "Europe", "where": "(Region,eq,Europe)" },
    { "alias": "Asia", "where": "(Region,eq,Asia)" }
  ]
```

Present the results as a formatted table with columns for Region, Total Sales, Average Order, and Order Count.

### Monthly Active Records

Use date filters in filter groups to segment by time period:

```
mcp__nocodb__aggregate
  tableId: "tbl_activities"
  aggregations: [
    { "field": "Id", "type": "count" }
  ]
  filterGroups: [
    { "alias": "This Month", "where": "(CreatedAt,isWithin,thisMonth)" },
    { "alias": "Last Month", "where": "(CreatedAt,isWithin,pastMonth)" },
    { "alias": "Past Week", "where": "(CreatedAt,isWithin,pastWeek)" }
  ]
```

### Inventory Counts by Category

```
mcp__nocodb__aggregate
  tableId: "tbl_inventory"
  aggregations: [
    { "field": "Quantity", "type": "sum" },
    { "field": "Quantity", "type": "min" },
    { "field": "Quantity", "type": "max" }
  ]
  filterGroups: [
    { "alias": "Electronics", "where": "(Category,eq,Electronics)" },
    { "alias": "Clothing", "where": "(Category,eq,Clothing)" },
    { "alias": "Food", "where": "(Category,eq,Food)" }
  ]
```

## Quick Data Summaries with Query

When you need the actual records behind a number (not just aggregates), use `mcp__nocodb__queryRecords` with sorting and field selection.

### Top 10 Highest-Value Orders

```
mcp__nocodb__queryRecords
  tableId: "tbl_orders"
  fields: ["Customer", "Total", "Date"]
  sort: [{ "field": "Total", "direction": "desc" }]
  pageSize: 10
```

### Most Recent Activity

```
mcp__nocodb__queryRecords
  tableId: "tbl_activities"
  fields: ["Name", "Status", "UpdatedAt"]
  sort: [{ "field": "UpdatedAt", "direction": "desc" }]
  pageSize: 5
```

### Records in a Specific Status

```
mcp__nocodb__queryRecords
  tableId: "tbl_tasks"
  where: "(Status,eq,Overdue)"
  fields: ["Title", "AssignedTo", "DueDate"]
  sort: [{ "field": "DueDate", "direction": "asc" }]
```

## Dashboard Pattern

A dashboard combines multiple calls to paint a complete picture. Run these calls together and present all results in one response.

**Step 1 -- Get totals and breakdown:**

```
mcp__nocodb__aggregate  (overall totals + filter groups by category)
```

**Step 2 -- Get record count:**

```
mcp__nocodb__countRecords  (total records, plus filtered counts for key segments)
```

**Step 3 -- Get recent and notable items:**

```
mcp__nocodb__queryRecords  (latest 5 records, sorted by date)
mcp__nocodb__queryRecords  (top 5 by value, sorted descending)
```

**Step 4 -- Present everything together** as a formatted summary:

- Overall metrics (total, average, count)
- Breakdown by segment (table format)
- Recent items list
- Top items list

## Best Practices

- **Use aggregate for numbers.** When the user asks "how much" or "how many," reach for `aggregate` first. It is faster and more accurate than fetching all records and counting manually.
- **Use queryRecords for detail.** When the user wants to see specific records, names, or lists, use `queryRecords` with field selection and sorting.
- **Use filter groups for segmentation.** Instead of making separate aggregate calls for each category, put all segments into one call using `filterGroups`. This is faster and keeps the results together.
- **Select only needed fields.** When querying records for a report, specify the `fields` parameter to return only the columns that matter. This keeps the output clean and readable.
- **Combine calls for dashboards.** A good dashboard is 2-4 calls: one aggregate for the big numbers, one or two queries for detail lists, and optionally a count for a headline figure.
- **Format results for readability.** Always present report data in tables, bullet lists, or structured summaries. Raw tool output is hard to read.
- **Check the schema first.** Before building a report, call `mcp__nocodb__getTableSchema` to confirm field names, types, and available values. Wrong field names produce empty results, not errors.
