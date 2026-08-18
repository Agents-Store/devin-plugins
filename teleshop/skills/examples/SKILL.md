---
name: examples
description: MCP tool call patterns, end-to-end workflow examples, code templates, and scenario references. Use when you need reference implementations for Teleshop operations.
---

# Examples & References

This skill provides reference implementations, tool call patterns, and complete workflow scenarios for Teleshop store management.

## Reference Files

| File | Description |
|------|-------------|
| [tool-patterns.md](references/mcp/tool-patterns.md) | MCP tool call patterns with exact parameter formats |
| [workflow-examples.md](references/mcp/workflow-examples.md) | Multi-step workflow examples combining multiple tools |
| [store-setup.md](references/scenarios/store-setup.md) | Complete store setup scenario from scratch |
| [order-processing.md](references/scenarios/order-processing.md) | Order lifecycle processing scenario |

## Quick Reference: All 50 Tools by Group

### Products (9)
`list_products`, `get_product`, `create_product`, `batch_create_products`, `update_product`, `delete_product`, `batch_delete_products`, `update_product_images`, `update_product_attributes`

### Orders (5)
`list_orders`, `get_order`, `update_order`, `update_order_status`, `update_order_payment`

### Categories (7)
`list_categories`, `get_category`, `create_category`, `batch_create_categories`, `update_category`, `delete_category`, `batch_delete_categories`

### Attributes (6)
`list_attributes`, `get_attribute`, `create_attribute`, `update_attribute`, `delete_attribute`, `add_attribute_values`

### Customers (2)
`list_customers`, `get_customer`

### Catalog Import (1)
`import_catalog`

### Webhooks (12)
`list_webhooks`, `get_webhook_events`, `get_webhook`, `create_webhook`, `update_webhook`, `delete_webhook`, `test_webhook`, `get_webhook_sample_payload`, `get_webhook_logs`, `get_webhook_secret`, `get_webhook_stats`, `toggle_webhook`

### Addons (8)
`list_workflows`, `toggle_workflow`, `get_workflow_variables`, `set_workflow_variables`, `execute_workflow`, `get_workflow_schedule`, `set_workflow_schedule`, `clear_workflow_schedule`
