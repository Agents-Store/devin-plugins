# NocoDB MCP Tool Patterns

Exact parameter formats for all NocoDB MCP tools.

## Tables

### list_tables
```json
Input: {}
Output: { "tables": [{ "id": "tbl_xxx", "name": "Contacts", "meta": {...} }] }
```

### create_table
```json
Input: {
  "name": "Contacts",
  "columns": [
    { "name": "Name", "type": "SingleLineText" },
    { "name": "Email", "type": "Email" },
    { "name": "Status", "type": "SingleSelect", "options": ["Active", "Inactive"] }
  ]
}
Output: { "id": "tbl_xxx", "name": "Contacts" }
```

### get_table
```json
Input: { "table_id": "tbl_xxx" }
Output: { "id": "tbl_xxx", "name": "Contacts", "columns": [...], "views": [...] }
```

### delete_table
```json
Input: { "table_id": "tbl_xxx" }
Output: { "success": true }
```

## Records

### list_records
```json
Input: {
  "table_id": "tbl_xxx",
  "where": "(Status,eq,Active)~and(Amount,gt,1000)",
  "sort": "-CreatedAt",
  "fields": ["Name", "Email", "Amount"],
  "limit": 25,
  "offset": 0
}
Output: { "records": [...], "pageInfo": { "totalRows": 150, "page": 1, "pageSize": 25 } }
```

### create_record
```json
Input: {
  "table_id": "tbl_xxx",
  "data": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "Status": "Active",
    "Amount": 5000
  }
}
Output: { "id": "rec_xxx", ... }
```

### bulk_create_records
```json
Input: {
  "table_id": "tbl_xxx",
  "records": [
    { "Name": "Alice", "Email": "alice@example.com" },
    { "Name": "Bob", "Email": "bob@example.com" }
  ]
}
Output: { "ids": ["rec_xxx", "rec_yyy"], "count": 2 }
```

### update_record
```json
Input: {
  "table_id": "tbl_xxx",
  "record_id": "rec_xxx",
  "data": { "Status": "Closed", "Amount": 7500 }
}
Output: { "id": "rec_xxx", ... }
```

### delete_record
```json
Input: {
  "table_id": "tbl_xxx",
  "record_id": "rec_xxx"
}
Output: { "success": true }
```

## Columns

### list_columns
```json
Input: { "table_id": "tbl_xxx" }
Output: { "columns": [{ "id": "cl_xxx", "name": "Email", "type": "Email" }] }
```

### create_column
```json
// Basic field
Input: {
  "table_id": "tbl_xxx",
  "name": "Phone",
  "type": "PhoneNumber"
}

// SingleSelect with options
Input: {
  "table_id": "tbl_xxx",
  "name": "Priority",
  "type": "SingleSelect",
  "options": ["Low", "Medium", "High", "Critical"]
}

// Relation (LinkToAnotherRecord)
Input: {
  "table_id": "tbl_contacts",
  "name": "Company",
  "type": "LinkToAnotherRecord",
  "linked_table_id": "tbl_companies",
  "relation_type": "hm"
}

// Lookup
Input: {
  "table_id": "tbl_deals",
  "name": "Contact Email",
  "type": "Lookup",
  "relation_column_id": "cl_contact_link",
  "lookup_column_id": "cl_email"
}

// Rollup
Input: {
  "table_id": "tbl_contacts",
  "name": "Total Deals",
  "type": "Rollup",
  "relation_column_id": "cl_deals_link",
  "rollup_column_id": "cl_amount",
  "rollup_function": "sum"
}

// Formula
Input: {
  "table_id": "tbl_xxx",
  "name": "Full Name",
  "type": "Formula",
  "formula": "CONCAT({First Name}, ' ', {Last Name})"
}

Output: { "id": "cl_xxx", "name": "Phone", "type": "PhoneNumber" }
```

### update_column
```json
Input: {
  "table_id": "tbl_xxx",
  "column_id": "cl_xxx",
  "name": "Updated Name",
  "options": ["New Option 1", "New Option 2"]
}
Output: { "id": "cl_xxx", ... }
```

### delete_column
```json
Input: {
  "table_id": "tbl_xxx",
  "column_id": "cl_xxx"
}
Output: { "success": true }
```

## Views

### list_views
```json
Input: { "table_id": "tbl_xxx" }
Output: { "views": [{ "id": "vw_xxx", "title": "All Records", "type": "Grid" }] }
```

### create_view
```json
Input: {
  "table_id": "tbl_xxx",
  "title": "Deal Pipeline",
  "type": "Kanban",
  "group_by": "Stage"
}
Output: { "id": "vw_xxx", "title": "Deal Pipeline", "type": "Kanban" }
```

### update_view
```json
Input: {
  "view_id": "vw_xxx",
  "filters": [
    { "field": "Status", "op": "eq", "value": "Active" }
  ],
  "sorts": [
    { "field": "Name", "direction": "ASC" }
  ]
}
Output: { "id": "vw_xxx", ... }
```

### delete_view
```json
Input: { "view_id": "vw_xxx" }
Output: { "success": true }
```

### get_view_data
```json
Input: {
  "view_id": "vw_xxx",
  "limit": 25,
  "offset": 0
}
Output: { "records": [...], "pageInfo": { "totalRows": 50, "page": 1, "pageSize": 25 } }
```

## Filters

### create_filter
```json
Input: {
  "view_id": "vw_xxx",
  "field": "Status",
  "op": "eq",
  "value": "Active"
}
Output: { "id": "flt_xxx", "field": "Status", "op": "eq", "value": "Active" }
```

### list_filters
```json
Input: { "view_id": "vw_xxx" }
Output: { "filters": [{ "id": "flt_xxx", "field": "Status", "op": "eq", "value": "Active" }] }
```

### delete_filter
```json
Input: { "filter_id": "flt_xxx" }
Output: { "success": true }
```

## Sorts

### create_sort
```json
Input: {
  "view_id": "vw_xxx",
  "field": "CreatedAt",
  "direction": "DESC"
}
Output: { "id": "srt_xxx", "field": "CreatedAt", "direction": "DESC" }
```

### list_sorts
```json
Input: { "view_id": "vw_xxx" }
Output: { "sorts": [{ "id": "srt_xxx", "field": "CreatedAt", "direction": "DESC" }] }
```

### delete_sort
```json
Input: { "sort_id": "srt_xxx" }
Output: { "success": true }
```

## Search & Aggregation

### search_records
```json
Input: {
  "table_id": "tbl_xxx",
  "query": "john doe"
}
Output: { "records": [{ "Id": 1, "Name": "John Doe", "Email": "john@example.com" }] }
```

### aggregate
```json
// Sum
Input: { "table_id": "tbl_xxx", "column": "Amount", "function": "sum" }
Output: { "value": 125000 }

// Count
Input: { "table_id": "tbl_xxx", "column": "Id", "function": "count" }
Output: { "value": 342 }

// Average
Input: { "table_id": "tbl_xxx", "column": "Price", "function": "avg" }
Output: { "value": 49.99 }

// Min / Max
Input: { "table_id": "tbl_xxx", "column": "Amount", "function": "max" }
Output: { "value": 15000 }
```

### group_by
```json
Input: {
  "table_id": "tbl_xxx",
  "column": "Status"
}
Output: [
  { "Status": "Active", "count": 150 },
  { "Status": "Lead", "count": 85 },
  { "Status": "Inactive", "count": 42 }
]
```

### query
```json
Input: {
  "table_id": "tbl_xxx",
  "where": "(Status,eq,Active)~and(Amount,gt,5000)",
  "sort": "-Amount",
  "fields": "Name,Amount,Status",
  "limit": 50
}
Output: { "records": [...], "pageInfo": { "totalRows": 12 } }
```

## Bulk Operations

### bulk_update_records
```json
Input: {
  "table_id": "tbl_xxx",
  "records": [
    { "id": "rec_1", "Status": "Closed" },
    { "id": "rec_2", "Status": "Closed" }
  ]
}
Output: { "count": 2 }
```

### bulk_delete_records
```json
Input: {
  "table_id": "tbl_xxx",
  "record_ids": ["rec_1", "rec_2", "rec_3"]
}
Output: { "count": 3 }
```

### export_table_data
```json
Input: {
  "table_id": "tbl_xxx",
  "format": "csv"
}
Output: { "url": "https://nocodb.example.com/download/export_xxx.csv" }
```

## Webhooks

### create_webhook
```json
Input: {
  "table_id": "tbl_xxx",
  "title": "New Order Notification",
  "event": "after.insert",
  "url": "https://hooks.example.com/new-order",
  "headers": { "Content-Type": "application/json" }
}
Output: { "id": "wh_xxx", "title": "New Order Notification", "event": "after.insert" }
```

### list_webhooks
```json
Input: { "table_id": "tbl_xxx" }
Output: { "webhooks": [{ "id": "wh_xxx", "title": "New Order", "event": "after.insert", "url": "..." }] }
```

### delete_webhook
```json
Input: { "webhook_id": "wh_xxx" }
Output: { "success": true }
```

### test_webhook
```json
Input: { "webhook_id": "wh_xxx" }
Output: { "success": true, "statusCode": 200 }
```
