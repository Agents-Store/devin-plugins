---
name: execution-monitoring
description: Workflow execution, monitoring, and debugging. This skill should be used when the user asks to run a workflow, check execution status, view execution history, or debug workflow errors.
---

# Execution & Monitoring

This skill covers running and monitoring n8n workflow executions — triggering runs, checking status, debugging failures, and understanding execution data.

## Available Tools

| Tool | Description |
|------|-------------|
| `execute_workflow` | Trigger a workflow execution |
| `list_executions` | List recent executions |
| `get_execution` | Get detailed execution results |
| `activate_workflow` | Activate (enable trigger-based execution) |
| `deactivate_workflow` | Deactivate (disable triggers) |

## Executing Workflows

### Manual Execution
```
Tool: execute_workflow
Input: {
  "workflow_id": "wf_abc123"
}
```

### Execution with Input Data
```
Tool: execute_workflow
Input: {
  "workflow_id": "wf_abc123",
  "data": {
    "name": "Test User",
    "email": "test@example.com"
  }
}
```

## Listing Executions

### All Recent Executions
```
Tool: list_executions
Input: {
  "limit": 20
}
```

### Filter by Workflow
```
Tool: list_executions
Input: {
  "workflow_id": "wf_abc123",
  "limit": 10
}
```

### Filter by Status
```
Tool: list_executions
Input: {
  "status": "error",
  "limit": 10
}
```

**Execution statuses:** `success`, `error`, `waiting`, `running`

## Execution Details

```
Tool: get_execution
Input: {
  "execution_id": "exec_xyz789"
}

Returns:
- Execution status (success/error)
- Start time, end time, duration
- Node-by-node output data
- Error details (if failed)
```

## Common Workflows

### Execute and Verify
```
1. execute_workflow(workflow_id) -> Get execution_id
2. get_execution(execution_id) -> Check status and outputs
3. If error: identify failing node and error message
```

### Debug Failed Execution
```
1. list_executions(workflow_id, status="error") -> Find failed runs
2. get_execution(execution_id) -> See full error details
3. Identify:
   - Which node failed
   - What error message
   - What input data the node received
4. get_workflow(workflow_id) -> Get workflow to fix
5. Fix the issue (update node parameters, add validation, etc.)
6. update_workflow(workflow_id, fixed_data) -> Save fix
7. execute_workflow(workflow_id) -> Re-test
```

### Monitor Workflow Health
```
1. list_executions(workflow_id, limit=50) -> Get recent history
2. Count success vs error executions
3. Identify patterns (time of failure, specific nodes)
4. Report findings and suggest improvements
```

## Activation Lifecycle

| State | Trigger-based execution | Manual execution |
|-------|------------------------|------------------|
| Active | Triggers fire automatically | Can also run manually |
| Inactive | Triggers do NOT fire | Can still run manually |

```
// Enable trigger-based execution
activate_workflow(workflow_id)

// Disable triggers (manual execution still works)
deactivate_workflow(workflow_id)
```

## Error Types

| Error | Common Cause | Fix |
|-------|-------------|-----|
| Authentication | Invalid/expired credentials | Update credential |
| Connection refused | Wrong URL or service down | Check URL and service status |
| Timeout | Slow external API | Increase timeout or add retry |
| Invalid input | Missing/wrong data format | Add validation node before |
| Rate limit | Too many API calls | Add Wait node or batch processing |

## Retry Failed Executions

### Manual Retry
```
1. list_executions(workflow_id, status="error") → Find failed execution
2. get_execution(execution_id) → Understand the failure
3. If issue is transient (API timeout, rate limit):
   execute_workflow(workflow_id) → Re-run the workflow
4. If issue is in the data:
   execute_workflow(workflow_id, input_data) → Re-run with corrected data
```

### Execution with Input Data
```
Tool: execute_workflow
Input: {
  "workflow_id": "wf_abc123",
  "data": {
    "key": "value",
    "orderId": 42
  }
}
```

## Best Practices

1. **Test before activating** — use `execute_workflow` with test data
2. **Check execution details** — don't assume success, verify node outputs
3. **Monitor error rate** — regularly check `list_executions(status="error")`
4. **Use meaningful test data** — test with realistic inputs
5. **Debug from execution data** — node outputs show exactly what went wrong
6. **Deactivate flapping workflows** — disable workflows that keep failing until fixed
7. **Retry transient failures** — API timeouts and rate limits often resolve on retry
8. **Set up error notifications** — configure Error Trigger workflow for critical processes
