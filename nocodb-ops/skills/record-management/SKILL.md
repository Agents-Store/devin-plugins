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
---

# Record Management

All record operations require a `tableId`. Always resolve it first:

```
Step 0: mcp__nocodb__getTablesList  -->  get table IDs
Step 0b: mcp__nocodb__getTableSchema  -->  get exact field names and types
```

Never guess table IDs or field names. Always look them up.

---

## List Records

Use `mcp__nocodb__queryRecords` to search, filter, sort, and paginate.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table to query |
| `where` | No | Filter expression, e.g. `(Status,eq,Active)` |
| `fields[]` | No | List of field names to return (omit for all) |
| `sort[]` | No | Fields to sort by; prefix with `-` for descending |
| `page` | No | Page number (starts at 1) |
| `pageSize` | No | Records per page (default 25, max 2000) |

**Filter syntax:** `(FieldName,operator,value)` joined with `~and` or `~or`.

Examples:

```
# All active customers
where: "(Status,eq,Active)"

# High-priority items created this month
where: "(Priority,eq,High)~and(Created,gte,2026-04-01)"

# Search by name (partial match)
where: "(Name,like,%Smith%)"

# Multiple values
where: "(Category,in,Sales,Marketing,Support)"
```

**Sorting:**

```
# Newest first
sort: ["-Created"]

# By name A-Z, then by date newest first
sort: ["Name", "-Created"]
```

**Pagination:**

```
# First page, 50 per page
page: 1, pageSize: 50

# Next page
page: 2, pageSize: 50
```

Always set a reasonable `pageSize`. For large tables, fetch in pages rather than requesting everything at once.

---

## Get a Single Record

Use `mcp__nocodb__getRecord` when you know the exact record ID.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `recordId` | Yes | The specific record ID |
| `fields` | No | Limit which fields to return |

Use this after finding a record via `queryRecords`, or when you have the ID from another source.

---

## Create Records

Use `mcp__nocodb__createRecords` to add one or many records at once.

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

**Bulk create (up to 2000 per call):**

```
records: [
  { "fields": { "Name": "Alice", "Role": "Manager" } },
  { "fields": { "Name": "Bob", "Role": "Developer" } },
  { "fields": { "Name": "Carol", "Role": "Designer" } }
]
```

**Rules:**

- Maximum 2000 records per call. For larger imports, split into batches.
- Field names must match the schema exactly (case-sensitive).
- Omitted fields get their default values.
- The response includes the created record IDs -- save them if you need to reference the records later.

---

## Update Records

Use `mcp__nocodb__updateRecords` to change existing records.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `records` | Yes | Array of `{id, fields: {}}` objects |

**Single update:**

```
records: [
  {
    "id": "rec_abc123",
    "fields": { "Status": "Completed" }
  }
]
```

**Bulk update:**

```
records: [
  { "id": "rec_abc123", "fields": { "Status": "Completed" } },
  { "id": "rec_def456", "fields": { "Status": "Completed" } },
  { "id": "rec_ghi789", "fields": { "Status": "Cancelled" } }
]
```

**Rules:**

- Only send the fields you want to change. Omitted fields stay as they are.
- You must include the record `id` for each entry.
- Maximum 2000 records per call.
- Verify changes after updating by querying the affected records.

---

## Delete Records

Use `mcp__nocodb__deleteRecords` to permanently remove records.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `records` | Yes | Array of `{id}` objects |

```
records: [
  { "id": "rec_abc123" },
  { "id": "rec_def456" }
]
```

**Rules:**

- **Always confirm before bulk delete.** Deleted records cannot be recovered.
- Query the records first to verify you are deleting the right ones.
- Maximum 2000 records per call.
- For large deletions, fetch matching record IDs with `queryRecords`, review them, then pass to `deleteRecords`.

---

## Count Records

Use `mcp__nocodb__countRecords` to count without fetching data.

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `tableId` | Yes | The table |
| `where` | No | Filter expression |

```
# Total records in table
tableId: <table_id>

# Count active customers
tableId: <customers_table_id>
where: "(Status,eq,Active)"

# Count overdue tasks
tableId: <tasks_table_id>
where: "(Due Date,lt,2026-04-06)~and(Status,neq,Done)"
```

Use this before large operations to understand the scope (e.g., "how many records will this bulk update affect?").

---

## Common Workflows

### Import data

1. Call `getTableSchema` to confirm field names and types.
2. Prepare records as an array of `{fields: {}}` objects.
3. Split into batches of up to 2000.
4. Call `createRecords` for each batch.
5. Call `countRecords` to verify the total matches expectations.

### Search and update

1. Use `queryRecords` with a `where` filter to find matching records.
2. Review the results to confirm they are the right ones.
3. Build an update array with the record IDs and new field values.
4. Call `updateRecords` with the changes.
5. Query again to verify the updates took effect.

### Filtered batch update

Update all records matching a condition (e.g., mark all overdue tasks as "Escalated"):

1. Call `countRecords` with the filter to know the scope.
2. Call `queryRecords` with the same filter, paginating through all results.
3. Collect all record IDs from the results.
4. Call `updateRecords` in batches of up to 2000.
5. Call `countRecords` with a filter for the new value to confirm.

### Deduplicate records

1. Use `queryRecords` sorted by the field that might have duplicates.
2. Identify duplicates by comparing adjacent records.
3. Decide which record to keep (e.g., oldest, most complete).
4. Call `deleteRecords` to remove the extras.

---

## Best Practices

1. **Resolve table and field info first** -- call `getTablesList` and `getTableSchema` before any operation.
2. **Use bulk operations for imports** -- one call with 2000 records is much faster than 2000 single calls.
3. **Verify after writes** -- query or count after creating, updating, or deleting to confirm success.
4. **Filter on the server** -- use `where` instead of fetching everything and filtering manually.
5. **Paginate reads** -- never try to fetch an entire large table in one call.
6. **Confirm before deleting** -- always show the user what will be deleted and get approval.
7. **Send only changed fields** -- when updating, include only the fields that need to change.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| "Table not found" | Wrong or outdated `tableId` | Re-run `getTablesList` for current IDs |
| "Field not found" | Misspelled field name or wrong case | Run `getTableSchema` for exact names |
| "Record not found" | Invalid `recordId` or already deleted | Query first to confirm it exists |
| "Invalid filter" | Malformed `where` expression | Check parentheses: `(Field,op,value)` |
| "Too many records" | Batch exceeds 2000 limit | Split into smaller batches |
| "Validation failed" | Value does not match field type | Check schema for expected type (text, number, date, etc.) |
| "Read-only field" | Trying to write a computed or system field | Remove that field from your update payload |
