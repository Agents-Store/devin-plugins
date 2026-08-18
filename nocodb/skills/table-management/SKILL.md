---
name: table-management
description: Table CRUD operations — create, list, get, delete tables. This skill should be used when the user asks to create a table, list existing tables, or manage table structure.
---

# Table Management

This skill covers all table-level operations in NocoDB — creating, listing, getting details, and deleting tables.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_tables` | List all tables in the base |
| `create_table` | Create a new table with columns |
| `get_table` | Get table details and metadata |
| `delete_table` | Delete a table |

## Listing Tables

```
Tool: list_tables
Input: {}

Returns: Array of tables with id, name, and metadata.
```

Always call this first to:
- Check if a table already exists before creating
- Resolve table name to table_id for other operations

## Creating Tables

```
Tool: create_table
Input: {
  "name": "Contacts",
  "columns": [
    { "name": "Name", "type": "SingleLineText" },
    { "name": "Email", "type": "Email" },
    { "name": "Phone", "type": "PhoneNumber" },
    { "name": "Company", "type": "SingleLineText" },
    { "name": "Status", "type": "SingleSelect", "options": ["Lead", "Active", "Inactive"] }
  ]
}
```

**Column types available on create:**
SingleLineText, LongText, Number, Decimal, Currency, Percent, Email, URL, PhoneNumber, SingleSelect, MultiSelect, Checkbox, Date, DateTime, Duration, Rating, Attachment

**Note:** LinkToAnotherRecord, Lookup, Rollup, Formula columns must be added separately via `create_column` after both tables exist.

## Getting Table Details

```
Tool: get_table
Input: { "table_id": "tbl_abc123" }

Returns: Full table metadata including all columns, views, and configuration.
```

## Deleting Tables

```
Tool: delete_table
Input: { "table_id": "tbl_abc123" }
```

**Warning:** This permanently deletes the table and all its data. Always confirm with user first.

## Common Workflows

### Create Multiple Related Tables
```
1. list_tables() -> Check existing tables
2. create_table("Categories", columns) -> Reference table first
3. create_table("Products", columns) -> Main table
4. create_column(products_id, type=LinkToAnotherRecord, linked_table_id=categories_id) -> Add relation
```

### Verify Table Structure
```
1. list_tables() -> Get table IDs
2. get_table(table_id) -> See all columns, types, and configuration
```

## Best Practices

1. **Always check before creating** — use `list_tables` to avoid duplicates
2. **Use plural names** — "Contacts" not "Contact"
3. **Include a primary text field** — first column should be the display name
4. **Create reference tables first** — tables without dependencies come before tables with relations
5. **Don't include relation fields on creation** — add them separately after both tables exist
