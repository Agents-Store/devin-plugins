---
name: view-management
description: View types — Grid, Kanban, Gallery, Form, Calendar. This skill should be used when the user asks to create or configure views, set up a kanban board, build a form, or manage view filters and sorts.
---

# View Management

This skill covers view operations in NocoDB — creating and configuring Grid, Kanban, Gallery, Form, and Calendar views with filters, sorting, and field visibility.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_views` | List all views for a table |
| `create_view` | Create a new view |
| `update_view` | Update view configuration (filters, sorts, fields) |
| `delete_view` | Delete a view |
| `create_filter` | Add a filter to a view |
| `list_filters` | List filters on a view |
| `delete_filter` | Remove a filter from a view |
| `create_sort` | Add a sort rule to a view |
| `list_sorts` | List sort rules on a view |
| `delete_sort` | Remove a sort rule from a view |
| `get_view_data` | Get records through a specific view |

## Listing Views

```
Tool: list_views
Input: { "table_id": "tbl_abc123" }

Returns: Array of views with id, title, type, and configuration.
```

## View Types

### Grid View
General-purpose data view. Best for working with records, filtering, and sorting.

```
Tool: create_view
Input: {
  "table_id": "tbl_abc123",
  "title": "All Contacts",
  "type": "Grid"
}
```

### Kanban View
Board view grouped by a SingleSelect field. Best for pipeline/status tracking.

```
Tool: create_view
Input: {
  "table_id": "tbl_deals",
  "title": "Deal Pipeline",
  "type": "Kanban",
  "group_by": "Stage"
}
```

**Requires:** A SingleSelect column to group by (e.g., Status, Stage, Priority).

### Gallery View
Card view with cover images. Best for visual items like products or contacts.

```
Tool: create_view
Input: {
  "table_id": "tbl_products",
  "title": "Product Catalog",
  "type": "Gallery",
  "cover_image_field": "Photo"
}
```

**Requires:** An Attachment column for cover images.

### Form View
Data entry form. Best for collecting submissions and lead capture.

```
Tool: create_view
Input: {
  "table_id": "tbl_leads",
  "title": "Lead Capture Form",
  "type": "Form"
}
```

Configure which fields are visible and required in the form.

### Calendar View
Date-based calendar layout. Best for scheduling and events.

```
Tool: create_view
Input: {
  "table_id": "tbl_events",
  "title": "Event Calendar",
  "type": "Calendar",
  "date_field": "EventDate"
}
```

**Requires:** A Date or DateTime column.

## Configuring Views

### Add Filters
```
Tool: update_view
Input: {
  "view_id": "vw_abc123",
  "filters": [
    { "field": "Status", "op": "eq", "value": "Active" },
    { "field": "Amount", "op": "gt", "value": 1000 }
  ]
}
```

### Add Sorting
```
Tool: update_view
Input: {
  "view_id": "vw_abc123",
  "sorts": [
    { "field": "Priority", "direction": "DESC" },
    { "field": "Name", "direction": "ASC" }
  ]
}
```

### Hide/Show Fields
```
Tool: update_view
Input: {
  "view_id": "vw_abc123",
  "fields": {
    "Name": { "visible": true, "order": 1 },
    "Email": { "visible": true, "order": 2 },
    "InternalNotes": { "visible": false }
  }
}
```

## Common Workflows

### Create View with Configuration
```
1. list_tables() -> Find table
2. list_columns(table_id) -> See available columns
3. create_view(table_id, title, type) -> Create view
4. update_view(view_id, filters, sorts, fields) -> Configure
```

### Set Up Complete Table Views
```
1. create_view(type=Grid, title="All Records") -> Default working view
2. create_view(type=Kanban, title="Pipeline", group_by="Status") -> Status board
3. create_view(type=Form, title="New Entry") -> Data entry form
4. create_view(type=Gallery, title="Gallery") -> Visual card view
```

### Create Filtered Dashboard Views
```
1. create_view(type=Grid, title="Active Items") -> For active records
2. update_view(filters=[Status=Active]) -> Apply filter
3. create_view(type=Grid, title="Overdue Items") -> For overdue items
4. update_view(filters=[DueDate < today, Status != Done]) -> Apply filter
```

## View Recommendations by Use Case

| Use Case | View Type | Group By / Config |
|----------|-----------|-------------------|
| CRM pipeline | Kanban | Stage (SingleSelect) |
| Product catalog | Gallery | Cover image (Attachment) |
| Contact list | Grid | Sorted by Name, filtered by Status |
| Lead capture | Form | Required: Name, Email |
| Event planning | Calendar | Event Date (Date field) |
| Task board | Kanban | Priority or Status |
| Data review | Grid | All fields visible, sortable |

## Granular Filter Management

### Create Filter
```
Tool: create_filter
Input: {
  "view_id": "vw_abc123",
  "field": "Status",
  "op": "eq",
  "value": "Active"
}
```

### List Filters
```
Tool: list_filters
Input: { "view_id": "vw_abc123" }

Returns: Array of active filters with IDs, fields, operators, and values.
```

### Delete Filter
```
Tool: delete_filter
Input: { "filter_id": "flt_xyz789" }
```

## Granular Sort Management

### Create Sort
```
Tool: create_sort
Input: {
  "view_id": "vw_abc123",
  "field": "Amount",
  "direction": "DESC"
}
```

### List Sorts
```
Tool: list_sorts
Input: { "view_id": "vw_abc123" }
```

### Delete Sort
```
Tool: delete_sort
Input: { "sort_id": "srt_xyz789" }
```

## Get View Data

Get records through a specific view (applies view filters and sorts).

```
Tool: get_view_data
Input: {
  "view_id": "vw_abc123",
  "limit": 25,
  "offset": 0
}
```

## Advanced Workflows

### Create View with Granular Filters and Sorts
```
1. create_view(table_id, title, type) → Create view
2. create_filter(view_id, field="Status", op="eq", value="Active") → Add filter
3. create_filter(view_id, field="Amount", op="gt", value=1000) → Add another filter
4. create_sort(view_id, field="Amount", direction="DESC") → Add sort
5. get_view_data(view_id) → Verify the view shows correct data
```

### Audit and Update View Configuration
```
1. list_views(table_id) → Find existing views
2. list_filters(view_id) → Check current filters
3. list_sorts(view_id) → Check current sorts
4. delete_filter(filter_id) → Remove outdated filters
5. create_filter(view_id, ...) → Add new filters
```

## Best Practices

1. **Create views AFTER schema is complete** — all fields should exist first
2. **Name views descriptively** — "Active Deals" not "View 1"
3. **Use Kanban for status tracking** — requires SingleSelect field
4. **Hide internal fields in Forms** — only show user-facing fields
5. **Create role-specific views** — different views for different user personas
6. **Set default sort** — most views benefit from a default sort order
7. **Use granular filter/sort tools** — for precise control over individual filters
8. **Verify with get_view_data** — always check that filters produce expected results

## Error Handling Patterns

### Common Failure Scenarios
- **View creation fails** → verify table_id exists; for Kanban, ensure group_by field is SingleSelect; for Calendar, ensure date_field is Date/DateTime; for Gallery, ensure cover_image_field is Attachment
- **Filter references invalid field** → list_columns first to verify field names and types; field names are case-sensitive
- **Sort on unsupported field** → not all field types support sorting (e.g., Attachment); check field type before adding sort
- **View data returns empty** → filters may be too restrictive; list_filters to audit, then selectively delete overly narrow filters
- **Duplicate view name** → some implementations reject duplicate names; use unique descriptive titles

### Defensive Workflow
1. Always list_columns(table_id) before creating views — verify required fields exist
2. For Kanban: confirm group_by field is SingleSelect type
3. For Calendar: confirm date_field is Date or DateTime type
4. For Gallery: confirm cover_image_field is Attachment type
5. After creating view: get_view_data to verify it returns expected records
6. After adding filters: get_view_data to confirm filter works correctly
