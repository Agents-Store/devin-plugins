---
name: record-management
description: |
  Create, read, update, and delete NocoDB records. Use when:
  - "add a new record"
  - "create entries in NocoDB"
  - "update a record"
  - "delete records"
  - "bulk import data"
  - "search and edit records"
  - "how many records match..."
  - "restore deleted records"
---

# Record Management

All record operations require a `tableId`. Always resolve it first:

```
Step 0: mcp__plugin_nocodb-ops_nocodb__getTablesList  -->  get table IDs
Step 0b: mcp__plugin_nocodb-ops_nocodb__getTableSchema  -->  get exact field names and types
```

Never guess table IDs or field names. Always look them up.

---

## List Records

Use `mcp__plugin_nocodb-ops_nocodb__queryRecords` to search, filter, sort, and paginate.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table to query |
| `filter` | No | Structured filter (preferred): `{ "field": "Status", "operator": "eq", "value": "Active" }` or a `{ "group_operator": "AND"\|"OR", "filters": [...] }` group |
| `where` | No | Filter string, e.g. `(Status,eq,Active)` -- fallback; pass `filter` **or** `where`, not both |
| `fields` | No | Array of field names to return (omit for all) |
| `sort` | No | Array of `{ "field", "direction" }` objects, applied in order |
| `page` | No | Page number (starts at 1) |
| `pageSize` | No | Records per page (default 50, max 200) |

**Filter syntax:** the structured `filter` takes `{field, operator, value}` (add `sub_operator` on date fields); the `where` string is `(FieldName,operator,value)` joined with `~and` or `~or`.

Examples:

```
# All active customers
filter: { "field": "Status", "operator": "eq", "value": "Active" }

# High-priority items created since 1 April 2026 (date fields need sub_operator exactDate)
filter: { "group_operator": "AND", "filters": [
  { "field": "Priority", "operator": "eq", "value": "High" },
  { "field": "Created", "operator": "gte", "sub_operator": "exactDate", "value": "2026-04-01" } ] }
where:  "(Priority,eq,High)~and(Created,gte,exactDate,2026-04-01)"      # same, as a string

# Search by name (partial match)
where: "(Name,like,%Smith%)"

# Multiple values
filter: { "field": "Category", "operator": "in", "value": ["Sales", "Marketing", "Support"] }
```

**Sorting** -- `sort` is an array of objects; a string or `["-Created"]` is rejected by the server:

```
# Newest first
sort: [{ "field": "Created", "direction": "desc" }]

# By name A-Z, then by date newest first
sort: [{ "field": "Name", "direction": "asc" }, { "field": "Created", "direction": "desc" }]
```

**Pagination:**

```
# First page, 50 per page
page: 1, pageSize: 50

# Next page
page: 2, pageSize: 50
```

The default `pageSize` is 50 and the cap is 200; the response reports the `page_size` actually applied (a deployment can cap it lower). For large tables, fetch in pages rather than requesting everything at once.

---

## Get a Single Record

Use `mcp__plugin_nocodb-ops_nocodb__getRecord` when you know the exact record ID.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `recordId` | Yes | The specific record ID |
| `fields` | No | Limit which fields to return |

Use this after finding a record via `queryRecords`, or when you have the ID from another source.

---

## Create Records

Use `mcp__plugin_nocodb-ops_nocodb__createRecords` to add one or many records at once.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The target table |
| `records` | Yes | Array of `{fields: {}}` objects |

**Single record:**

```
records: [
  {
    "fields": {
      "Name": "Acme Corp",
      "Email": "info@acme.com",
      "Status": "Active"
    }
  }
]
```

**Bulk create (up to 100 per call):**

```
records: [
  { "fields": { "Name": "Alice", "Role": "Manager" } },
  { "fields": { "Name": "Bob", "Role": "Developer" } },
  { "fields": { "Name": "Carol", "Role": "Designer" } }
]
```

**Rules:**

- Maximum **100 records per call**. A longer array is rejected outright -- the whole call fails, nothing is written -- so split larger imports into batches of 100 or fewer (or use `importCsv`, see **import-export**).
- Field names must match the schema exactly (use the titles from `getTableSchema`).
- Omitted fields get their default values.
- The response includes the created record IDs -- save them if you need to reference the records later.

---

## Update Records

Use `mcp__plugin_nocodb-ops_nocodb__updateRecords` to change existing records.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `records` | Yes | Array of `{id, fields: {}}` objects |

**Single update:**

```
records: [
  {
    "id": 101,
    "fields": { "Status": "Completed" }
  }
]
```

**Bulk update:**

```
records: [
  { "id": 101, "fields": { "Status": "Completed" } },
  { "id": 102, "fields": { "Status": "Completed" } },
  { "id": 103, "fields": { "Status": "Cancelled" } }
]
```

**Rules:**

- Only send the fields you want to change. Omitted fields stay as they are.
- You must include the record `id` for each entry.
- Maximum **100 records per call** -- a longer array is rejected outright.
- A link field is **replaced**, not appended to: pass the complete list you want, `[]` to clear it. To add or remove single links use `linkRecords` / `unlinkRecords`.
- To set the same values on every record matching a condition (no 100 cap), use `updateRecordsByCondition` -- see "Filtered batch update" below.
- Verify changes after updating by querying the affected records.

---

## Delete Records

Use `mcp__plugin_nocodb-ops_nocodb__deleteRecords` to remove records.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `records` | Yes | Array of `{id}` objects |

```
records: [
  { "id": 101 },
  { "id": 102 }
]
```

**Rules:**

- **Always confirm before bulk delete**, and show the user the records first.
- Query the records first to verify you are deleting the right ones.
- Maximum **100 records per call**.
- For large deletions, fetch matching record IDs with `queryRecords`, review them, then pass them to `deleteRecords` in batches of 100 or fewer.

**Can a delete be undone?** It depends on where the table lives:

- **NocoDB-managed table:** deleted rows go to the base trash and can be restored until the retention window ends. On Cloud / licensed servers, `listTools` category `trash` offers `listTrash`, `restoreRecords` (inverse of `deleteRecords`, by row id) and `restoreFromTrash`. A restore can collide with the table as it stands now (a unique value taken since, a linked row gone); without `force` / `partial` the call refuses and names the conflicts. After the window the entry is purged for good.
- **Table on an external source** (for example a connected database): the delete is **permanent**, and `restoreRecords` refuses.
- **Community Edition:** the MCP server has no trash tools -- treat every delete as permanent from the agent's side.

Tell the user which case applies before they approve a bulk delete.

---

## Count Records

Use `mcp__plugin_nocodb-ops_nocodb__countRecords` to count without fetching data.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `filter` or `where` | No | Filter (pass one of the two) |

```
# Total records in table
tableId: <table_id>

# Count active customers
tableId: <customers_table_id>
filter: { "field": "Status", "operator": "eq", "value": "Active" }

# Count overdue tasks (before today)
tableId: <tasks_table_id>
where: "(Due Date,lt,today)~and(Status,neq,Done)"

# Count tasks due on or after a calendar date
tableId: <tasks_table_id>
filter: { "field": "Due Date", "operator": "gte", "sub_operator": "exactDate", "value": "2026-04-06" }
```

Use this before large operations to understand the scope (e.g., "how many records will this bulk update affect?").

---

## Common Workflows

### Import data

1. Call `getTableSchema` to confirm field names and types.
2. Prepare records as an array of `{fields: {}}` objects.
3. Split into batches of up to 100.
4. Call `createRecords` for each batch.
5. Call `countRecords` to verify the total matches expectations.

For a records-already-keyed import (an external ID or email identifies each row), use `upsertRecords` through `listTools` / `callTool` instead -- see **mcp-patterns**.

### Search and update

1. Use `queryRecords` with a `filter` (or `where`) to find matching records.
2. Review the results to confirm they are the right ones.
3. Build an update array with the record IDs and new field values.
4. Call `updateRecords` with the changes.
5. Query again to verify the updates took effect.

### Filtered batch update

Update all records matching a condition (e.g., mark all overdue tasks as "Escalated"):

1. Call `countRecords` with the filter to know the scope, and show the number to the user.
2. **Cloud / licensed:** call `updateRecordsByCondition` through `callTool` (category `records`) with the same `filter` and the `fields` to set. It is not capped at 100, the condition is required, and it answers with a count only.
3. **Community Edition or per-record values:** call `queryRecords` with the same filter, paginate through all results, collect the record IDs, then call `updateRecords` in batches of up to 100.
4. Call `countRecords` with a filter for the new value to confirm.

### Deduplicate records

1. Use `queryRecords` sorted by the field that might have duplicates.
2. Identify duplicates by comparing adjacent records.
3. Decide which record to keep (e.g., oldest, most complete).
4. Call `deleteRecords` to remove the extras.

---

## Best Practices

1. **Resolve table and field info first** -- call `getTablesList` and `getTableSchema` before any operation.
2. **Use bulk operations for imports** -- one call with 100 records is much faster than 100 single calls (and 100 is the ceiling).
3. **Verify after writes** -- query or count after creating, updating, or deleting to confirm success.
4. **Filter on the server** -- use `filter` (or `where`) instead of fetching everything and filtering manually.
5. **Paginate reads** -- never try to fetch an entire large table in one call.
6. **Confirm before deleting** -- always show the user what will be deleted and get approval.
7. **Send only changed fields** -- when updating, include only the fields that need to change.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| "Table not found" | Wrong or outdated `tableId` | Re-run `getTablesList` for current IDs |
| "Field not found" / `Column alias '<name>' not found` | Misspelled field name or wrong case in a `where` string | Run `getTableSchema` for exact names |
| "Record not found" | Invalid `recordId` or already deleted | Query first to confirm it exists |
| "Invalid filter" | Malformed `where` expression | Check parentheses: `(Field,op,value)`, or use the structured `filter` |
| `'<date>' is not supported` | Date compared without a sub-operator | `(Field,gte,exactDate,2026-04-01)` / `sub_operator: "exactDate"` |
| Input validation error on `records` | More than 100 records in one call | Split into batches of 100 or fewer |
| "Validation failed" | Value does not match field type | Check schema for expected type (text, number, date, etc.) |
| "Read-only field" | Trying to write a computed or system field | Remove that field from your update payload |
