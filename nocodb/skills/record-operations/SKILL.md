---
name: record-operations
description: Record CRUD, filtering, sorting, bulk operations. This skill should be used when the user asks to create, read, update, or delete records, filter or search data, bulk import, or aggregate values.
---

# Record Operations

This skill covers all record-level operations in NocoDB — CRUD, filtering, sorting, pagination, and bulk imports.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_records` | List records with filtering, sorting, and pagination |
| `create_record` | Create a single record |
| `bulk_create_records` | Create multiple records at once (up to 100) |
| `update_record` | Update an existing record |
| `delete_record` | Delete a record |
| `search_records` | Full-text search across record fields |
| `bulk_update_records` | Update multiple records at once |
| `bulk_delete_records` | Delete multiple records at once |
| `aggregate` | Compute sum, count, avg, min, max on fields |
| `group_by` | Group records by a field with counts |
| `export_table_data` | Export table data in CSV or JSON format |

## Listing Records

### Basic List
```
Tool: list_records
Input: {
  "table_id": "tbl_abc123",
  "limit": 25,
  "offset": 0
}
```

### With Filters
```
Tool: list_records
Input: {
  "table_id": "tbl_abc123",
  "where": "(Status,eq,Active)~and(Amount,gt,1000)",
  "sort": "-CreatedAt",
  "limit": 50,
  "offset": 0,
  "fields": ["Name", "Email", "Status", "Amount"]
}
```

### Filter Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| eq | Equal | `(Status,eq,Active)` |
| neq | Not equal | `(Status,neq,Archived)` |
| gt | Greater than | `(Amount,gt,1000)` |
| lt | Less than | `(Amount,lt,100)` |
| gte | Greater or equal | `(Price,gte,50)` |
| lte | Less or equal | `(Rating,lte,3)` |
| like | Contains | `(Name,like,John)` |
| nlike | Not contains | `(Name,nlike,Test)` |
| is | Is null | `(Email,is,null)` |
| isnot | Is not null | `(Email,isnot,null)` |

### Combining Filters
- AND: `(Status,eq,Active)~and(Amount,gt,1000)`
- OR: `(Status,eq,Active)~or(Status,eq,Pending)`
- Complex: `(Status,eq,Active)~and((Amount,gt,1000)~or(Priority,eq,High))`

### Sorting
- Ascending: `sort=Name`
- Descending: `sort=-Name`
- Multiple: `sort=-Priority,Name`

### Pagination
- `limit`: Max records per request (max 100)
- `offset`: Skip N records
- Use offset for paginating through large datasets

## Creating Records

### Single Record
```
Tool: create_record
Input: {
  "table_id": "tbl_abc123",
  "data": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Status": "Active",
    "Amount": 5000
  }
}
```

### Bulk Create (up to 100)
```
Tool: bulk_create_records
Input: {
  "table_id": "tbl_abc123",
  "records": [
    { "Name": "Alice", "Email": "alice@example.com", "Status": "Active" },
    { "Name": "Bob", "Email": "bob@example.com", "Status": "Lead" },
    { "Name": "Carol", "Email": "carol@example.com", "Status": "Active" }
  ]
}
```

## Updating Records

```
Tool: update_record
Input: {
  "table_id": "tbl_abc123",
  "record_id": "rec_xyz789",
  "data": {
    "Status": "Closed",
    "Amount": 7500
  }
}
```

Only send fields you want to change — other fields remain unchanged.

## Deleting Records

```
Tool: delete_record
Input: {
  "table_id": "tbl_abc123",
  "record_id": "rec_xyz789"
}
```

## Common Workflows

### Import Data
```
1. list_tables() -> Find target table
2. list_columns(table_id) -> Verify column structure matches data
3. bulk_create_records(table_id, records) -> Import batch (max 100)
4. Repeat step 3 for remaining batches
5. list_records(table_id, limit=5) -> Verify import
```

### Search and Update
```
1. list_records(table_id, where="(Name,like,John)") -> Find matching records
2. update_record(table_id, record_id, data) -> Update each match
```

### Filtered Report
```
1. list_records(table_id, where="(Status,eq,Active)~and(Amount,gt,5000)", sort="-Amount") -> Get filtered data
2. Present results in a formatted table
```

## Search Records

Full-text search across all fields in a table.

```
Tool: search_records
Input: {
  "table_id": "tbl_abc123",
  "query": "john"
}

Returns: Records matching the search query across all text fields.
```

## Bulk Update Records

Update multiple records at once.

```
Tool: bulk_update_records
Input: {
  "table_id": "tbl_abc123",
  "records": [
    { "id": "rec_1", "Status": "Closed" },
    { "id": "rec_2", "Status": "Closed" },
    { "id": "rec_3", "Status": "Closed" }
  ]
}
```

## Bulk Delete Records

Delete multiple records at once.

```
Tool: bulk_delete_records
Input: {
  "table_id": "tbl_abc123",
  "record_ids": ["rec_1", "rec_2", "rec_3"]
}
```

## Advanced Workflows

### Search and Bulk Update
```
1. search_records(table_id, query="overdue") → Find matching records
2. bulk_update_records(table_id, records=[{id, Status: "Overdue"} ...]) → Update all matches
3. list_records(table_id, where="(Status,eq,Overdue)") → Verify updates
```

### Aggregate Data
```
Tool: aggregate
Input: {
  "table_id": "tbl_abc123",
  "column": "Amount",
  "function": "sum"
}

Functions: sum, count, avg, min, max
```

### Group By
```
Tool: group_by
Input: {
  "table_id": "tbl_abc123",
  "column": "Status"
}

Returns: Records grouped by the specified column with counts.
```

### Data Export
```
Tool: export_table_data
Input: {
  "table_id": "tbl_abc123",
  "format": "csv"
}
```

## Error Handling Patterns

### Common Failure Scenarios
- **Table/record not found** → verify table_id exists via `list_tables` first
- **Bulk operation partial failure** → check response for failed record IDs, retry individually
- **Invalid field value** → validate field type before create/update (number for Number fields, valid option for SingleSelect)
- **Relation target missing** → ensure referenced record exists before linking
- **Duplicate record** → use `search_records` to check for duplicates before creating

### Defensive Workflow
1. Always resolve table name → ID via `list_tables` before any operation
2. For bulk operations: batch in groups of 100, check response for failures
3. For updates: read record first to verify it exists and check current values
4. For deletes: list records with filters first to confirm what will be deleted
5. After writes: verify with `list_records` to confirm changes

## Best Practices

1. **Always resolve table_id first** — use `list_tables` to get IDs
2. **Use bulk for imports** — `bulk_create_records` is much faster than individual creates
3. **Use bulk for mass updates** — `bulk_update_records` instead of individual update_record
4. **Limit results** — always set reasonable limits, max 100 per request
5. **Filter on server side** — use `where` instead of fetching all and filtering locally
6. **Check column types** — ensure data matches column types (number for Number fields, etc.)
7. **Use fields parameter** — request only needed fields for better performance
8. **Search before creating** — use `search_records` to check for duplicates
9. **Verify before bulk delete** — always list records first to confirm what will be deleted
