# NocoDB Workflow Examples

Multi-step workflows combining multiple NocoDB tools.

## Workflow 1: Create a Complete Table with Relations

Build a Products table related to a Categories table.

```
Step 1: Check existing tables
Tool: list_tables
→ Result: No "Categories" or "Products" table exists

Step 2: Create Categories table
Tool: create_table
Input: {
  "name": "Categories",
  "columns": [
    { "name": "Name", "type": "SingleLineText" },
    { "name": "Description", "type": "LongText" },
    { "name": "Active", "type": "Checkbox" }
  ]
}
→ Result: { "id": "tbl_cat001" }

Step 3: Create Products table
Tool: create_table
Input: {
  "name": "Products",
  "columns": [
    { "name": "Name", "type": "SingleLineText" },
    { "name": "Price", "type": "Currency" },
    { "name": "Description", "type": "LongText" },
    { "name": "InStock", "type": "Checkbox" },
    { "name": "SKU", "type": "SingleLineText" }
  ]
}
→ Result: { "id": "tbl_prod001" }

Step 4: Add relation (Product → Category)
Tool: create_column
Input: {
  "table_id": "tbl_prod001",
  "name": "Category",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "tbl_cat001",
  "relation_type": "hm"
}
→ Result: Link column created in Products, reverse link in Categories

Step 5: Add Rollup (Category → count of Products)
Tool: list_columns
Input: { "table_id": "tbl_cat001" }
→ Get the reverse link column ID (e.g., "cl_products_link")

Tool: create_column
Input: {
  "table_id": "tbl_cat001",
  "name": "Product Count",
  "type": "Rollup",
  "relation_column_id": "cl_products_link",
  "rollup_column_id": "cl_id",
  "rollup_function": "count"
}
```

## Workflow 2: Import Data with Validation

Import contacts from a CSV-like dataset.

```
Step 1: Find target table
Tool: list_tables
→ Find "Contacts" table ID: "tbl_contacts"

Step 2: Verify column structure
Tool: list_columns
Input: { "table_id": "tbl_contacts" }
→ Columns: Name (Text), Email (Email), Phone (Phone), Status (SingleSelect)

Step 3: Bulk create records
Tool: bulk_create_records
Input: {
  "table_id": "tbl_contacts",
  "records": [
    { "Name": "Alice Johnson", "Email": "alice@company.com", "Phone": "+1234567890", "Status": "Active" },
    { "Name": "Bob Smith", "Email": "bob@company.com", "Phone": "+0987654321", "Status": "Lead" },
    { "Name": "Carol Williams", "Email": "carol@company.com", "Status": "Active" }
  ]
}
→ Result: 3 records created

Step 4: Verify import
Tool: list_records
Input: { "table_id": "tbl_contacts", "limit": 5, "sort": "-CreatedAt" }
→ Confirm all records present
```

## Workflow 3: Set Up Kanban Board

Create a task board with Kanban view.

```
Step 1: Create Tasks table
Tool: create_table
Input: {
  "name": "Tasks",
  "columns": [
    { "name": "Title", "type": "SingleLineText" },
    { "name": "Description", "type": "LongText" },
    { "name": "Status", "type": "SingleSelect", "options": ["To Do", "In Progress", "Review", "Done"] },
    { "name": "Priority", "type": "SingleSelect", "options": ["Low", "Medium", "High"] },
    { "name": "DueDate", "type": "Date" },
    { "name": "Assignee", "type": "SingleLineText" }
  ]
}
→ Result: { "id": "tbl_tasks" }

Step 2: Create Kanban view
Tool: create_view
Input: {
  "table_id": "tbl_tasks",
  "title": "Task Board",
  "type": "Kanban",
  "group_by": "Status"
}
→ Result: Kanban view created grouped by Status

Step 3: Create filtered view for high priority
Tool: create_view
Input: {
  "table_id": "tbl_tasks",
  "title": "High Priority",
  "type": "Grid"
}
Tool: update_view
Input: {
  "view_id": "<new_view_id>",
  "filters": [{ "field": "Priority", "op": "eq", "value": "High" }],
  "sorts": [{ "field": "DueDate", "direction": "ASC" }]
}

Step 4: Add sample tasks
Tool: bulk_create_records
Input: {
  "table_id": "tbl_tasks",
  "records": [
    { "Title": "Design homepage", "Status": "To Do", "Priority": "High", "Assignee": "Alice" },
    { "Title": "Write tests", "Status": "In Progress", "Priority": "Medium", "Assignee": "Bob" },
    { "Title": "Deploy v2.0", "Status": "To Do", "Priority": "High", "Assignee": "Carol" }
  ]
}
```

## Workflow 4: Search, Filter, and Update

Find and update specific records.

```
Step 1: Find records matching criteria
Tool: list_records
Input: {
  "table_id": "tbl_contacts",
  "where": "(Status,eq,Lead)~and(CreatedAt,gt,2024-01-01)",
  "sort": "-CreatedAt",
  "limit": 50
}
→ Result: 12 matching records

Step 2: Update each matching record
Tool: update_record
Input: {
  "table_id": "tbl_contacts",
  "record_id": "rec_001",
  "data": { "Status": "Active", "Notes": "Converted from lead" }
}
→ Repeat for each record

Step 3: Verify changes
Tool: list_records
Input: {
  "table_id": "tbl_contacts",
  "where": "(Status,eq,Active)",
  "sort": "-UpdatedAt",
  "limit": 15
}
→ Confirm updates applied
```
