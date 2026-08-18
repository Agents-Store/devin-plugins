# Scenario: Scheduled Report Generator

Fetch analytics data daily → aggregate → send email report → notify on failure.

## Architecture

```
Schedule Trigger (daily 9 AM)
  → HTTP Request (fetch analytics API)
    → Code (aggregate data)
      → Send Email (formatted report)

Error Trigger
  → Slack (notify #ops-alerts)
```

## Step 1: Discover Nodes

```javascript
search_nodes({query: "schedule trigger"})
// → nodes-base.scheduleTrigger

search_nodes({query: "http request"})
// → nodes-base.httpRequest

search_nodes({query: "code"})
// → nodes-base.code

search_nodes({query: "email send"})
// → nodes-base.emailSend

search_nodes({query: "error trigger"})
// → nodes-base.errorTrigger
```

## Step 2: Create Workflow

```javascript
n8n_create_workflow({
  name: "Daily Analytics Report",
  nodes: [
    {
      id: "schedule-1",
      name: "Daily 9 AM",
      type: "n8n-nodes-base.scheduleTrigger",
      typeVersion: 1.2,
      position: [250, 300],
      parameters: {
        rule: {
          interval: [{
            field: "cronExpression",
            expression: "0 9 * * *"
          }]
        }
      }
    },
    {
      id: "http-1",
      name: "Fetch Analytics",
      type: "n8n-nodes-base.httpRequest",
      typeVersion: 4.2,
      position: [450, 300],
      parameters: {
        method: "GET",
        url: "https://api.example.com/analytics/daily",
        authentication: "genericCredentialType",
        genericAuthType: "httpHeaderAuth"
      }
    },
    {
      id: "code-1",
      name: "Aggregate Data",
      type: "n8n-nodes-base.code",
      typeVersion: 2,
      position: [650, 300],
      parameters: {
        mode: "runOnceForAllItems",
        jsCode: "const items = $input.all();\nconst data = items[0].json;\n\nconst totalViews = data.pages.reduce((sum, p) => sum + p.views, 0);\nconst totalUsers = data.uniqueUsers;\nconst topPages = data.pages\n  .sort((a, b) => b.views - a.views)\n  .slice(0, 5)\n  .map(p => `- ${p.name}: ${p.views} views`)\n  .join('\\n');\n\nreturn [{\n  json: {\n    subject: `Daily Report - ${$now.toFormat('yyyy-MM-dd')}`,\n    body: `Analytics Report\\n\\nTotal Views: ${totalViews}\\nUnique Users: ${totalUsers}\\n\\nTop Pages:\\n${topPages}`,\n    date: $now.toFormat('yyyy-MM-dd')\n  }\n}];"
      }
    },
    {
      id: "email-1",
      name: "Send Report",
      type: "n8n-nodes-base.emailSend",
      typeVersion: 2.1,
      position: [850, 300],
      parameters: {
        fromEmail: "reports@example.com",
        toEmail: "team@example.com",
        subject: "={{$json.subject}}",
        emailType: "text",
        message: "={{$json.body}}"
      }
    },
    {
      id: "error-1",
      name: "Error Trigger",
      type: "n8n-nodes-base.errorTrigger",
      typeVersion: 1,
      position: [250, 500],
      parameters: {}
    },
    {
      id: "slack-error",
      name: "Notify Failure",
      type: "n8n-nodes-base.slack",
      typeVersion: 2.2,
      position: [450, 500],
      parameters: {
        resource: "message",
        operation: "post",
        channel: { __rl: true, mode: "name", value: "#ops-alerts" },
        text: "Daily report workflow FAILED!\n\nError: {{$json.execution.error.message}}\nWorkflow: {{$json.workflow.name}}"
      }
    }
  ],
  connections: {
    "Daily 9 AM": {
      "main": [[{"node": "Fetch Analytics", "type": "main", "index": 0}]]
    },
    "Fetch Analytics": {
      "main": [[{"node": "Aggregate Data", "type": "main", "index": 0}]]
    },
    "Aggregate Data": {
      "main": [[{"node": "Send Report", "type": "main", "index": 0}]]
    },
    "Error Trigger": {
      "main": [[{"node": "Notify Failure", "type": "main", "index": 0}]]
    }
  },
  settings: {
    executionOrder: "v1",
    errorWorkflow: ""
  }
})
```

## Step 3: Configure Error Workflow

After creation, set the workflow as its own error handler:

```javascript
n8n_update_partial_workflow({
  id: "<workflow-id>",
  operations: [{
    type: "updateSettings",
    settings: { errorWorkflow: "<workflow-id>" }
  }]
})
```

## Step 4: Validate and Activate

```javascript
n8n_validate_workflow({id: "<workflow-id>"})
n8n_update_partial_workflow({
  id: "<workflow-id>",
  operations: [{type: "activateWorkflow"}]
})
```

## Key Learnings

- Schedule Trigger uses cron expressions for timing
- Code node in `runOnceForAllItems` mode processes all data at once
- Must return `[{json: {...}}]` format from Code node
- Error Trigger node catches workflow failures — place in same workflow
- Set `errorWorkflow` in settings to route errors to the Error Trigger
- HTTP Request v4 uses `authentication` and `genericAuthType` for auth config
