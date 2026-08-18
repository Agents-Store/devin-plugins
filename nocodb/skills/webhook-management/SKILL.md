---
name: webhook-management
description: Webhook management — create, list, delete, and test webhooks for table events. This skill should be used when the user asks to set up webhooks, configure event notifications, or integrate with external systems.
---

# Webhook Management

Guide for managing NocoDB webhooks — event notifications for record changes, integrations with external systems.

## Available Tools

| Tool | Purpose |
|------|---------|
| `create_webhook` | Create a webhook for table events |
| `list_webhooks` | List all webhooks for a table |
| `delete_webhook` | Delete a webhook |
| `test_webhook` | Send a test payload to a webhook URL |

## Create Webhook

```
Tool: create_webhook
Input: {
  "table_id": "tbl_abc123",
  "title": "New Order Notification",
  "event": "after.insert",
  "url": "https://hooks.example.com/new-order"
}

Returns: { "id": "wh_xyz789", "title": "New Order Notification", ... }
```

### Event Types

| Event | Trigger |
|-------|---------|
| `after.insert` | After a record is created |
| `after.update` | After a record is updated |
| `after.delete` | After a record is deleted |
| `after.bulkInsert` | After bulk record creation |
| `after.bulkUpdate` | After bulk record update |
| `after.bulkDelete` | After bulk record deletion |

### Webhook with Headers
```
Tool: create_webhook
Input: {
  "table_id": "tbl_abc123",
  "title": "Slack Notification",
  "event": "after.insert",
  "url": "https://hooks.slack.com/services/xxx",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

## List Webhooks

```
Tool: list_webhooks
Input: { "table_id": "tbl_abc123" }

Returns: [
  { "id": "wh_1", "title": "New Order", "event": "after.insert", "url": "..." },
  { "id": "wh_2", "title": "Order Update", "event": "after.update", "url": "..." }
]
```

## Delete Webhook

```
Tool: delete_webhook
Input: { "webhook_id": "wh_xyz789" }
```

## Test Webhook

Send a test payload to verify webhook URL is reachable and configured correctly.

```
Tool: test_webhook
Input: { "webhook_id": "wh_xyz789" }

Returns: { "success": true, "statusCode": 200 }
```

## Workflows

### Set Up Full CRUD Notifications
```
1. create_webhook(table_id, "Record Created", "after.insert", url) → Create notification
2. create_webhook(table_id, "Record Updated", "after.update", url) → Update notification
3. create_webhook(table_id, "Record Deleted", "after.delete", url) → Delete notification
4. For each: test_webhook(webhook_id) → Verify all webhooks work
```

### Integration with External Service
```
1. list_tables() → Find target table
2. create_webhook(table_id, title, event, external_url) → Set up webhook
3. test_webhook(webhook_id) → Verify connection
4. create_record(table_id, data) → Trigger webhook with real data
5. Verify external service received the payload
```

### Audit and Clean Up Webhooks
```
1. list_tables() → Get all tables
2. For each table: list_webhooks(table_id) → Find all webhooks
3. test_webhook(webhook_id) → Test each webhook
4. If test fails: delete_webhook(webhook_id) → Remove broken webhooks
```

## Webhook Payload Structure

Webhooks send JSON payloads with the following structure:
```json
{
  "type": "records.after.insert",
  "table_id": "tbl_abc123",
  "table_name": "orders",
  "data": {
    "rows": [
      { "Id": 1, "Name": "New Order", "Amount": 5000, "Status": "Active" }
    ]
  }
}
```

## Integration Examples

### Notify on New Record
```
1. create_webhook(table_id, "New Record Alert", "after.insert", "https://hooks.example.com/new-record")
2. Payload includes: table name, record data, timestamp
3. Use for: Slack notifications, email alerts, syncing to external systems
```

### Sync on Update
```
1. create_webhook(table_id, "Sync Updates", "after.update", "https://api.example.com/sync")
2. Payload includes: updated row data with new values
3. Use for: keeping external database in sync, triggering recalculations
```

### Audit Trail
```
1. create_webhook(table_id, "Audit: Created", "after.insert", "https://audit.example.com/log")
2. create_webhook(table_id, "Audit: Updated", "after.update", "https://audit.example.com/log")
3. create_webhook(table_id, "Audit: Deleted", "after.delete", "https://audit.example.com/log")
4. Captures all changes for compliance/audit
```

## Error Handling

- **Webhook delivery fails** → most implementations retry 3-5 times with exponential backoff
- **URL unreachable** → use test_webhook before relying on it in production
- **Duplicate events** → design webhook receivers to be idempotent (handle same event twice safely)
- **Payload too large** → some systems limit payload size; use webhook to signal change, then fetch full data via API

## Best Practices

1. **Test before relying** — always use `test_webhook` after creation
2. **Use descriptive titles** — "Slack: New Order" not "Webhook 1"
3. **One webhook per event type** — don't try to handle all events in one webhook
4. **Clean up unused webhooks** — regularly audit and remove broken/unused webhooks
5. **Handle failures externally** — webhook delivery is fire-and-forget; build retry logic in the receiving service
6. **Use headers for auth** — if your endpoint requires authentication, pass headers
