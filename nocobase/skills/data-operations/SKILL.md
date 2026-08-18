---
name: data-operations
description: Data CRUD operations — list, create, update, delete records. This skill should be used when the user asks to add records, query or filter data, update fields, delete entries, or bulk create records.
---

# Data Operations

Guide for managing data in NocoBase collections — list, create, update, delete records.

## Tools

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `data_list` | List records from a collection | collection, filter, sort, limit, offset |
| `data_create` | Create a new record | collection, data (field values) |
| `data_update` | Update an existing record | collection, filter/id, data (field values) |
| `data_delete` | Delete a record | collection, filter/id |
| `collection_get` | Get collection schema (for field reference) | collection name |

## Workflows

### Create a Single Record

```
Step 1: collection_get → get field names and types for the target collection
Step 2: data_create → create record with field values
```

Example:
```
collection_get("contacts")
  → fields: name (string), email (email), status (select), company (belongsTo)

data_create("contacts", {
  name: "John Doe",
  email: "john@example.com",
  status: "Active"
})
  → { id: 1, name: "John Doe", ... }
```

### Bulk Create Records

```
Step 1: collection_get → understand field schema
Step 2: data_create → repeat for each record
Step 3: data_list → verify all records were created
```

### List and Filter Records

```
Step 1: data_list → list records with optional filter
```

Common filter patterns:
```
data_list("orders", { filter: { status: "Draft" } })
data_list("contacts", { filter: { createdAt: { $gte: "2024-01-01" } } })
data_list("products", { sort: ["-price"], limit: 10 })
```

### Update a Record

```
Step 1: data_list → find the record to update (get its ID)
Step 2: data_update → update specific fields
Step 3: data_list → verify the update
```

Example:
```
data_list("orders", { filter: { id: 42 } })
  → { id: 42, status: "Draft", total: 1500 }

data_update("orders", { filter: { id: 42 }, data: { status: "Approved" } })
  → { id: 42, status: "Approved", total: 1500 }
```

### Delete a Record

```
Step 1: data_list → find and confirm the record to delete
Step 2: data_delete → delete by ID
Step 3: data_list → verify deletion
```

### Search and Update Multiple Records

```
Step 1: data_list → search for records matching criteria
Step 2: For each record: data_update → apply changes
Step 3: data_list → verify all updates
```

Example — mark overdue orders:
```
data_list("orders", { filter: { dueDate: { $lt: "2024-01-01" }, status: "Pending" } })
  → [{ id: 10 }, { id: 15 }, { id: 22 }]

data_update("orders", { filter: { id: 10 }, data: { status: "Overdue" } })
data_update("orders", { filter: { id: 15 }, data: { status: "Overdue" } })
data_update("orders", { filter: { id: 22 }, data: { status: "Overdue" } })
```

## Error Handling Patterns

### Common Failure Scenarios
- **Collection not found** → verify collection exists via `collection_list` first
- **Invalid field name** → use `collection_get` to check valid field names before writes
- **Data type mismatch** → ensure values match field types (string for text, number for integer)
- **Relation target missing** → for belongsTo fields, verify the related record's ID exists
- **Permission denied** → check if current user has write access to the collection

### Defensive Workflow
1. Always check collection exists via `collection_list` before operations
2. Get collection schema via `collection_get` to validate field names and types
3. For bulk creates: create records one by one and verify each, or batch and check results
4. After writes: verify with `data_list` and a filter on the created/updated record

## Best Practices

1. **Always check schema first** — use `collection_get` before creating/updating to know valid field names
2. **Filter before deleting** — use `data_list` to confirm what will be deleted
3. **Verify after writes** — use `data_list` to confirm creates/updates succeeded
4. **Use specific filters** — filter by ID when possible for precision
5. **Respect field types** — use correct value types (string, number, date format)
6. **Handle relations** — for belongsTo fields, provide the related record's ID
