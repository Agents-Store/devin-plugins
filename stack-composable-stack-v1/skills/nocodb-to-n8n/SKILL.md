---
name: nocodb-to-n8n
description: This skill should be used when the user wants to "trigger n8n workflow from NocoDB", "connect NocoDB data to n8n", "create webhook from NocoDB to n8n", "automate NocoDB with n8n", or needs to integrate NocoDB data events with n8n workflow automation.
---

# NocoDB to n8n Integration

Patterns for connecting NocoDB data events to n8n workflow automation. Covers webhook triggers, data sync, and cross-service operations.

## Integration Patterns

### Pattern 1: NocoDB Webhook → n8n Workflow

Trigger an n8n workflow when NocoDB records change.

**Setup steps:**

1. Create an n8n workflow with a Webhook trigger node
2. Copy the webhook URL from n8n
3. Create a NocoDB webhook pointing to that URL

**n8n workflow structure:**

```
[Webhook] → [Parse NocoDB Payload] → [Business Logic] → [Response]
```

**NocoDB webhook payload format:**

```json
{
  "type": "records.after.insert",
  "data": {
    "table_id": "tbl_xxx",
    "rows": [
      {
        "Id": 1,
        "Title": "New Record",
        "Status": "active"
      }
    ]
  }
}
```

**Supported NocoDB webhook events:**
- `records.after.insert` — new record created
- `records.after.update` — record modified
- `records.after.delete` — record deleted
- `records.after.bulkInsert` — bulk records created
- `records.after.bulkUpdate` — bulk records modified

### Pattern 2: n8n Reads NocoDB Data via MCP

n8n workflow reads NocoDB records using the NocoDB MCP tools.

```
Tool: mcp__nocodb__queryRecords
Input: {
  "tableId": "tbl_xxx",
  "where": "(Status,eq,active)",
  "limit": 100
}
```

Use this pattern when:
- n8n workflow needs to look up related data
- Workflow processes records in batches
- Data enrichment before sending to external services

### Pattern 3: n8n Writes Back to NocoDB

n8n workflow creates or updates NocoDB records after processing.

```
Tool: mcp__nocodb__createRecords
Input: {
  "tableId": "tbl_xxx",
  "records": [
    {
      "Title": "Processed Item",
      "Status": "completed",
      "processed_at": "2026-04-07T12:00:00Z"
    }
  ]
}
```

### Pattern 4: Scheduled n8n Sync

n8n Schedule trigger polls NocoDB for records matching criteria and processes them.

```
[Schedule Trigger (every 5min)] → [Query NocoDB Records] → [Filter Changed] → [Process] → [Update Status in NocoDB]
```

Use for:
- Periodic data sync to external services
- Batch processing of queued records
- Report generation from NocoDB data

## Workflow Naming Convention

Follow the project convention: `[Domain] - [Action] - [Trigger]`

Examples:
- `Orders - Process Payment - NocoDB Webhook`
- `Users - Sync to CRM - Schedule`
- `Inventory - Update Stock - NocoDB Webhook`

## Error Handling

1. **n8n Error Trigger node** — catch workflow failures, log to NocoDB error table
2. **Retry logic** — use n8n retry settings for transient failures (429, 5xx)
3. **Dead letter table** — create a `failed_events` NocoDB table for manual review
4. **Idempotency** — check record ID before processing to avoid duplicates

## Best Practices

- Name webhook trigger nodes descriptively: `NocoDB - New Order Created`
- Parse and validate the NocoDB payload early in the workflow
- Use NocoDB record IDs (not display values) for lookups
- Log the webhook event type for debugging
- Set n8n workflow to production mode for reliable execution
- Keep webhook URLs in environment variables, not hardcoded in NocoDB
