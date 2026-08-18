# Scenario: Webhook Automation

Build a webhook-triggered workflow that receives data, validates it, processes it, and sends notifications.

## Goal

Create a workflow that:
1. Receives form submission via webhook
2. Validates required fields
3. Stores data in an external system
4. Sends email notification
5. Returns confirmation response

## Build Steps

### 1. Create the Workflow

```
create_workflow({
  name: "Form Submission Handler",
  nodes: [
    {
      name: "Webhook",
      type: "webhook",
      position: [250, 300],
      parameters: { path: "form-submit", httpMethod: "POST" }
    },
    {
      name: "Validate Fields",
      type: "conditional",
      position: [450, 300],
      parameters: {
        conditions: {
          string: [
            { value1: "={{ $json.name }}", operation: "isNotEmpty" },
            { value1: "={{ $json.email }}", operation: "isNotEmpty" }
          ]
        }
      }
    },
    {
      name: "Store Data",
      type: "http-request",
      position: [650, 250],
      parameters: {
        url: "https://api.example.com/submissions",
        method: "POST",
        bodyParameters: {
          parameters: [
            { name: "name", value: "={{ $json.name }}" },
            { name: "email", value: "={{ $json.email }}" },
            { name: "message", value: "={{ $json.message }}" }
          ]
        }
      }
    },
    {
      name: "Send Notification",
      type: "http-request",
      position: [850, 250],
      parameters: {
        url: "https://api.example.com/notify",
        method: "POST",
        bodyParameters: {
          parameters: [
            { name: "to", value: "admin@example.com" },
            { name: "subject", value: "New form submission from {{ $json.name }}" }
          ]
        }
      }
    },
    {
      name: "Success Response",
      type: "respond-to-webhook",
      position: [1050, 250],
      parameters: { respondWith: "json", responseBody: '{"status": "success", "message": "Submission received"}' }
    },
    {
      name: "Error Response",
      type: "respond-to-webhook",
      position: [650, 400],
      parameters: { respondWith: "json", responseBody: '{"status": "error", "message": "Name and email are required"}', responseCode: 400 }
    }
  ],
  connections: {
    "Webhook": { main: [[{ node: "Validate Fields" }]] },
    "Validate Fields": { main: [[{ node: "Store Data" }], [{ node: "Error Response" }]] },
    "Store Data": { main: [[{ node: "Send Notification" }]] },
    "Send Notification": { main: [[{ node: "Success Response" }]] }
  }
})
```

### 2. Activate
```
activate_workflow(workflow_id)
```

### 3. Test
```
execute_workflow(workflow_id, {
  data: {
    name: "John Doe",
    email: "john@example.com",
    message: "I'd like to learn more about your services"
  }
})
```

### 4. Verify
```
get_execution(execution_id)
→ Check: Validate passed, data stored, notification sent, success response returned
```

## Result

A production-ready webhook handler with:
- Input validation
- External API integration
- Email notifications
- Proper error responses
