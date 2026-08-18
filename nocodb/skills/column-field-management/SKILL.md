---
name: column-field-management
description: Column/field types, relations, lookups, rollups, formulas. This skill should be used when the user asks to add columns, configure field types, set up relations, lookups, rollups, or formulas.
---

# Column & Field Management

This skill covers column operations in NocoDB — creating fields of all types, setting up relations (Links), Lookups, Rollups, and Formulas.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_columns` | List all columns in a table |
| `create_column` | Create a new column |
| `update_column` | Update column configuration |
| `delete_column` | Delete a column |

## Listing Columns

```
Tool: list_columns
Input: { "table_id": "tbl_abc123" }

Returns: Array of columns with id, name, type, and configuration.
```

## Field Types Reference

### Basic Fields

| Type | Description | Example Input |
|------|-------------|---------------|
| SingleLineText | Short text | `{ "name": "Title", "type": "SingleLineText" }` |
| LongText | Multi-line text | `{ "name": "Description", "type": "LongText" }` |
| Number | Integer | `{ "name": "Quantity", "type": "Number" }` |
| Decimal | Float | `{ "name": "Score", "type": "Decimal" }` |
| Currency | Money | `{ "name": "Price", "type": "Currency" }` |
| Percent | Percentage | `{ "name": "Discount", "type": "Percent" }` |
| Email | Email address | `{ "name": "Email", "type": "Email" }` |
| URL | Web link | `{ "name": "Website", "type": "URL" }` |
| PhoneNumber | Phone | `{ "name": "Phone", "type": "PhoneNumber" }` |
| Checkbox | Boolean | `{ "name": "Active", "type": "Checkbox" }` |
| Date | Date | `{ "name": "Birthday", "type": "Date" }` |
| DateTime | Date + Time | `{ "name": "CreatedAt", "type": "DateTime" }` |
| Duration | Time span | `{ "name": "TimeSpent", "type": "Duration" }` |
| Rating | Star rating | `{ "name": "Rating", "type": "Rating", "max": 5 }` |
| Attachment | Files | `{ "name": "Files", "type": "Attachment" }` |

### Selection Fields

```
Tool: create_column
Input: {
  "table_id": "tbl_abc123",
  "name": "Status",
  "type": "SingleSelect",
  "options": ["New", "In Progress", "Done", "Archived"]
}
```

```
Tool: create_column
Input: {
  "table_id": "tbl_abc123",
  "name": "Tags",
  "type": "MultiSelect",
  "options": ["Urgent", "Feature", "Bug", "Documentation"]
}
```

### Relation Fields (LinkToAnotherRecord)

**Has Many (hm):**
```
Tool: create_column
Input: {
  "table_id": "tbl_contacts",
  "name": "Company",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "tbl_companies",
  "relation_type": "hm"
}
```

**Many to Many (mm):**
```
Tool: create_column
Input: {
  "table_id": "tbl_deals",
  "name": "Products",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "tbl_products",
  "relation_type": "mm"
}
```

### Lookup Fields

Show a field from a related table. Requires a LinkToAnotherRecord column.

```
Tool: create_column
Input: {
  "table_id": "tbl_deals",
  "name": "Contact Email",
  "type": "Lookup",
  "relation_column_id": "cl_company_link",
  "lookup_column_id": "cl_email"
}
```

### Rollup Fields

Aggregate values from related records. Requires a LinkToAnotherRecord column.

```
Tool: create_column
Input: {
  "table_id": "tbl_contacts",
  "name": "Total Deal Value",
  "type": "Rollup",
  "relation_column_id": "cl_deals_link",
  "rollup_column_id": "cl_amount",
  "rollup_function": "sum"
}
```

**Rollup functions:** sum, count, avg, min, max, count_distinct

### Formula Fields

```
Tool: create_column
Input: {
  "table_id": "tbl_deals",
  "name": "Deal Category",
  "type": "Formula",
  "formula": "IF({Amount} > 10000, 'Enterprise', 'SMB')"
}
```

**Formula Reference:**

| Pattern | Formula | Use Case |
|---------|---------|----------|
| Conditional | `IF({Amount} > 10000, "Enterprise", "SMB")` | Categorization |
| Multi-condition | `SWITCH({Status}, "Active", "🟢", "Inactive", "🔴", "⚪")` | Status icons |
| Display name | `CONCAT({First Name}, " ", {Last Name})` | Combine text |
| Substring | `LEFT({Code}, 3)` | Extract prefix |
| Right substring | `RIGHT({Phone}, 4)` | Extract last digits |
| Due date | `DATEADD({Created}, 30, 'days')` | Calculate future date |
| Duration | `DATETIME_DIFF({End Date}, {Start Date}, 'days')` | Days between |
| Day of week | `WEEKDAY({Date})` | Get weekday (0=Sun) |
| Percentage | `ROUND({Completed} / {Total} * 100, 1)` | Calc percentage |
| Rounding up | `CEILING({Price} * 1.1)` | Round up |
| Rounding down | `FLOOR({Score} / 10) * 10` | Round to nearest 10 |
| Null check | `IF({Email} = "", "Missing", {Email})` | Handle empty fields |
| Nested IF | `IF({Amount} > 10000, "High", IF({Amount} > 1000, "Medium", "Low"))` | Multi-level categorization |
| Text contains | `IF(FIND("urgent", LOWER({Title})) > 0, "Yes", "No")` | Search in text |
| Record age | `DATETIME_DIFF(NOW(), {Created}, 'days')` | Days since creation |

**Formula syntax:** Reference fields with `{field_name}`. String literals in `"quotes"` or `'quotes'`.

## Common Workflows

### Add Relation + Lookup + Rollup
```
1. list_tables() -> Get table IDs for both tables
2. list_columns(table_id) -> Check existing columns
3. create_column(type=LinkToAnotherRecord) -> Create relation
4. list_columns(linked_table_id) -> Get column IDs for lookup/rollup
5. create_column(type=Lookup) -> Show related field
6. create_column(type=Rollup) -> Aggregate related values
```

### Add Select Field with Options
```
1. list_columns(table_id) -> Check if field exists
2. create_column(type=SingleSelect, options=[...]) -> Create with options
```

### Add Formula Based on Existing Fields
```
1. list_columns(table_id) -> Verify referenced fields exist
2. create_column(type=Formula, formula="...") -> Create formula
```

## Important Rules

1. **Creation order matters:**
   - Basic fields → Relations → Lookups/Rollups → Formulas
   - Each type depends on the previous

2. **Use table_id, not table_name** — always resolve via list_tables

3. **Use column_id for Lookup/Rollup** — get IDs from list_columns

4. **Relation creates columns in BOTH tables** — a Link in table A auto-creates a reverse link in table B

5. **Formula field names are case-sensitive** — `{Amount}` not `{amount}`

## Best Practices

1. **Name columns clearly** — "Contact Email" (lookup) vs "Email" (native field)
2. **Set primary display first** — affects how linked records appear
3. **Use SingleSelect for statuses** — enables Kanban views
4. **Plan formulas on paper** — complex formulas are hard to debug
5. **Test Lookups/Rollups** — add sample data to verify they resolve correctly
