# Scenario: Scheduled Data Pipeline

Build a scheduled workflow that fetches data from an API, transforms it, and stores the results.

## Goal

Create a workflow that:
1. Runs every hour on a schedule
2. Fetches recent orders from an API
3. Filters orders above a threshold
4. Transforms data format
5. Sends processed data to a destination

## Build Steps

### 1. Create the Pipeline

```
create_workflow({
  name: "Hourly Order Sync",
  nodes: [
    {
      name: "Every Hour",
      type: "schedule-trigger",
      position: [250, 300],
      parameters: {
        rule: { interval: [{ field: "hours", hoursInterval: 1 }] }
      }
    },
    {
      name: "Fetch Orders",
      type: "http-request",
      position: [450, 300],
      parameters: {
        url: "https://api.store.com/orders?since=1h",
        method: "GET",
        authentication: "genericCredentialType",
        genericAuthType: "httpHeaderAuth"
      }
    },
    {
      name: "Filter High Value",
      type: "conditional",
      position: [650, 300],
      parameters: {
        conditions: {
          number: [{ value1: "={{ $json.total }}", operation: "larger", value2: 100 }]
        }
      }
    },
    {
      name: "Transform",
      type: "set-data",
      position: [850, 250],
      parameters: {
        values: {
          string: [
            { name: "orderId", value: "={{ $json.id }}" },
            { name: "customer", value: "={{ $json.customer.name }}" },
            { name: "status", value: "high-value" }
          ],
          number: [
            { name: "amount", value: "={{ $json.total }}" }
          ]
        }
      }
    },
    {
      name: "Send to Warehouse",
      type: "http-request",
      position: [1050, 250],
      parameters: {
        url: "https://warehouse.example.com/api/orders",
        method: "POST",
        body: "={{ JSON.stringify($json) }}"
      }
    },
    {
      name: "Log Skipped",
      type: "set-data",
      position: [850, 400],
      parameters: {
        values: {
          string: [{ name: "action", value: "skipped-low-value" }]
        }
      }
    }
  ],
  connections: {
    "Every Hour": { main: [[{ node: "Fetch Orders" }]] },
    "Fetch Orders": { main: [[{ node: "Filter High Value" }]] },
    "Filter High Value": { main: [[{ node: "Transform" }], [{ node: "Log Skipped" }]] },
    "Transform": { main: [[{ node: "Send to Warehouse" }]] }
  }
})
```

### 2. Set Up Credentials
```
create_credential({
  name: "Store API",
  type: "httpHeaderAuth",
  data: { name: "Authorization", value: "Bearer sk-store-api-key" }
})
```

### 3. Test Manually
```
execute_workflow(workflow_id)
get_execution(execution_id)
→ Verify: orders fetched, filtered correctly, transformed, sent
```

### 4. Activate
```
activate_workflow(workflow_id)
```

### 5. Monitor After First Hour
```
list_executions(workflow_id, limit=5)
→ Check first automated run succeeded
```

## Result

An automated data pipeline that:
- Runs hourly without intervention
- Filters data based on business rules
- Transforms and routes data to the right destination
- Can be monitored via execution history
