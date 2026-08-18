# Scenario: Webhook to Slack Notification

Receive form submission via webhook → validate data → post to Slack → respond to caller.

## Architecture

```
Webhook (POST /form-submit)
  → Set (map fields)
    → Slack (post to #notifications)
      → Respond to Webhook (200 OK)
```

## Step 1: Discover Nodes

```javascript
search_nodes({query: "webhook"})
// → nodes-base.webhook

search_nodes({query: "slack"})
// → nodes-base.slack

search_nodes({query: "set"})
// → nodes-base.set

search_nodes({query: "respond webhook"})
// → nodes-base.respondToWebhook
```

## Step 2: Get Node Details

```javascript
get_node({nodeType: "nodes-base.webhook", detail: "standard"})
get_node({nodeType: "nodes-base.slack", detail: "standard"})
```

## Step 3: Create Workflow

```javascript
n8n_create_workflow({
  name: "Form to Slack Notification",
  nodes: [
    {
      id: "webhook-1",
      name: "Webhook",
      type: "n8n-nodes-base.webhook",
      typeVersion: 2,
      position: [250, 300],
      parameters: {
        path: "form-submit",
        httpMethod: "POST",
        responseMode: "responseNode"
      }
    },
    {
      id: "set-1",
      name: "Map Fields",
      type: "n8n-nodes-base.set",
      typeVersion: 3.4,
      position: [450, 300],
      parameters: {
        mode: "manual",
        duplicateItem: false,
        assignments: {
          assignments: [
            {
              id: "name",
              name: "name",
              value: "={{$json.body.name}}",
              type: "string"
            },
            {
              id: "email",
              name: "email",
              value: "={{$json.body.email}}",
              type: "string"
            },
            {
              id: "message",
              name: "message",
              value: "={{$json.body.message}}",
              type: "string"
            }
          ]
        }
      }
    },
    {
      id: "slack-1",
      name: "Slack",
      type: "n8n-nodes-base.slack",
      typeVersion: 2.2,
      position: [650, 300],
      parameters: {
        resource: "message",
        operation: "post",
        channel: { __rl: true, mode: "name", value: "#notifications" },
        text: "New form submission!\n\nName: {{$json.name}}\nEmail: {{$json.email}}\nMessage: {{$json.message}}"
      }
    },
    {
      id: "respond-1",
      name: "Respond",
      type: "n8n-nodes-base.respondToWebhook",
      typeVersion: 1.1,
      position: [850, 300],
      parameters: {
        respondWith: "json",
        responseBody: "={\"status\": \"received\", \"message\": \"Thank you!\"}"
      }
    }
  ],
  connections: {
    "Webhook": {
      "main": [[{"node": "Map Fields", "type": "main", "index": 0}]]
    },
    "Map Fields": {
      "main": [[{"node": "Slack", "type": "main", "index": 0}]]
    },
    "Slack": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
})
```

## Step 4: Validate

```javascript
n8n_validate_workflow({id: "<workflow-id>"})
```

## Step 5: Test

```javascript
n8n_test_workflow({
  workflowId: "<workflow-id>",
  data: {
    name: "John Doe",
    email: "john@example.com",
    message: "Hello from the form!"
  }
})
```

## Step 6: Activate

```javascript
n8n_update_partial_workflow({
  id: "<workflow-id>",
  operations: [{type: "activateWorkflow"}]
})
```

## Key Learnings

- Webhook data is under `$json.body.*` — not `$json.*` directly
- Use `responseMode: "responseNode"` to control response with Respond to Webhook node
- Slack channel uses `__rl` (resource locator) format with `mode: "name"`
- Set node v3.4 uses `assignments` structure for field mapping
