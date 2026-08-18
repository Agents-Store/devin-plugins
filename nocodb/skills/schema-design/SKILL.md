---
name: schema-design
description: Schema design best practices — entity modeling, relation patterns, creation order, formulas, views. This skill should be used when the user asks to design a database schema, plan tables and relationships, or build CRM/ERP/project databases.
---

# NocoDB Schema Design

Expert guidance on designing and building complex NocoDB schemas — data modeling, relations, rollups, formulas, views, and forms.

## Design Principles

Before creating any table:
1. **Identify entities and relationships** — think ERD (Entity Relationship Diagram)
2. **Define primary display field** for each table — set BEFORE creating relations
3. **Plan Lookup and Rollup fields** in advance — they depend on relations existing first
4. **Design views** per user role or workflow

## Creation Order (Critical)

Dependencies must exist before dependent fields. Follow this strict order:

```
Step 1: Reference tables (no dependencies)
  └── Statuses, Categories, Tags, Priorities
  └── Use SingleSelect columns for fixed option lists

Step 2: Main entity tables
  └── Contacts, Companies, Deals, Products, Tasks
  └── Include basic fields: text, number, date, select

Step 3: Relations (LinkToAnotherRecord)
  └── Both tables must exist before linking
  └── Always use table_id, never table_name
  └── Types: hm (has many), mm (many to many)

Step 4: Lookup fields
  └── Relation column must exist first
  └── Shows a specific field from the related table
  └── Example: show Contact.Email inside a Deal record

Step 5: Rollup fields
  └── Relation column must exist first
  └── Aggregates: sum, count, avg, min, max
  └── Example: SUM of Deal.Amount in Contact record

Step 6: Formula fields
  └── All referenced fields must exist
  └── Calculations, conditionals, string manipulation

Step 7: Views
  └── All fields should be in place
  └── Grid, Kanban, Gallery, Form, Calendar
  └── Configure filters, sorts, field visibility per view
```

## Workflow: Build a Schema

```
1. list_tables() -> Check what already exists
2. create_table(reference_tables) -> Statuses, Categories first
3. create_table(main_tables) -> Contacts, Deals, etc.
4. create_column(type=LinkToAnotherRecord) -> Relations between tables
5. create_column(type=Lookup) -> Show fields from related tables
6. create_column(type=Rollup) -> Aggregate related data
7. create_column(type=Formula) -> Calculated fields
8. create_view(type=Grid/Kanban/Form) -> Views for each workflow
9. list_tables() + list_columns() -> Verify structure
```

## Relation Patterns

### One-to-Many (hm)
One parent, many children. Create Link in the child table.

```
Example: Company has many Contacts
Tool: create_column
Input: {
  "table_id": "<contacts_table_id>",
  "name": "Company",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "<companies_table_id>"
}
```

### Many-to-Many (mm)
Both sides have many. NocoDB auto-creates a junction table.

```
Example: Deals have many Products, Products belong to many Deals
Tool: create_column
Input: {
  "table_id": "<deals_table_id>",
  "name": "Products",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "<products_table_id>",
  "relation_type": "mm"
}
```

### Lookup + Rollup After Relation
```
After creating Deal → Contact relation:

Lookup — show Contact.Email in Deal:
create_column(table_id=deals, type=Lookup, relation_column_id=<link_col>, lookup_column_id=<email_col>)

Rollup — show SUM of Deal.Amount in Contact:
create_column(table_id=contacts, type=Rollup, relation_column_id=<link_col>, rollup_column_id=<amount_col>, rollup_function="sum")
```

## Formula Patterns

| Pattern | Formula | Use Case |
|---------|---------|----------|
| Conditional | `IF({Amount} > 10000, "Enterprise", "SMB")` | Categorize records |
| Display name | `CONCAT({First Name}, " ", {Last Name})` | Combined text |
| Due date | `DATEADD({Created}, 30, 'days')` | Auto deadline |
| Days elapsed | `DATETIME_DIFF(NOW(), {Created}, 'days')` | Age tracking |
| Progress | `IF({Status} = "Done", 1, 0)` | Completion flag |
| Percentage | `ROUND({Completed} / {Total} * 100, 1)` | Progress % |

## View Recommendations

| View Type | Best For | Group By |
|-----------|----------|----------|
| Grid | General data work, filtering | — |
| Kanban | Pipeline stages, status tracking | SingleSelect (Status/Stage) |
| Gallery | Visual items with images | Cover image field |
| Form | Data collection, lead capture | — |
| Calendar | Date-based items, scheduling | Date/DateTime field |

## Common Design Mistakes

1. **Everything in one table** — normalize into separate entities with relations
2. **Duplicating data** instead of relations — use Links + Lookups instead of copying data
3. **Creating formulas before relations** — relations must exist first for Lookup/Rollup
4. **Forgetting primary display** — set before creating relations (affects how linked records display)
5. **Using table names in API calls** — always resolve to table_id via list_tables first
6. **No reference tables** — use separate tables or SingleSelect for statuses/categories instead of free text

## Best Practices

1. **Name tables as plural nouns** — Contacts, Deals, Products (not Contact, Deal)
2. **Use Title/Name as first field** — makes primary display intuitive
3. **Add Created/Updated dates** — track record lifecycle
4. **Use SingleSelect over free text** for statuses — enables Kanban views and consistent filtering
5. **Plan relations on paper first** — draw entity relationships before building
6. **Test with sample data** — create a few records after schema to verify relations work
