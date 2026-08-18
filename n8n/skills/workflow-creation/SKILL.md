---
name: workflow-creation
description: Workflow creation — node definitions, connections, triggers, workflow structure. This skill should be used when the user asks to create a new workflow, build an automation, set up triggers, or scaffold a workflow structure.
---

# Workflow Creation

This skill covers creating new n8n workflows — choosing triggers, adding nodes, wiring connections, and configuring the workflow structure.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_workflows` | List existing workflows |
| `get_workflow` | Get full workflow details |
| `create_workflow` | Create a new workflow |
| `activate_workflow` | Activate a workflow |

## Workflow Structure

Every n8n workflow consists of:
- **name** — descriptive workflow name
- **nodes** — array of node objects (trigger + processing)
- **connections** — object mapping node outputs to inputs

```json
{
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...}
}
```

## Creating a Workflow

### Step-by-step Process
```
1. list_workflows() -> Check for duplicates
2. create_workflow({ name, nodes, connections }) -> Create
3. get_workflow(id) -> Verify structure
4. activate_workflow(id) -> Enable (when ready)
```

### Minimal Workflow (Manual Trigger)
```
Tool: create_workflow
Input: {
  "name": "Test Workflow",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "manual-trigger",  // platform-specific: e.g. "n8n-nodes-base.manualTrigger"
      "position": [250, 300],
      "parameters": {}
    },
    {
      "name": "Set Data",
      "type": "set-data",  // platform-specific: e.g. "n8n-nodes-base.set"
      "position": [450, 300],
      "parameters": {
        "values": {
          "string": [{ "name": "message", "value": "Hello World" }]
        }
      }
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{ "node": "Set Data", "type": "main", "index": 0 }]]
    }
  }
}
```

## Trigger Nodes

Every workflow needs exactly ONE trigger node.

### Webhook Trigger
Receives HTTP requests from external systems.
```json
{
  "name": "Webhook",
  "type": "webhook",  // platform-specific: e.g. "n8n-nodes-base.webhook"
  "position": [250, 300],
  "parameters": {
    "path": "my-endpoint",
    "httpMethod": "POST",
    "responseMode": "onReceived"
  }
}
```

### Schedule Trigger
Runs on a cron/interval schedule.
```json
{
  "name": "Schedule",
  "type": "schedule-trigger",  // platform-specific: e.g. "n8n-nodes-base.scheduleTrigger"
  "position": [250, 300],
  "parameters": {
    "rule": {
      "interval": [{ "field": "hours", "hoursInterval": 1 }]
    }
  }
}
```

Schedule options:
- Seconds: `{ "field": "seconds", "secondsInterval": 30 }`
- Minutes: `{ "field": "minutes", "minutesInterval": 5 }`
- Hours: `{ "field": "hours", "hoursInterval": 1 }`
- Cron: `{ "field": "cronExpression", "expression": "0 9 * * 1-5" }`

### Manual Trigger
For testing and on-demand execution.
```json
{
  "name": "Manual Trigger",
  "type": "manual-trigger",  // platform-specific: e.g. "n8n-nodes-base.manualTrigger"
  "position": [250, 300],
  "parameters": {}
}
```

## Processing Nodes

### HTTP Request
```json
{
  "name": "API Call",
  "type": "http-request",  // platform-specific: e.g. "n8n-nodes-base.httpRequest"
  "position": [450, 300],
  "parameters": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth"
  }
}
```

### Set (Transform Data)
```json
{
  "name": "Transform",
  "type": "set-data",  // platform-specific: e.g. "n8n-nodes-base.set"
  "position": [450, 300],
  "parameters": {
    "values": {
      "string": [{ "name": "status", "value": "={{ $json.state }}" }],
      "number": [{ "name": "total", "value": "={{ $json.price * $json.qty }}" }]
    }
  }
}
```

### Code (Custom Logic)
```json
{
  "name": "Custom Code",
  "type": "code",  // platform-specific: e.g. "n8n-nodes-base.code"
  "position": [450, 300],
  "parameters": {
    "language": "javaScript",
    "jsCode": "const items = $input.all();\nreturn items.map(item => ({ json: { ...item.json, processed: true } }));"
  }
}
```

### If (Conditional)
```json
{
  "name": "Check Status",
  "type": "conditional",  // platform-specific: e.g. "n8n-nodes-base.if"
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "string": [{
        "value1": "={{ $json.status }}",
        "operation": "equals",
        "value2": "active"
      }]
    }
  }
}
```

## Connection Patterns

### Linear: A → B → C
```json
{
  "A": { "main": [[{ "node": "B", "type": "main", "index": 0 }]] },
  "B": { "main": [[{ "node": "C", "type": "main", "index": 0 }]] }
}
```

### Branch: A → If → B (true) / C (false)
```json
{
  "A": { "main": [[{ "node": "If", "type": "main", "index": 0 }]] },
  "If": {
    "main": [
      [{ "node": "B", "type": "main", "index": 0 }],
      [{ "node": "C", "type": "main", "index": 0 }]
    ]
  }
}
```

### Merge: A + B → Merge → C
```json
{
  "A": { "main": [[{ "node": "Merge", "type": "main", "index": 0 }]] },
  "B": { "main": [[{ "node": "Merge", "type": "main", "index": 1 }]] },
  "Merge": { "main": [[{ "node": "C", "type": "main", "index": 0 }]] }
}
```

## Node Positioning

Lay out nodes on a grid for readability:
- Start: `[250, 300]`
- Horizontal spacing: 200px
- Vertical spacing (branches): 150px
- Flow: left → right

## Additional Trigger Types

### Email Trigger (IMAP)
```json
{
  "name": "Email Received",
  "type": "email-trigger",  // platform-specific: e.g. "n8n-nodes-base.emailReadImap"
  "position": [250, 300],
  "parameters": {
    "mailbox": "INBOX",
    "options": { "unseen": true }
  }
}
```

### Form Trigger
```json
{
  "name": "Form Submitted",
  "type": "form-trigger",  // platform-specific: e.g. "n8n-nodes-base.formTrigger"
  "position": [250, 300],
  "parameters": {
    "formTitle": "Contact Form",
    "formFields": {
      "values": [
        { "fieldLabel": "Name", "fieldType": "text", "requiredField": true },
        { "fieldLabel": "Email", "fieldType": "email", "requiredField": true },
        { "fieldLabel": "Message", "fieldType": "textarea" }
      ]
    }
  }
}
```

### Chat Trigger
```json
{
  "name": "Chat Message",
  "type": "chat-trigger",  // platform-specific: e.g. "@n8n/n8n-nodes-langchain.chatTrigger"
  "position": [250, 300],
  "parameters": {}
}
```

## Additional Processing Nodes

### Filter
```json
{
  "name": "Filter Active",
  "type": "filter",  // platform-specific: e.g. "n8n-nodes-base.filter"
  "position": [450, 300],
  "parameters": {
    "conditions": {
      "string": [{
        "value1": "={{ $json.status }}",
        "operation": "equals",
        "value2": "active"
      }]
    }
  }
}
```

### Switch
```json
{
  "name": "Route by Type",
  "type": "switch",  // platform-specific: e.g. "n8n-nodes-base.switch"
  "position": [450, 300],
  "parameters": {
    "mode": "rules",
    "rules": {
      "values": [
        { "conditions": { "string": [{ "value1": "={{ $json.type }}", "operation": "equals", "value2": "order" }] } },
        { "conditions": { "string": [{ "value1": "={{ $json.type }}", "operation": "equals", "value2": "refund" }] } }
      ]
    },
    "fallbackOutput": "extra"
  }
}
```

### Merge
```json
{
  "name": "Combine Data",
  "type": "merge",  // platform-specific: e.g. "n8n-nodes-base.merge"
  "position": [650, 300],
  "parameters": {
    "mode": "combine",
    "mergeByFields": {
      "values": [{ "field1": "id", "field2": "userId" }]
    },
    "joinMode": "inner"
  }
}
```

### Split In Batches
```json
{
  "name": "Process in Batches",
  "type": "split-in-batches",  // platform-specific: e.g. "n8n-nodes-base.splitInBatches"
  "position": [450, 300],
  "parameters": {
    "batchSize": 10
  }
}
```

### Wait
```json
{
  "name": "Wait 5 seconds",
  "type": "wait",  // platform-specific: e.g. "n8n-nodes-base.wait"
  "position": [450, 300],
  "parameters": {
    "amount": 5,
    "unit": "seconds"
  }
}
```

### Respond to Webhook
```json
{
  "name": "Send Response",
  "type": "respond-to-webhook",  // platform-specific: e.g. "n8n-nodes-base.respondToWebhook"
  "position": [650, 300],
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ { success: true, id: $json.id } }}"
  }
}
```

## Advanced Connection Patterns

### Loop: Split In Batches → Process → [loop back]
```json
{
  "Split In Batches": {
    "main": [
      [{ "node": "Process Item", "type": "main", "index": 0 }],
      [{ "node": "Done", "type": "main", "index": 0 }]
    ]
  },
  "Process Item": {
    "main": [[{ "node": "Split In Batches", "type": "main", "index": 0 }]]
  }
}
```

### Parallel Execution: A → [B, C] → Merge → D
```json
{
  "A": {
    "main": [
      [
        { "node": "B", "type": "main", "index": 0 },
        { "node": "C", "type": "main", "index": 0 }
      ]
    ]
  },
  "B": { "main": [[{ "node": "Merge", "type": "main", "index": 0 }]] },
  "C": { "main": [[{ "node": "Merge", "type": "main", "index": 1 }]] },
  "Merge": { "main": [[{ "node": "D", "type": "main", "index": 0 }]] }
}
```

### Error Handling: Node → Error Trigger → Notification
```json
// In the error workflow:
{
  "nodes": [
    { "name": "Error Trigger", "type": "error-trigger", "position": [250, 300] },
    { "name": "Send Alert", "type": "http-request", "position": [450, 300], "parameters": {
      "url": "https://hooks.slack.com/services/xxx",
      "method": "POST",
      "body": "={{ JSON.stringify({ text: `Workflow failed: ${$json.workflow.name} - ${$json.execution.error.message}` }) }}"
    }}
  ]
}
```

## Debugging Failed Workflows

### Common Failure Scenarios
- **Invalid credentials** → check credential type and configuration; re-authenticate if expired
- **Wrong URL in HTTP Request** → verify URL is reachable and correct; check for trailing slashes
- **Missing input data** → previous node returned empty; add If node to check for data before processing
- **Expression error** → `$json.field` doesn't exist; use `$json?.field` or check data structure first
- **Rate limited by external API** → add Wait node between requests; use Split In Batches with smaller batch size
- **Timeout** → increase timeout in HTTP Request settings; consider async approach

### Debugging Steps
1. Get execution details → find the exact node that failed
2. Check the node's input data → was the expected data passed in?
3. Check the node's error message → what specifically went wrong?
4. Check previous node's output → did it produce the expected data format?
5. Fix the issue → update workflow
6. Re-test with the same input data if possible

### Debugging Code Nodes
- **Syntax error** → check language setting (JavaScript vs Python); verify correct syntax for chosen language
- **Undefined variable** → Code nodes have their own scope; data from previous nodes is in `$input.all()` or `items`
- **Wrong output format** → Code nodes must return array of objects with `json` property: `return [{json: {key: value}}]`
- **Module not found** → only built-in modules available; cannot import external packages in standard Code node

### Systematic Debugging for Complex Workflows
For workflows with 10+ nodes:
1. **Bisect** — disable half the nodes, test; narrow down which half contains the failure
2. **Isolate** — run the failing node alone with mock input data
3. **Inspect data shape** — add a temporary Set node before the failing node to log the exact data structure
4. **Check execution order** — for parallel branches, verify merge node receives data from all branches

## Best Practices

1. **One trigger per workflow** — don't mix triggers
2. **Name nodes descriptively** — "Fetch Orders" not "HTTP Request 1"
3. **Test before activating** — use `execute_workflow` first
4. **Use expressions** — `={{ $json.field }}` for dynamic values
5. **Handle errors** — add error paths for critical workflows
6. **Start simple** — build minimal workflow, test, then add complexity
7. **Use Split In Batches** — for API rate limiting and large datasets
8. **Add Wait nodes** — between API calls to respect rate limits
9. **Use Merge after parallel branches** — always merge parallel paths before continuing
10. **Set up error workflows** — configure Error Trigger workflow for critical automations
