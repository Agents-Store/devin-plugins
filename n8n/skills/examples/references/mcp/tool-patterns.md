# n8n MCP Tool Patterns

Exact parameter formats for all n8n MCP tools.

## Workflows

### list_workflows
```json
Input: {}
Output: { "workflows": [{ "id": "wf_xxx", "name": "My Workflow", "active": true, "tags": [...] }] }
```

### get_workflow
```json
Input: { "workflow_id": "wf_xxx" }
Output: { "id": "wf_xxx", "name": "...", "nodes": [...], "connections": {...}, "active": true }
```

### create_workflow
```json
Input: {
  "name": "New Workflow",
  "nodes": [
    { "name": "Webhook", "type": "webhook", "position": [250, 300], "parameters": { "path": "hook", "httpMethod": "POST" } },
    { "name": "Process", "type": "set-data", "position": [450, 300], "parameters": { "values": { "string": [{ "name": "status", "value": "received" }] } } }
  ],
  "connections": {
    "Webhook": { "main": [[{ "node": "Process", "type": "main", "index": 0 }]] }
  }
}
Output: { "id": "wf_xxx", "name": "New Workflow" }
```

### update_workflow
```json
Input: {
  "workflow_id": "wf_xxx",
  "name": "Updated Name",
  "nodes": [...],
  "connections": {...}
}
Output: { "id": "wf_xxx", ... }
```

### delete_workflow
```json
Input: { "workflow_id": "wf_xxx" }
Output: { "success": true }
```

### activate_workflow
```json
Input: { "workflow_id": "wf_xxx" }
Output: { "id": "wf_xxx", "active": true }
```

### deactivate_workflow
```json
Input: { "workflow_id": "wf_xxx" }
Output: { "id": "wf_xxx", "active": false }
```

## Execution

### execute_workflow
```json
Input: {
  "workflow_id": "wf_xxx",
  "data": { "key": "value" }
}
Output: { "execution_id": "exec_xxx", "status": "success" }
```

### list_executions
```json
Input: {
  "workflow_id": "wf_xxx",
  "status": "error",
  "limit": 20
}
Output: { "executions": [{ "id": "exec_xxx", "status": "error", "startedAt": "...", "stoppedAt": "..." }] }
```

### get_execution
```json
Input: { "execution_id": "exec_xxx" }
Output: { "id": "exec_xxx", "status": "success", "data": { "resultData": { "runData": { ... } } }, "startedAt": "...", "stoppedAt": "..." }
```

## Credentials

### list_credentials
```json
Input: {}
Output: { "credentials": [{ "id": "cred_xxx", "name": "My API", "type": "httpHeaderAuth" }] }
```

### create_credential
```json
Input: {
  "name": "Slack Bot",
  "type": "slackApi",
  "data": { "accessToken": "xoxb-..." }
}
Output: { "id": "cred_xxx", "name": "Slack Bot" }
```

### delete_credential
```json
Input: { "credential_id": "cred_xxx" }
Output: { "success": true }
```

## Tags

### list_tags
```json
Input: {}
Output: { "tags": [{ "id": "tag_xxx", "name": "production" }] }
```

### create_tag
```json
Input: { "name": "production" }
Output: { "id": "tag_xxx", "name": "production" }
```

### update_tag
```json
Input: { "tag_id": "tag_xxx", "name": "prod" }
Output: { "id": "tag_xxx", "name": "prod" }
```

### delete_tag
```json
Input: { "tag_id": "tag_xxx" }
Output: { "success": true }
```
