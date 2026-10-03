---
name: nocobase-to-n8n
description: This skill should be used when the user wants to "trigger n8n from NocoBase", "connect NocoBase UI to n8n", "automate NocoBase actions with n8n", "create NocoBase workflow that calls n8n", or needs to integrate NocoBase interface events with n8n workflow automation.
---

# NocoBase to n8n Integration

Patterns for connecting NocoBase UI actions and workflow events to n8n automation: NocoBase webhooks, API triggers, and cross-service coordination. NocoBase detail is in `nocobase-dev`, n8n detail in `n8n-dev`; this skill is the link between them.

## Dev vs Production Instance

This stack runs two NocoBase instances:

| Instance | URL / API key | When to use |
|----------|---------------|-------------|
| **Prod** | `${NOCOBASE_URL}` / `${NOCOBASE_API_KEY}` | Live integrations, released collections |
| **Dev** | `${NOCOBASE_DEV_URL}` / `${NOCOBASE_DEV_API_KEY}` | Wiring up new collection events, testing webhook payloads, prototyping button actions, and running dev/test apps |

Build and iterate every new NocoBase → n8n integration on the **dev** instance first (it also has a `nocobase-dev` MCP server for fast Claude-driven authoring). Only swap the n8n HTTP node URLs and NocoBase credentials to prod once the workflow is stable.

## Integration Patterns

### Pattern 1: NocoBase Workflow → n8n Webhook

Use NocoBase's built-in workflow engine to trigger n8n when collection events occur.

**Setup steps:**

1. Create an n8n workflow with a Webhook trigger node and publish it
2. In NocoBase, create a workflow with trigger type "Collection event"
3. Add an "HTTP request" node in the NocoBase workflow pointing to the n8n webhook (production) URL
4. Map NocoBase collection fields to the HTTP request body

**NocoBase workflow configuration:**

- Trigger: Collection event on target collection
- Event: After create / After update / After delete
- Action node: HTTP request → n8n webhook URL

**n8n receives** whatever body you map in step 4, for example:

```json
{
  "collection": "orders",
  "event": "afterCreate",
  "data": {
    "id": 1,
    "title": "New Order",
    "status": "pending",
    "created_at": "2026-04-07T12:00:00Z"
  }
}
```

Building the NocoBase workflow (triggers, nodes, variables): see `nocobase-dev:nocobase-workflow-manage`.

### Pattern 2: NocoBase Button → n8n Workflow

Create a custom action button in NocoBase that triggers an n8n workflow.

**Setup steps:**

1. Create and publish an n8n webhook workflow
2. In NocoBase, add a custom action button to a collection's table or form block
3. Configure the button to call the n8n webhook URL with the current record data

### Pattern 3: n8n Reads/Writes NocoBase via API

n8n interacts with NocoBase collections through the NocoBase REST API — an HTTP Request node with the API key in a Header Auth credential, calling `${NOCOBASE_URL}/api/<collection>:list`, `:create` and `:update?filterByTk=<id>`. Filter syntax, response shape and curl recipes: see `nocobase-dev:api-reference` (`references/common-endpoints.md`, *Calling the API from n8n or another service*). The stack's `NOCOBASE_URL` / `NOCOBASE_API_KEY` are that skill's `NB_URL` and bearer token.

### Pattern 4: NocoBase Schedule → n8n Processing

Use NocoBase's scheduled workflow trigger to periodically call n8n.

**Setup:**
1. NocoBase workflow: Schedule trigger (e.g., every hour)
2. NocoBase HTTP node: call the n8n webhook
3. n8n workflow: process data and write results back

## Shared Data Between NocoBase and NocoDB

NocoBase and NocoDB can both connect to the same PostgreSQL database. When they share tables:

- **NocoBase** provides the UI (forms, dashboards, admin panels)
- **NocoDB** provides MCP access for Claude operations
- **PostgreSQL** is the source of truth

Changes made through either interface are immediately visible to both once the schema is synced (Meta Sync in NocoDB, refresh of the data source in NocoBase — see `postgresql-external-dev:modify-schema`). Use NocoDB MCP tools for data operations in Claude workflows and NocoBase for user-facing interactions.

## Workflow Naming Convention

NocoBase workflows: `[Collection] - [Action] - [Event Type]`

Examples:
- `Orders - Notify Warehouse - After Create`
- `Users - Sync Profile - After Update`
- `Invoices - Generate PDF - Button Action`

## Error Handling

1. **NocoBase workflow error handling** — add try-catch nodes in NocoBase workflows
2. **n8n Error Trigger** — catch failed webhook processing
3. **Retry configuration** — configure retries in both the NocoBase HTTP node and n8n
4. **Logging** — log failed events to a shared error collection

## Best Practices

- Use NocoBase workflow variables for n8n webhook URLs — do not hardcode
- Include the collection name and record ID in every webhook payload
- Validate that the NocoBase API key's role permits the required operations
- Use NocoBase's built-in workflow engine for simple automations, n8n for complex orchestration
- In n8n keep the NocoBase API key in a credential, not an `$env` expression (blocked by default in n8n 2.x)
- Document webhook URLs in the project config skill
