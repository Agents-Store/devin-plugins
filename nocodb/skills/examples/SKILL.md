---
name: examples
description: Tool call patterns, end-to-end workflow examples, and scenario references. This skill should be used when the user needs reference implementations, complete examples, or tool call patterns.
---

# Examples & References

This skill provides reference implementations, tool call patterns, and complete workflow scenarios for NocoDB database management.

## Reference Files

| File | Description |
|------|-------------|
| [tool-patterns.md](references/mcp/tool-patterns.md) | MCP tool call patterns with exact parameter formats |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step workflow examples combining multiple tools |
| [database-setup.md](references/scenarios/database-setup.md) | Complete database setup scenario from scratch |
| [crm-schema.md](references/scenarios/crm-schema.md) | CRM schema design with contacts, deals, and pipeline |

## Quick Reference: All Tools by Group

### Tables (4)
`list_tables`, `create_table`, `get_table`, `delete_table`

### Records (8)
`list_records`, `create_record`, `bulk_create_records`, `update_record`, `delete_record`, `bulk_update_records`, `bulk_delete_records`, `export_table_data`

### Columns (4)
`list_columns`, `create_column`, `update_column`, `delete_column`

### Views (5)
`list_views`, `create_view`, `update_view`, `delete_view`, `get_view_data`

### Filters & Sorts (6)
`create_filter`, `list_filters`, `delete_filter`, `create_sort`, `list_sorts`, `delete_sort`

### Search & Aggregation (4)
`search_records`, `query`, `aggregate`, `group_by`

### Webhooks (4)
`create_webhook`, `list_webhooks`, `delete_webhook`, `test_webhook`
