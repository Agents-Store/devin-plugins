---
name: mcp-patterns
description: |
  NocoDB MCP tools reference -- available tools, parameters, and usage patterns. Use when:
  - "what NocoDB tools are available?"
  - "how do I query records?"
  - "show me NocoDB MCP parameters"
  - "which tool do I use for..."
  - "NocoDB tool reference"
---

# NocoDB MCP Tools Reference

All tools use the `mcp__nocodb__` prefix. Every tool call goes through the NocoDB MCP server.

## Discovery Tools

Use these first to understand what data is available.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `getBaseInfo` | Get base name, ID, and metadata | None |
| `getTablesList` | List all tables you can access | None |
| `getTableSchema` | Get columns, types, and views for a table | `tableId` |

**Always start with `getTablesList`** to get table IDs. You need a `tableId` for almost every other tool.

## Read Tools

Retrieve data without changing anything.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `queryRecords` | Search and list records with filters, sorting, and pagination | `tableId`, `where`, `fields[]`, `sort[]`, `page`, `pageSize` |
| `getRecord` | Fetch one specific record by its ID | `tableId`, `recordId`, `fields` |
| `countRecords` | Count how many records match a filter | `tableId`, `where` |

## Write Tools

Create, change, or remove data.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `createRecords` | Add new records (single or bulk, up to 2000) | `tableId`, `records[{fields:{}}]` |
| `updateRecords` | Change existing records (send only changed fields) | `tableId`, `records[{id, fields:{}}]` |
| `deleteRecords` | Remove records permanently | `tableId`, `records[{id}]` |

## Analytics Tools

Run calculations across your data.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `aggregate` | Sum, count, average, min, max, median, std_dev, and more | `tableId`, `aggregations[{field, type}]`, `filterGroups[{alias, where}]` |

## File Tools

Work with file attachments stored in records.

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `readAttachment` | Read files attached to a record | `files[]` |

---

## Filter Syntax

Filters use the format: `(field,operator,value)`

**Operators:**

| Category | Operators |
|----------|----------|
| Comparison | `eq`, `neq`, `gt`, `lt`, `gte`, `lte` |
| Range | `btw`, `nbtw` |
| Text | `like`, `nlike` |
| List | `in`, `allof`, `anyof`, `nallof`, `nanyof` |
| Empty checks | `blank`, `notblank`, `null`, `notnull`, `empty`, `notempty` |
| Checkbox | `checked`, `notchecked` |

**Combine filters** with `~and`, `~or`, `~not`:

```
(Status,eq,Active)~and(Priority,eq,High)
```

---

## Common Patterns

### Pattern 1 -- List with filter and sort

Find all active orders sorted by date, showing only key fields:

```
Tool: mcp__nocodb__queryRecords
Params:
  tableId: <orders_table_id>
  where: "(Status,eq,Active)"
  fields: ["Order Number", "Customer", "Total", "Date"]
  sort: ["-Date"]
  pageSize: 25
```

Prefix a field name with `-` to sort descending.

### Pattern 2 -- Create and verify

Add a new record, then confirm it was saved:

```
Step 1 - Tool: mcp__nocodb__createRecords
Params:
  tableId: <contacts_table_id>
  records: [{ "fields": { "Name": "Jane Smith", "Email": "jane@example.com" } }]

Step 2 - Tool: mcp__nocodb__queryRecords
Params:
  tableId: <contacts_table_id>
  where: "(Email,eq,jane@example.com)"
```

### Pattern 3 -- Aggregate report

Get total revenue and order count, split by status:

```
Tool: mcp__nocodb__aggregate
Params:
  tableId: <orders_table_id>
  aggregations: [
    { "field": "Total", "type": "sum" },
    { "field": "Id", "type": "count" }
  ]
  filterGroups: [
    { "alias": "Active", "where": "(Status,eq,Active)" },
    { "alias": "Completed", "where": "(Status,eq,Completed)" }
  ]
```

---

## Best Practices

1. **Resolve table IDs first** -- always call `getTablesList` before operating on data. Never guess IDs.
2. **Check the schema** -- call `getTableSchema` to confirm exact field names and types before querying.
3. **Use pagination** -- set `pageSize` (default is 25, max is 2000) and use `page` for large datasets.
4. **Filter on the server** -- apply `where` filters instead of fetching all records and filtering locally.
5. **Request only needed fields** -- use `fields[]` to limit returned data and keep responses fast.
6. **Bulk operations** -- prefer batch calls (up to 2000 records) over looping one-by-one.

## Error Handling

| Error | Meaning | What to Do |
|-------|---------|-----------|
| "Table not found" | Wrong `tableId` | Re-run `getTablesList` and use the correct ID |
| "Field not found" | Typo or wrong field name | Run `getTableSchema` to see exact field names |
| "Invalid filter" | Bad `where` syntax | Check parentheses and operator spelling |
| "Record not found" | Wrong `recordId` | Query first to confirm the record exists |
| "Too many records" | Batch exceeds 2000 limit | Split into smaller batches |
| 401 / 403 | Auth or permission issue | See the **setup** skill for troubleshooting |
