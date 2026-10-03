---
name: nocodb-to-n8n
description: This skill should be used when the user wants to "trigger n8n workflow from NocoDB", "connect NocoDB data to n8n", "create webhook from NocoDB to n8n", "automate NocoDB with n8n", or needs to integrate NocoDB data events with n8n workflow automation.
---

# NocoDB to n8n Integration

Patterns for connecting NocoDB data events to n8n workflow automation: webhook triggers, data sync, and cross-service operations. NocoDB-side detail is in `nocodb-ops`, n8n-side detail in `n8n-dev`; this skill is the link between them.

## Integration Patterns

### Pattern 1: NocoDB Webhook → n8n Workflow

Trigger an n8n workflow when NocoDB records change.

**Setup steps:**

1. Create an n8n workflow with a Webhook trigger node and **publish** it (in n8n 2.x the production URL receives events only after Publish)
2. Copy the Webhook node's **production** URL
3. Create a NocoDB webhook pointing to that URL — events, UI steps, conditions, testing and the Button trigger: see `nocodb-ops:webhooks`

**n8n workflow structure:**

```
[Webhook] → [Split Out: body.data.rows] → [Business Logic] → [Respond to Webhook]
```

The payload carries the changed records as an array, `body.data.rows`, with the event in `body.type` and the table in `body.data.table_id` — one event can hold several records, so split it before processing. Payload format and events: see `nocodb-ops:webhooks`.

### Pattern 2: Reading NocoDB Data

The workflow reads NocoDB with the n8n **NocoDB** node (or an HTTP Request on the NocoDB API). When Claude checks the same data while building the workflow, it uses the NocoDB MCP — `pageSize` and `page` for paging (there is no `limit`), `filter` for conditions:

```
Tool: mcp__plugin_stack-composable-stack-v1_nocodb__queryRecords
Input: {
  "tableId": "tbl_xxx",
  "filter": { "field": "Status", "operator": "eq", "value": "active" },
  "pageSize": 100
}
```

Use this pattern when:
- The workflow needs to look up related data
- The workflow processes records in batches
- Data is enriched before it goes to external services

Tool parameters, `filter` versus `where`, date sub-operators: see `nocodb-ops:mcp-patterns`.

### Pattern 3: Writing Back to NocoDB

The workflow creates or updates NocoDB records after processing (NocoDB node, or an HTTP Request on the NocoDB API). The MCP form, for Claude-side writes, wraps every record in `fields` and takes at most 100 records per call:

```
Tool: mcp__plugin_stack-composable-stack-v1_nocodb__createRecords
Input: {
  "tableId": "tbl_xxx",
  "records": [
    { "fields": { "Title": "Processed Item", "Status": "completed", "processed_at": "2026-04-07T12:00:00Z" } }
  ]
}
```

If the write-back goes to the table whose webhook started the workflow, it fires that webhook again — gate the webhook with a condition on the status transition (`nocodb-ops:webhooks`, *Conditions*) or write the result to another table.

### Pattern 4: Scheduled n8n Sync

An n8n Schedule trigger polls NocoDB for records matching criteria and processes them.

```
[Schedule Trigger (every 5min)] → [Query NocoDB Records] → [Filter Changed] → [Process] → [Update Status in NocoDB]
```

Use for:
- Periodic data sync to external services
- Batch processing of queued records
- Report generation from NocoDB data

Workflow shapes and node notes: see `n8n-dev:examples` (`references/background-processing-patterns.md`).

## Workflow Naming Convention

Follow the project convention: `[Domain] - [Action] - [Trigger]`

Examples:
- `Orders - Process Payment - NocoDB Webhook`
- `Users - Sync to CRM - Schedule`
- `Inventory - Update Stock - NocoDB Webhook`

## Error Handling

1. **n8n Error Trigger node** — catch workflow failures, log to a NocoDB error table
2. **Retry logic** — use n8n retry settings for transient failures (429, 5xx)
3. **Dead letter table** — create a `failed_events` NocoDB table for manual review
4. **Idempotency** — check the record ID before processing to avoid duplicates; a webhook event can arrive more than once

## Best Practices

- Name webhook trigger nodes descriptively: `NocoDB - New Order Created`
- Parse and validate the NocoDB payload early in the workflow
- Use NocoDB record IDs (not display values) for lookups
- Log the webhook event type for debugging
- Publish the n8n workflow (n8n 2.x: Activate is now Publish) so the production webhook URL receives events
- Keep tokens in n8n credentials and send them as headers — n8n 2.x blocks `$env` in expressions and Code nodes by default, and a secret in the webhook URL ends up in logs
