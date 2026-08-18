# NocoBase MCP Tool Patterns

Exact tool call patterns for all NocoBase MCP tools. Use as reference for building workflows.

## Collection Tools

### collection_list

List all collections in the instance.

```
Input: (no parameters)
Output: [
  { name: "contacts", title: "Contacts", fields: [...] },
  { name: "orders", title: "Orders", fields: [...] }
]
```

### collection_get

Get detailed collection info including fields and relations.

```
Input: { name: "contacts" }
Output: {
  name: "contacts",
  title: "Contacts",
  fields: [
    { name: "name", type: "string", required: true },
    { name: "email", type: "email", unique: true },
    { name: "company", type: "belongsTo", target: "companies" },
    { name: "createdAt", type: "datetime" }
  ]
}
```

## Page & UI Tools

### page_create

Create a new page.

```
Input: { title: "Contacts", icon: "UserOutlined", parent: "CRM" }
Output: { id: "page_abc123", title: "Contacts" }
```

### page_list

List all pages.

```
Input: (no parameters)
Output: [
  { id: "page_abc123", title: "Contacts", parent: "CRM" },
  { id: "page_def456", title: "Dashboard", parent: null }
]
```

### page_inspect

Inspect page structure — blocks, columns, actions.

```
Input: { id: "page_abc123" }
Output: {
  title: "Contacts",
  blocks: [
    {
      type: "table",
      collection: "contacts",
      columns: ["name", "email", "phone", "status"],
      actions: ["create", "edit", "delete", "filter"]
    }
  ]
}
```

### page_delete

Delete a page.

```
Input: { id: "page_abc123" }
Output: { success: true }
```

### menu_create_group

Create a menu group for organizing pages.

```
Input: { title: "CRM", icon: "UserOutlined" }
Output: { id: "menu_group_xyz", title: "CRM" }
```

### table_add

Add a block (table, form, details, kanban, calendar) to a page.

```
Input: {
  pageId: "page_abc123",
  collection: "contacts",
  type: "table"  // table | form | details | kanban | calendar
}
Output: { blockId: "block_123", type: "table", collection: "contacts" }
```

For kanban:
```
Input: {
  pageId: "page_abc123",
  collection: "deals",
  type: "kanban",
  groupField: "stage"
}
```

### column_add

Add a column/field to a block.

```
Input: { blockId: "block_123", fieldName: "name" }
Output: { success: true, field: "name" }
```

### action_add

Add an action button to a block.

```
Input: { blockId: "block_123", type: "create" }
// Types: create, edit, delete, view, duplicate, filter, export, submit, cancel
Output: { success: true, action: "create" }
```

## Data Tools

### data_list

List records from a collection.

```
Input: {
  collection: "contacts",
  filter: { status: "Active" },
  sort: ["-createdAt"],
  limit: 20,
  offset: 0
}
Output: {
  data: [
    { id: 1, name: "John", email: "john@example.com", status: "Active" },
    { id: 2, name: "Jane", email: "jane@example.com", status: "Active" }
  ],
  total: 45
}
```

### data_create

Create a record.

```
Input: {
  collection: "contacts",
  data: { name: "John Doe", email: "john@example.com", status: "Lead" }
}
Output: { id: 3, name: "John Doe", email: "john@example.com", status: "Lead" }
```

### data_update

Update a record.

```
Input: {
  collection: "contacts",
  filter: { id: 3 },
  data: { status: "Active" }
}
Output: { id: 3, name: "John Doe", status: "Active" }
```

### data_delete

Delete a record.

```
Input: {
  collection: "contacts",
  filter: { id: 3 }
}
Output: { success: true }
```

## Health Tool

### health_check

Check NocoBase server health.

```
Input: (no parameters)
Output: { status: "ok", version: "1.4.0" }
```
