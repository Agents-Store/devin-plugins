# n8n Workflow Examples

Multi-step workflows combining multiple n8n tools.

## Example 1: Build a Webhook Handler

```
Step 1: Create workflow with webhook trigger
Tool: create_workflow
Input: {
  "name": "Order Webhook Handler",
  "nodes": [
    {
      "name": "Webhook",
      "type": "webhook",
      "position": [250, 300],
      "parameters": { "path": "orders", "httpMethod": "POST" }
    },
    {
      "name": "Validate",
      "type": "conditional",
      "position": [450, 300],
      "parameters": {
        "conditions": { "string": [{ "value1": "={{ $json.orderId }}", "operation": "isNotEmpty" }] }
      }
    },
    {
      "name": "Process Order",
      "type": "http-request",
      "position": [650, 250],
      "parameters": { "url": "https://api.example.com/process", "method": "POST", "body": "={{ JSON.stringify($json) }}" }
    },
    {
      "name": "Return Error",
      "type": "respond-to-webhook",
      "position": [650, 400],
      "parameters": { "respondWith": "json", "responseBody": "{\"error\": \"Invalid order\"}", "responseCode": 400 }
    },
    {
      "name": "Return Success",
      "type": "respond-to-webhook",
      "position": [850, 250],
      "parameters": { "respondWith": "json", "responseBody": "{\"status\": \"processed\"}" }
    }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Validate" }]] },
    "Validate": { "main": [[{ "node": "Process Order" }], [{ "node": "Return Error" }]] },
    "Process Order": { "main": [[{ "node": "Return Success" }]] }
  }
}

Step 2: Activate the workflow
Tool: activate_workflow
Input: { "workflow_id": "<created_id>" }

Step 3: Test with sample data
Tool: execute_workflow
Input: {
  "workflow_id": "<created_id>",
  "data": { "orderId": "ORD-001", "amount": 99.99, "customer": "John" }
}

Step 4: Verify execution
Tool: get_execution
Input: { "execution_id": "<exec_id>" }
→ Check all node outputs are correct
```

## Example 2: Add a Node to Existing Workflow

```
Step 1: Get current workflow
Tool: get_workflow
Input: { "workflow_id": "wf_existing" }
→ Current: Webhook → Process → Respond

Step 2: Deactivate
Tool: deactivate_workflow
Input: { "workflow_id": "wf_existing" }

Step 3: Update - insert logging node
Tool: update_workflow
Input: {
  "workflow_id": "wf_existing",
  "nodes": [
    ...existing_nodes,
    {
      "name": "Log to DB",
      "type": "http-request",
      "position": [550, 450],
      "parameters": { "url": "https://api.example.com/logs", "method": "POST" }
    }
  ],
  "connections": {
    ...existing_connections,
    "Process": {
      "main": [[{ "node": "Respond" }], [{ "node": "Log to DB" }]]
    }
  }
}

Step 4: Test
Tool: execute_workflow
Input: { "workflow_id": "wf_existing" }

Step 5: Re-activate
Tool: activate_workflow
Input: { "workflow_id": "wf_existing" }
```

## Example 3: Schedule and Monitor

```
Step 1: Create scheduled workflow
Tool: create_workflow
Input: {
  "name": "Hourly Health Check",
  "nodes": [
    {
      "name": "Schedule",
      "type": "schedule-trigger",
      "position": [250, 300],
      "parameters": { "rule": { "interval": [{ "field": "hours", "hoursInterval": 1 }] } }
    },
    {
      "name": "Check API",
      "type": "http-request",
      "position": [450, 300],
      "parameters": { "url": "https://api.example.com/health", "method": "GET" }
    }
  ],
  "connections": {
    "Schedule": { "main": [[{ "node": "Check API" }]] }
  }
}

Step 2: Activate
Tool: activate_workflow
Input: { "workflow_id": "<id>" }

Step 3: Monitor executions after some time
Tool: list_executions
Input: { "workflow_id": "<id>", "limit": 10 }
→ Check success rate

Step 4: Investigate any failures
Tool: get_execution
Input: { "execution_id": "<failed_exec_id>" }
→ See error details
```
